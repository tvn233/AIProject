"""Đọc tài liệu Markdown, giữ thông tin mô tả và chia theo đề mục."""

from __future__ import annotations

import os
import re
from typing import Any

import yaml

from .models import Document, DocumentChunk

# Giữ tương thích với retriever hiện tại đang import TextChunk.
TextChunk = DocumentChunk


class MarkdownChunker:
    """Chia tài liệu theo các tiêu đề cấp 2 Markdown (##)."""

    def __init__(self, corpus_dir: str):
        self.corpus_dir = corpus_dir

    @staticmethod
    def parse_yaml_frontmatter(
        file_content: str,
    ) -> tuple[dict[str, Any], str]:
        """Tách phần thông tin YAML ở đầu tài liệu Markdown."""
        match = re.search(
            r"^---\s*\n(.*?)\n---\s*\n",
            file_content,
            re.DOTALL,
        )

        if not match:
            return {}, file_content.strip()

        metadata = yaml.safe_load(match.group(1)) or {}
        if not isinstance(metadata, dict):
            raise ValueError("Thông tin YAML đầu tài liệu phải có dạng khóa: giá trị.")

        body = file_content[match.end():].strip()
        return metadata, body

    def load_document(self, file_path: str) -> Document:
        """Đọc một file Markdown thành Document."""
        with open(file_path, "r", encoding="utf-8") as file:
            raw_content = file.read()

        metadata, body = self.parse_yaml_frontmatter(raw_content)

        if not metadata.get("doc_id") or not metadata.get("title"):
            raise ValueError(f"Thiếu doc_id/title trong YAML: {file_path}")

        return Document(
            doc_id=str(metadata.get("doc_id", "UNKNOWN")),
            title=str(metadata.get("title", "")),
            content=body,
            metadata=metadata,
        )

    @staticmethod
    def chunk_document(document: Document, max_words: int = 230, overlap_words: int = 30) -> list[DocumentChunk]:
        """Split by ## heading, then cap oversized sections with word overlap.

        Word limits are approximate (E5 tokenization differs from whitespace).
        """
        if max_words <= 0 or not 0 <= overlap_words < max_words:
            raise ValueError("Cần 0 <= overlap_words < max_words và max_words > 0")
        body = re.sub(r"(?m)^#\s+[^\n]*\n?", "", document.content, count=1).strip()
        sections = re.split(r"(?m)(?=^##\s+)", body)
        chunks: list[DocumentChunk] = []
        for section_content in sections:
            section_content = section_content.strip()
            if not section_content:
                continue
            first_line = section_content.split("\n", 1)[0]
            section = first_line.removeprefix("##").strip() if first_line.startswith("##") else "Tổng quan"
            words = section_content.split()
            step = max_words - overlap_words
            for offset in range(0, len(words), step):
                part = words[offset:offset + max_words]
                if not part:
                    break
                chunks.append(DocumentChunk(
                    chunk_id=f"{document.doc_id}_CHUNK_{len(chunks) + 1:03d}",
                    doc_id=document.doc_id, title=document.title,
                    section=section, content=" ".join(part), metadata=dict(document.metadata),
                ))
                if offset + max_words >= len(words):
                    break
        return chunks

    def process_file(self, file_path: str) -> list[DocumentChunk]:
        """Đọc và chia đoạn cho một tài liệu."""
        document = self.load_document(file_path)
        return self.chunk_document(document)

    def process_all(self) -> list[DocumentChunk]:
        """Đọc và chia đoạn cho tất cả tài liệu Markdown trong thư mục."""
        if not os.path.isdir(self.corpus_dir):
            raise FileNotFoundError(
                f"Không tìm thấy thư mục tài liệu: {self.corpus_dir}"
            )

        all_chunks: list[DocumentChunk] = []

        for filename in sorted(os.listdir(self.corpus_dir)):
            if filename.lower().endswith(".md"):
                file_path = os.path.join(self.corpus_dir, filename)
                all_chunks.extend(self.process_file(file_path))

        return all_chunks


if __name__ == "__main__":
    chunker = MarkdownChunker("data/corpus")
    chunks = chunker.process_all()

    print(f"Đã tạo {len(chunks)} đoạn tài liệu.")
    for chunk in chunks[:3]:
        print(
            chunk.chunk_id,
            "|", chunk.doc_id,
            "|", chunk.section,
            "| phiên bản", chunk.metadata.get("version", "?"),
        )
        print(chunk.content[:250], "\n")
