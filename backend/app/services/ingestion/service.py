from dataclasses import dataclass
from math import ceil
from pathlib import Path
from uuid import UUID, uuid4

import anyio
from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.core.config import Settings
from app.core.exceptions import InvalidUploadError, NotFoundError, UploadTooLargeError
from app.db.models import Dataset, DatasetColumn
from app.domain.enums import DatasetFileType, DatasetStatus
from app.repositories.audit_logs import AuditLogRepository
from app.repositories.clients import ClientRepository
from app.repositories.datasets import DatasetRepository
from app.services.ingestion.parsers import build_parser_registry
from app.services.ingestion.parsers.base import DatasetParseError

CHUNK_SIZE = 1024 * 1024
FILE_TYPE_BY_EXTENSION = {
    ".csv": DatasetFileType.CSV,
    ".json": DatasetFileType.JSON,
    ".xlsx": DatasetFileType.XLSX,
}
ALLOWED_CONTENT_TYPES = {
    DatasetFileType.CSV: {
        "text/csv",
        "application/csv",
        "text/plain",
        "application/vnd.ms-excel",
        "application/octet-stream",
    },
    DatasetFileType.JSON: {
        "application/json",
        "text/json",
        "text/plain",
        "application/octet-stream",
    },
    DatasetFileType.XLSX: {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/octet-stream",
    },
}


@dataclass(frozen=True)
class DatasetPage:
    items: list[Dataset]
    page: int
    page_size: int
    total: int
    total_pages: int


class IngestionService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.clients = ClientRepository(session)
        self.datasets = DatasetRepository(session)
        self.audit_logs = AuditLogRepository(session)
        self.parsers = build_parser_registry()

    async def upload(
        self,
        organization_id: UUID,
        client_id: UUID,
        uploaded_by: UUID,
        upload: UploadFile,
    ) -> Dataset:
        if self.clients.get(organization_id, client_id) is None:
            raise NotFoundError("Client not found")

        try:
            original_filename, file_type, extension = self._validate_upload_metadata(
                upload
            )
            if (
                upload.size is not None
                and upload.size > self.settings.max_upload_size_bytes
            ):
                raise UploadTooLargeError(
                    "Upload exceeds the configured maximum size of "
                    f"{self.settings.max_upload_size_mb} MB"
                )
        except (InvalidUploadError, UploadTooLargeError):
            await upload.close()
            raise
        storage_directory = self.settings.upload_dir.expanduser().resolve()
        storage_directory.mkdir(parents=True, exist_ok=True)
        stored_filename = f"{uuid4().hex}{extension}"
        destination = storage_directory / stored_filename

        try:
            file_size = await self._stream_to_storage(upload, destination)
            await self._validate_file_content(destination, file_type)
            parser = self.parsers[file_type]
            parsed = await run_in_threadpool(
                parser.parse,
                destination,
                max_rows=self.settings.dataset_max_rows,
                sample_size=self.settings.dataset_sample_size,
            )
        except (InvalidUploadError, UploadTooLargeError):
            destination.unlink(missing_ok=True)
            raise
        except DatasetParseError as exc:
            destination.unlink(missing_ok=True)
            raise InvalidUploadError(str(exc)) from exc
        finally:
            await upload.close()

        dataset = Dataset(
            organization_id=organization_id,
            client_id=client_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_type=file_type,
            file_size=file_size,
            row_count=parsed.row_count,
            column_count=parsed.column_count,
            status=DatasetStatus.NEEDS_REVIEW,
            uploaded_by=uploaded_by,
            columns=[
                DatasetColumn(
                    source_name=column.source_name,
                    detected_type=column.detected_type,
                    sample_values=column.sample_values,
                    null_count=column.null_count,
                    unique_count=column.unique_count,
                )
                for column in parsed.columns
            ],
        )
        self.datasets.add(dataset)
        try:
            self.session.flush()
            self.audit_logs.add(
                organization_id=organization_id,
                user_id=uploaded_by,
                client_id=client_id,
                action="dataset.uploaded",
                resource_type="dataset",
                resource_id=dataset.id,
                metadata={
                    "file_type": file_type.value,
                    "file_size": file_size,
                    "row_count": parsed.row_count,
                    "column_count": parsed.column_count,
                },
            )
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            destination.unlink(missing_ok=True)
            raise

        self.session.refresh(dataset)
        return dataset

    def list(
        self,
        organization_id: UUID,
        client_id: UUID,
        *,
        page: int,
        page_size: int,
    ) -> DatasetPage:
        if self.clients.get(organization_id, client_id) is None:
            raise NotFoundError("Client not found")
        items, total = self.datasets.list(
            organization_id,
            client_id,
            offset=(page - 1) * page_size,
            limit=page_size,
        )
        return DatasetPage(items, page, page_size, total, ceil(total / page_size))

    def get(
        self,
        organization_id: UUID,
        client_id: UUID,
        dataset_id: UUID,
    ) -> Dataset:
        dataset = self.datasets.get(organization_id, client_id, dataset_id)
        if dataset is None:
            raise NotFoundError("Dataset not found")
        return dataset

    def _validate_upload_metadata(
        self,
        upload: UploadFile,
    ) -> tuple[str, DatasetFileType, str]:
        unsafe_filename = upload.filename or ""
        original_filename = unsafe_filename.replace("\\", "/").rsplit("/", 1)[-1]
        if not original_filename or len(original_filename) > 255:
            raise InvalidUploadError("A valid filename is required")

        extension = Path(original_filename).suffix.lower()
        file_type = FILE_TYPE_BY_EXTENSION.get(extension)
        if file_type is None:
            raise InvalidUploadError("Only CSV, JSON, and XLSX files are supported")

        content_type = (upload.content_type or "application/octet-stream").lower()
        if content_type not in ALLOWED_CONTENT_TYPES[file_type]:
            raise InvalidUploadError(
                f"Content type {content_type!r} does not match {extension}"
            )
        return original_filename, file_type, extension

    async def _stream_to_storage(self, upload: UploadFile, destination: Path) -> int:
        total_size = 0
        await upload.seek(0)
        async with await anyio.open_file(destination, "wb") as stored_file:
            while chunk := await upload.read(CHUNK_SIZE):
                total_size += len(chunk)
                if total_size > self.settings.max_upload_size_bytes:
                    raise UploadTooLargeError(
                        "Upload exceeds the configured maximum size of "
                        f"{self.settings.max_upload_size_mb} MB"
                    )
                await stored_file.write(chunk)
        if total_size == 0:
            raise InvalidUploadError("Uploaded file is empty")
        return total_size

    async def _validate_file_content(
        self,
        destination: Path,
        file_type: DatasetFileType,
    ) -> None:
        async with await anyio.open_file(destination, "rb") as stored_file:
            header = await stored_file.read(4096)

        if file_type == DatasetFileType.XLSX and not header.startswith(b"PK"):
            raise InvalidUploadError("The uploaded file is not a valid XLSX container")
        if file_type == DatasetFileType.JSON:
            stripped = header.lstrip()
            if not stripped.startswith((b"{", b"[")):
                raise InvalidUploadError("The uploaded file does not contain JSON data")
        if file_type == DatasetFileType.CSV:
            if b"\x00" in header:
                raise InvalidUploadError("The uploaded CSV appears to be a binary file")
            try:
                header.decode("utf-8-sig")
            except UnicodeDecodeError as exc:
                raise InvalidUploadError("CSV files must use UTF-8 encoding") from exc
