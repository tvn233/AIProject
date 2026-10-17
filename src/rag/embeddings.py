"""Mã hóa câu hỏi và tài liệu thành vector bằng E5 đa ngôn ngữ."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer


DEFAULT_MODEL = "intfloat/multilingual-e5-small"
VECTOR_DIMENSION = 384


class MultilingualE5Embedder:
    """Thêm tiền tố query:/passage: theo đầu vào của E5.

    Mô hình được tải nếu chưa có trong bộ nhớ đệm, mặc định chạy trên CPU.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL, device: str = "cpu") -> None:
        self.model = SentenceTransformer(model_name, device=device)
        self.model.max_seq_length = 512

    def embed_documents(self, texts: Sequence[str]) -> np.ndarray:
        return self._encode(texts, prefix="passage: ")

    def embed_queries(self, texts: Sequence[str]) -> np.ndarray:
        return self._encode(texts, prefix="query: ")

    def _encode(self, texts: Sequence[str], *, prefix: str) -> np.ndarray:
        if not texts:
            return np.empty((0, VECTOR_DIMENSION), dtype=np.float32)
        prepared = [prefix + text for text in texts]
        return self.model.encode(
            prepared,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
