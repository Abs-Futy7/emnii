from app.domain.enums import DocumentFileType
from app.services.documents.extractors.base import DocumentExtractor
from app.services.documents.extractors.docx import DOCXExtractor
from app.services.documents.extractors.markdown import MarkdownExtractor
from app.services.documents.extractors.pdf import PDFExtractor
from app.services.documents.extractors.text import TextExtractor


def build_extractor_registry() -> dict[DocumentFileType, DocumentExtractor]:
    return {
        DocumentFileType.PDF: PDFExtractor(),
        DocumentFileType.DOCX: DOCXExtractor(),
        DocumentFileType.TXT: TextExtractor(),
        DocumentFileType.MARKDOWN: MarkdownExtractor(),
    }


__all__ = ["DocumentExtractor", "build_extractor_registry"]
