"""Cấu trúc tài liệu, đoạn trích và kho dữ liệu RAG."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    """Một tài liệu Markdown trong corpus."""

    doc_id: str
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentChunk:
    """Một đoạn văn bản được tách từ tài liệu."""

    chunk_id: str
    doc_id: str
    title: str
    section: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentStore:
    """Lưu tài liệu và các đoạn trích trong bộ nhớ."""

    documents: dict[str, Document] = field(default_factory=dict)
    chunks: dict[str, DocumentChunk] = field(default_factory=dict)

    def add_document(self, document: Document) -> None:
        if document.doc_id in self.documents:
            raise ValueError(f"Trùng doc_id: {document.doc_id}")
        self.documents[document.doc_id] = document

    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        for chunk in chunks:
            if chunk.doc_id not in self.documents:
                raise ValueError(
                    f"Đoạn {chunk.chunk_id} tham chiếu tài liệu "
                    f"không tồn tại: {chunk.doc_id}"
                )
            if chunk.chunk_id in self.chunks:
                raise ValueError(f"Trùng chunk_id: {chunk.chunk_id}")
            self.chunks[chunk.chunk_id] = chunk

    def get_document(self, doc_id: str) -> Document | None:
        return self.documents.get(doc_id)

    def get_chunk(self, chunk_id: str) -> DocumentChunk | None:
        return self.chunks.get(chunk_id)

    def all_chunks(self) -> list[DocumentChunk]:
        return list(self.chunks.values())
