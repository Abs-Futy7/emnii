from app.services.documents.chunking import RecursiveTextChunker


def test_recursive_chunker_generates_bounded_nonempty_overlapping_chunks() -> None:
    text = "\n\n".join(
        f"Section {index}. " + ("customer support policy details " * 4)
        for index in range(8)
    )
    chunker = RecursiveTextChunker(chunk_size=120, overlap=20)

    chunks = chunker.chunk(text)

    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)
    assert all(len(chunk) <= 120 for chunk in chunks)
    assert any(
        chunks[index][-10:].strip() in chunks[index + 1]
        for index in range(len(chunks) - 1)
    )


def test_recursive_chunker_rejects_invalid_configuration() -> None:
    try:
        RecursiveTextChunker(chunk_size=100, overlap=100)
    except ValueError as exc:
        assert "overlap" in str(exc)
    else:
        raise AssertionError("Expected invalid overlap to be rejected")
