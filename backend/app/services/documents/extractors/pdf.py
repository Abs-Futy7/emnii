from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.services.documents.extractors.base import (
    DocumentExtractionError,
    DocumentExtractor,
    ExtractedDocument,
    ExtractedSection,
)


class PDFExtractor(DocumentExtractor):
    def extract(self, path: Path) -> ExtractedDocument:
        try:
            reader = PdfReader(path)
            sections = tuple(
                ExtractedSection((page.extract_text() or "").strip(), index)
                for index, page in enumerate(reader.pages, start=1)
            )
        except (OSError, PdfReadError, ValueError) as exc:
            raise DocumentExtractionError("The PDF could not be parsed") from exc

        nonempty = tuple(section for section in sections if section.text)
        if not nonempty:
            raise DocumentExtractionError(
                "The PDF contains no extractable text; scanned PDFs require OCR"
            )
        raw_title = reader.metadata.title if reader.metadata else None
        title = raw_title.strip() if isinstance(raw_title, str) else None
        return ExtractedDocument(nonempty, title or None, len(reader.pages))
