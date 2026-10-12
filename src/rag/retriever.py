"""Dense and hybrid retrieval over MarkdownChunker TextChunk objects.

The embedding provider is injected so the project can use the embedding model
already selected by the group without tying retrieval to one vendor.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Literal, Sequence

import numpy as np
from rank_bm25 import BM25Okapi

from .chunking import TextChunk


EmbeddingFunction = Callable[
    [list[str]], np.ndarray | Sequence[Sequence[float]]
]
SearchMode = Literal["dense", "hybrid"]


@dataclass(frozen=True)
class SearchResult:
    """A retrieved chunk and its component scores."""

    chunk: TextChunk
    score: float
    dense_score: float
    bm25_score: float


def tokenize_vietnamese(text: str) -> list[str]:
    """Simple Unicode word tokenization that preserves Vietnamese accents."""
    return re.findall(r"[^\W_]+", text.casefold(), flags=re.UNICODE)


class HybridRetriever:
    """Retrieve chunks with dense cosine similarity or weighted RRF fusion.

    Args:
        chunks: Output of ``MarkdownChunker.process_all()``.
        embed_documents: Function that returns one vector per corpus chunk.
        embed_query: Optional query-specific embedding function. This is needed
            by asymmetric models such as multilingual E5, which use different
            prefixes for passages and queries.
        dense_weight: Dense ranking weight in hybrid mode, between 0 and 1.
        rrf_k: Reciprocal-rank-fusion constant; 60 is a common stable default.
    """

    def __init__(
        self,
        chunks: Sequence[TextChunk],
        embed_documents: EmbeddingFunction,
        *,
        embed_query: EmbeddingFunction | None = None,
        dense_weight: float = 0.5,
        rrf_k: int = 60,
    ) -> None:
        if not chunks:
            raise ValueError("chunks must not be empty")
        if not 0.0 <= dense_weight <= 1.0:
            raise ValueError("dense_weight must be between 0 and 1")
        if rrf_k <= 0:
            raise ValueError("rrf_k must be positive")

        self.chunks = list(chunks)
        self.embed_documents = embed_documents
        self.embed_query = embed_query or embed_documents
        self.dense_weight = dense_weight
        self.rrf_k = rrf_k

        self._tokens = [tokenize_vietnamese(chunk.content) for chunk in self.chunks]
        if any(not tokens for tokens in self._tokens):
            raise ValueError("every chunk must contain searchable text")
        self._bm25 = BM25Okapi(self._tokens)
        self._vectors = self._as_matrix(
            self.embed_documents([chunk.content for chunk in self.chunks]),
            expected_rows=len(self.chunks),
        )
        self._vectors = self._normalize_rows(self._vectors)

    @staticmethod
    def _as_matrix(vectors: Sequence[Sequence[float]], expected_rows: int) -> np.ndarray:
        matrix = np.asarray(vectors, dtype=np.float32)
        if matrix.ndim != 2 or matrix.shape[0] != expected_rows or matrix.shape[1] == 0:
            raise ValueError(
                f"embedding function must return a 2D matrix with {expected_rows} rows"
            )
        if not np.isfinite(matrix).all():
            raise ValueError("embedding vectors contain NaN or infinite values")
        return matrix

    @staticmethod
    def _normalize_rows(matrix: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        if np.any(norms == 0):
            raise ValueError("embedding vectors must not be zero vectors")
        return matrix / norms

    @staticmethod
    def _rank(scores: np.ndarray) -> np.ndarray:
        return np.argsort(-scores, kind="stable")

    def search(
        self,
        query: str,
        *,
        mode: SearchMode = "hybrid",
        top_k: int = 5,
    ) -> list[SearchResult]:
        """Return the top matching chunks in dense or hybrid mode."""
        if not query.strip():
            raise ValueError("query must not be empty")
        if mode not in ("dense", "hybrid"):
            raise ValueError("mode must be 'dense' or 'hybrid'")
        if top_k <= 0:
            raise ValueError("top_k must be positive")

        query_vector = self._as_matrix(self.embed_query([query]), expected_rows=1)
        if query_vector.shape[1] != self._vectors.shape[1]:
            raise ValueError("query and corpus embedding dimensions do not match")
        query_vector = self._normalize_rows(query_vector)[0]
        dense_scores = self._vectors @ query_vector
        bm25_scores = np.asarray(
            self._bm25.get_scores(tokenize_vietnamese(query)), dtype=np.float32
        )

        dense_order = self._rank(dense_scores)
        bm25_order = self._rank(bm25_scores)

        if mode == "dense":
            order = dense_order[: min(top_k, len(self.chunks))]
            fused_scores = dense_scores
        else:
            dense_ranks = np.empty(len(self.chunks), dtype=np.int32)
            bm25_ranks = np.empty(len(self.chunks), dtype=np.int32)
            dense_ranks[dense_order] = np.arange(1, len(self.chunks) + 1)
            bm25_ranks[bm25_order] = np.arange(1, len(self.chunks) + 1)
            lexical_weight = 1.0 - self.dense_weight
            fused_scores = (
                self.dense_weight / (self.rrf_k + dense_ranks)
                + lexical_weight / (self.rrf_k + bm25_ranks)
            )
            order = self._rank(fused_scores)[: min(top_k, len(self.chunks))]

        return [
            SearchResult(
                chunk=self.chunks[int(i)],
                score=float(fused_scores[i]),
                dense_score=float(dense_scores[i]),
                bm25_score=float(bm25_scores[i]),
            )
            for i in order
        ]
