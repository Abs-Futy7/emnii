from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


class DocumentExtractionError(ValueError):
    pass


@dataclass(frozen=True)
class ExtractedSection:
    text: str
    page_number: int | None = None


@dataclass(frozen=True)
class ExtractedDocument:
    sections: tuple[ExtractedSection, ...]
    title: str | None = None
    page_count: int | None = None

    @property
    def text_length(self) -> int:
        return sum(len(section.text) for section in self.sections)


class DocumentExtractor(ABC):
    @abstractmethod
    def extract(self, path: Path) -> ExtractedDocument:
        raise NotImplementedError
