import re

from app.services.documents.chunking.base import TextChunker


class RecursiveTextChunker(TextChunker):
    def __init__(self, chunk_size: int, overlap: int) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be between zero and chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.separators = ("\n\n", "\n", ". ", " ", "")

    def chunk(self, text: str) -> list[str]:
        normalized = re.sub(r"[ \t]+", " ", text).strip()
        if not normalized:
            return []
        pieces = self._split(normalized, 0)
        chunks: list[str] = []
        current = ""
        for piece in pieces:
            piece = piece.strip()
            if not piece:
                continue
            candidate = f"{current} {piece}".strip() if current else piece
            if len(candidate) <= self.chunk_size:
                current = candidate
                continue
            if current:
                chunks.append(current)
                carry = current[-self.overlap :].lstrip() if self.overlap else ""
                allowed_carry = max(self.chunk_size - len(piece) - 1, 0)
                carry = carry[-allowed_carry:] if allowed_carry else ""
                current = f"{carry} {piece}".strip()
            else:
                chunks.append(piece[: self.chunk_size].strip())
                current = piece[self.chunk_size - self.overlap :].strip()
        if current:
            chunks.append(current)
        return [chunk for chunk in chunks if chunk.strip()]

    def _split(self, text: str, separator_index: int) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]
        separator = self.separators[separator_index]
        if separator == "":
            step = self.chunk_size
            return [text[index : index + step] for index in range(0, len(text), step)]
        if separator not in text:
            return self._split(text, separator_index + 1)
        parts = text.split(separator)
        pieces: list[str] = []
        for part in parts:
            if not part:
                continue
            pieces.extend(self._split(part, separator_index + 1))
        return pieces
