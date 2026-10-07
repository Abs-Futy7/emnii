from dataclasses import dataclass
from datetime import UTC, datetime
from math import ceil
from pathlib import Path
from uuid import UUID

import anyio
from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.core.config import Settings
from app.core.exceptions import (
    ExternalServiceError,
    InvalidUploadError,
    NotFoundError,
    UploadTooLargeError,
)
from app.db.models import Document, DocumentChunk
from app.domain.enums import (
    DocumentFileType,
    DocumentIndexingStatus,
    DocumentStatus,
)
from app.repositories.audit_logs import AuditLogRepository
from app.repositories.clients import ClientRepository
from app.repositories.documents import DocumentRepository
from app.services.documents.chunking import RecursiveTextChunker
from app.services.documents.extractors import build_extractor_registry
from app.services.documents.extractors.base import DocumentExtractionError
from app.services.documents.storage import DocumentStorage
from app.services.rag.vector_store import VectorStore

FILE_TYPE_BY_EXTENSION = {
    ".pdf": DocumentFileType.PDF,
    ".docx": DocumentFileType.DOCX,
    ".txt": DocumentFileType.TXT,
    ".md": DocumentFileType.MARKDOWN,
    ".markdown": DocumentFileType.MARKDOWN,
}
ALLOWED_MIME_TYPES = {
    DocumentFileType.PDF: {"application/pdf", "application/octet-stream"},
    DocumentFileType.DOCX: {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/octet-stream",
    },
    DocumentFileType.TXT: {"text/plain", "application/octet-stream"},
    DocumentFileType.MARKDOWN: {
        "text/markdown",
        "text/plain",
        "text/x-markdown",
        "application/octet-stream",
    },
}


@dataclass(frozen=True)
class DocumentPage:
    items: list[Document]
    page: int
    page_size: int
    total: int
    total_pages: int


