import re
from pathlib import Path

from app.services.documents.extractors.base import ExtractedDocument
from app.services.documents.extractors.text import TextExtractor

HEADING_PATTERN = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


class MarkdownExtractor(TextExtractor):
    def extract(self, path: Path) -> ExtractedDocument:
        extracted = super().extract(path)
        match = HEADING_PATTERN.search(extracted.sections[0].text)
        title = match.group(1).strip() if match else None
        return ExtractedDocument(extracted.sections, title=title)
