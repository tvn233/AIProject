"""Local multilingual E5 embeddings for asymmetric retrieval."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer


DEFAULT_MODEL = "intfloat/multilingual-e5-small"
VECTOR_DIMENSION = 384


class MultilingualE5Embedder:
    """SentenceTransformer adapter with E5's required query/passage prefixes.

    The model supports multilingual retrieval including Vietnamese. Its weights
    are downloaded on first use; inference runs locally on CPU by default.
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