class DocumentService:
    def __init__(
        self,
        session: Session,
        settings: Settings,
        vector_store: VectorStore | None = None,
    ) -> None:
        self.session = session
        self.settings = settings
        self.clients = ClientRepository(session)
        self.documents = DocumentRepository(session)
        self.audit_logs = AuditLogRepository(session)
        self.storage = DocumentStorage(settings)
        self.extractors = build_extractor_registry()
        self.chunker = RecursiveTextChunker(
            settings.document_chunk_size,
            settings.document_chunk_overlap,
        )
        self.vector_store = vector_store

    async def upload(
        self,
        organization_id: UUID,
        client_id: UUID,
        uploaded_by: UUID,
        upload: UploadFile,
    ) -> Document:
        if self.clients.get(organization_id, client_id) is None:
            await upload.close()
            raise NotFoundError("Client not found")
        try:
            original_name, file_type, extension, mime_type = self._validate_metadata(
                upload
            )
            stored = await self.storage.save(upload, extension)
            await self._validate_content(stored.path, file_type)
        except (InvalidUploadError, UploadTooLargeError):
            await upload.close()
            raise
        finally:
            await upload.close()

        document = Document(
            organization_id=organization_id,
            client_id=client_id,
            uploaded_by=uploaded_by,
            original_filename=original_name,
            stored_filename=stored.filename,
            file_type=file_type,
            mime_type=mime_type,
            file_size=stored.size,
            status=DocumentStatus.PROCESSING,
        )
        self.documents.add(document)
        try:
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            self.storage.delete(stored.filename)
            raise

        try:
            extracted = await run_in_threadpool(
                self.extractors[file_type].extract, stored.path
            )
            chunks: list[DocumentChunk] = []
            chunk_index = 0
            for section in extracted.sections:
                for content in self.chunker.chunk(section.text):
                    if not content.strip():
                        continue
                    chunks.append(
                        DocumentChunk(
                            organization_id=organization_id,
                            client_id=client_id,
                            document_id=document.id,
                            chunk_index=chunk_index,
                            content=content,
                            page_number=section.page_number,
                            metadata_={
                                "document_id": str(document.id),
                                "source_filename": original_name,
                                "client_id": str(client_id),
                                "chunk_index": chunk_index,
                                **(
                                    {"page_number": section.page_number}
                                    if section.page_number is not None
                                    else {}
                                ),
                            },
                        )
                    )
                    chunk_index += 1
            if not chunks:
                raise DocumentExtractionError(
                    "The document contains no text suitable for chunking"
                )

            document.title = extracted.title
            document.extracted_text_length = extracted.text_length
            document.page_count = extracted.page_count
            document.status = DocumentStatus.PROCESSED
            document.chunks = chunks
            self.audit_logs.add(
                organization_id=organization_id,
                user_id=uploaded_by,
                client_id=client_id,
                action="document.processed",
                resource_type="document",
                resource_id=document.id,
                metadata={
                    "file_type": file_type.value,
                    "file_size": stored.size,
                    "chunk_count": len(chunks),
                },
            )
            self.session.commit()
        except DocumentExtractionError as exc:
            self.session.rollback()
            document.status = DocumentStatus.FAILED
            self.audit_logs.add(
                organization_id=organization_id,
                user_id=uploaded_by,
                client_id=client_id,
                action="document.processing_failed",
                resource_type="document",
                resource_id=document.id,
            )
            self.session.commit()
            raise InvalidUploadError(str(exc)) from exc
        except SQLAlchemyError:
            self.session.rollback()
            document.status = DocumentStatus.FAILED
            self.session.commit()
            raise

        self.session.expire_all()
        return self.get(organization_id, client_id, document.id)

    def list(
        self,
        organization_id: UUID,
        client_id: UUID,
        *,
        page: int,
        page_size: int,
    ) -> DocumentPage:
        if self.clients.get(organization_id, client_id) is None:
            raise NotFoundError("Client not found")
        items, total = self.documents.list(
            organization_id,
            client_id,
            offset=(page - 1) * page_size,
            limit=page_size,
        )
        return DocumentPage(items, page, page_size, total, ceil(total / page_size))

    def get(
        self, organization_id: UUID, client_id: UUID, document_id: UUID
    ) -> Document:
        document = self.documents.get(organization_id, client_id, document_id)
        if document is None:
            raise NotFoundError("Document not found")
        return document

    def delete(
        self,
        organization_id: UUID,
        client_id: UUID,
        document_id: UUID,
        actor_id: UUID,
    ) -> Document:
        document = self.get(organization_id, client_id, document_id)
        if (
            document.indexing_status != DocumentIndexingStatus.NOT_INDEXED
            and self.vector_store is not None
        ):
            try:
                self.vector_store.delete_document(
                    organization_id, client_id, document_id
                )
            except Exception as exc:
                raise ExternalServiceError(
                    "Document vectors could not be removed"
                ) from exc
        document.deleted_at = datetime.now(UTC)
        self.audit_logs.add(
            organization_id=organization_id,
            user_id=actor_id,
            client_id=client_id,
            action="document.deleted",
            resource_type="document",
            resource_id=document_id,
        )
        self.session.commit()
        return document

    def _validate_metadata(
        self, upload: UploadFile
    ) -> tuple[str, DocumentFileType, str, str]:
        unsafe_name = upload.filename or ""
        original_name = unsafe_name.replace("\\", "/").rsplit("/", 1)[-1]
        if not original_name or len(original_name) > 255:
            raise InvalidUploadError("A valid filename is required")
        extension = Path(original_name).suffix.lower()
        file_type = FILE_TYPE_BY_EXTENSION.get(extension)
        if file_type is None:
            raise InvalidUploadError("Only PDF, DOCX, TXT, and Markdown are supported")
        mime_type = (upload.content_type or "application/octet-stream").lower()
        if mime_type not in ALLOWED_MIME_TYPES[file_type]:
            raise InvalidUploadError(
                f"Content type {mime_type!r} does not match {extension}"
            )
        return original_name, file_type, extension, mime_type

    async def _validate_content(self, path: Path, file_type: DocumentFileType) -> None:
        async with await anyio.open_file(path, "rb") as stored:
            header = await stored.read(4096)
        if file_type == DocumentFileType.PDF and not header.startswith(b"%PDF-"):
            self.storage.delete(path.name)
            raise InvalidUploadError("The uploaded file is not a valid PDF")
        if file_type == DocumentFileType.DOCX and not header.startswith(b"PK"):
            self.storage.delete(path.name)
            raise InvalidUploadError("The uploaded file is not a valid DOCX container")
        if file_type in {DocumentFileType.TXT, DocumentFileType.MARKDOWN}:
            if b"\x00" in header:
                self.storage.delete(path.name)
                raise InvalidUploadError("Text documents cannot contain binary data")
            try:
                header.decode("utf-8-sig")
            except UnicodeDecodeError as exc:
                self.storage.delete(path.name)
                raise InvalidUploadError(
                    "Text documents must use UTF-8 encoding"
                ) from exc
