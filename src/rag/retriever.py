"""Tìm đoạn tài liệu bằng vector hoặc kết hợp vector với BM25."""

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
    """Đoạn tài liệu tìm được cùng điểm của từng cách truy xuất."""

    chunk: TextChunk
    score: float
    dense_score: float
    bm25_score: float


def tokenize_vietnamese(text: str) -> list[str]:
    """Tách theo khoảng trắng và dấu câu, giữ dấu tiếng Việt."""
    return re.findall(r"[^\W_]+", text.casefold(), flags=re.UNICODE)


class HybridRetriever:
    """Xếp hạng theo độ tương đồng cosine hoặc kết hợp hai thứ hạng bằng RRF.

    Truyền riêng embed_query khi mô hình mã hóa câu hỏi khác với tài liệu,
    như E5 dùng hai tiền tố query: và passage:.
    dense_weight nằm trong [0, 1]; phần trọng số còn lại dành cho BM25.
    rrf_k làm giảm chênh lệch điểm giữa các vị trí khi gộp thứ hạng.
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
            raise ValueError("Danh sách đoạn tài liệu không được rỗng.")
        if not 0.0 <= dense_weight <= 1.0:
            raise ValueError("Trọng số dense_weight phải nằm trong [0, 1].")
        if rrf_k <= 0:
            raise ValueError("rrf_k phải lớn hơn 0.")

        self.chunks = list(chunks)
        self.embed_documents = embed_documents
        self.embed_query = embed_query or embed_documents
        self.dense_weight = dense_weight
        self.rrf_k = rrf_k

        self._tokens = [tokenize_vietnamese(chunk.content) for chunk in self.chunks]
        if any(not tokens for tokens in self._tokens):
            raise ValueError("Mỗi đoạn tài liệu phải có từ để tìm kiếm.")
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
                f"Hàm mã hóa phải trả về ma trận hai chiều có {expected_rows} hàng."
            )
        if not np.isfinite(matrix).all():
            raise ValueError("Vector chứa giá trị NaN hoặc vô hạn.")
        return matrix

    @staticmethod
    def _normalize_rows(matrix: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        if np.any(norms == 0):
            raise ValueError("Vector mã hóa không được có độ dài bằng 0.")
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
        """Lấy các đoạn phù hợp nhất theo chế độ dense hoặc hybrid."""
        if not query.strip():
            raise ValueError("Câu hỏi không được để trống.")
        if mode not in ("dense", "hybrid"):
            raise ValueError("Chế độ tìm kiếm phải là 'dense' hoặc 'hybrid'.")
        if top_k <= 0:
            raise ValueError("Số kết quả top_k phải lớn hơn 0.")

        query_vector = self._as_matrix(self.embed_query([query]), expected_rows=1)
        if query_vector.shape[1] != self._vectors.shape[1]:
            raise ValueError("Vector câu hỏi và tài liệu phải có cùng số chiều.")
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
