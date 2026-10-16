"""Kết nối đọc corpus, truy xuất tài liệu và tạo câu trả lời."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .chunking import MarkdownChunker
from .generator import answer_with_groq
from .models import DocumentStore
from .retriever import HybridRetriever, SearchMode, SearchResult


@dataclass
class RAGAnswer:
    """Câu trả lời cùng các nguồn đã truy xuất."""

    question: str
    answer: str
    sources: list[SearchResult]

    @property
    def source_doc_ids(self) -> list[str]:
        """Các doc_id nguồn, giữ thứ tự truy xuất và bỏ ID trùng."""
        return list(dict.fromkeys(
            result.chunk.doc_id for result in self.sources
        ))


@dataclass
class RAGPipeline:
    """Nạp corpus một lần rồi dùng để truy xuất và trả lời."""

    store: DocumentStore
    retriever: HybridRetriever
    embedder: Any

    @classmethod
    def from_corpus(
        cls,
        corpus_dir: str | Path,
        *,
        embedder: Any | None = None,
        dense_weight: float = 0.5,
    ) -> RAGPipeline:
        corpus_path = Path(corpus_dir)
        if not corpus_path.is_dir():
            raise FileNotFoundError(
                f"Không tìm thấy thư mục tài liệu: {corpus_path}"
            )

        chunker = MarkdownChunker(str(corpus_path))
        store = DocumentStore()

        for file_path in sorted(corpus_path.glob("*.md")):
            document = chunker.load_document(str(file_path))
            store.add_document(document)
            store.add_chunks(chunker.chunk_document(document))

        chunks = store.all_chunks()
        if not chunks:
            raise ValueError(f"Không có đoạn tài liệu nào trong {corpus_path}")

        if embedder is None:
            from .embeddings import MultilingualE5Embedder
            embedder = MultilingualE5Embedder()

        retriever = HybridRetriever(
            chunks,
            embedder.embed_documents,
            embed_query=embedder.embed_queries,
            dense_weight=dense_weight,
        )

        return cls(
            store=store,
            retriever=retriever,
            embedder=embedder,
        )

    def retrieve(
        self,
        question: str,
        *,
        mode: SearchMode = "hybrid",
        top_k: int = 3,
    ) -> list[SearchResult]:
        return self.retriever.search(
            question,
            mode=mode,
            top_k=top_k,
        )

    def ask(
        self,
        question: str,
        *,
        mode: SearchMode = "hybrid",
        top_k: int = 3,
        model: str | None = None,
        client: Any | None = None,
    ) -> RAGAnswer:
        sources = self.retrieve(question, mode=mode, top_k=top_k)
        answer = answer_with_groq(
            question,
            sources,
            model=model,
            client=client,
        )

        return RAGAnswer(
            question=question,
            answer=answer,
            sources=sources,
        )
