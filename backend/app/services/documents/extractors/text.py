from pathlib import Path

from app.services.documents.extractors.base import (
    DocumentExtractionError,
    DocumentExtractor,
    ExtractedDocument,
    ExtractedSection,
)


class TextExtractor(DocumentExtractor):
    def extract(self, path: Path) -> ExtractedDocument:
        try:
            text = path.read_text(encoding="utf-8-sig").strip()
        except (OSError, UnicodeDecodeError) as exc:
            raise DocumentExtractionError(
                "The text file must contain UTF-8 text"
            ) from exc
        if not text:
            raise DocumentExtractionError("The text file is empty")
        return ExtractedDocument((ExtractedSection(text),))
