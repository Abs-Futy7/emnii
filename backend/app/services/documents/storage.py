from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import anyio
from fastapi import UploadFile

from app.core.config import Settings
from app.core.exceptions import InvalidUploadError, UploadTooLargeError

STREAM_CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class StoredDocument:
    filename: str
    path: Path
    size: int


class DocumentStorage:
    def __init__(self, settings: Settings) -> None:
        self.directory = settings.document_upload_dir.expanduser().resolve()
        self.max_size = settings.max_document_upload_size_bytes
        self.max_size_mb = settings.max_document_upload_size_mb

    async def save(self, upload: UploadFile, extension: str) -> StoredDocument:
        if upload.size is not None and upload.size > self.max_size:
            raise UploadTooLargeError(
                f"Document exceeds the configured maximum size of {self.max_size_mb} MB"
            )
        self.directory.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid4().hex}{extension}"
        destination = self.directory / filename
        total = 0
        await upload.seek(0)
        try:
            async with await anyio.open_file(destination, "wb") as stored:
                while chunk := await upload.read(STREAM_CHUNK_SIZE):
                    total += len(chunk)
                    if total > self.max_size:
                        raise UploadTooLargeError(
                            "Document exceeds the configured maximum size of "
                            f"{self.max_size_mb} MB"
                        )
                    await stored.write(chunk)
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        if total == 0:
            destination.unlink(missing_ok=True)
            raise InvalidUploadError("Uploaded document is empty")
        return StoredDocument(filename, destination, total)

    def delete(self, filename: str) -> None:
        safe_name = Path(filename).name
        if safe_name != filename:
            raise ValueError("Unsafe stored filename")
        (self.directory / safe_name).unlink(missing_ok=True)
