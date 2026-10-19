"""Local sentence-transformer embeddings (CPU)."""

from __future__ import annotations

from functools import lru_cache
from typing import Sequence

import numpy as np

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model(model_name: str = DEFAULT_MODEL):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def embed_texts(
    texts: Sequence[str],
    model_name: str = DEFAULT_MODEL,
    batch_size: int = 32,
    normalize: bool = True,
) -> np.ndarray:
    """Return float32 array of shape (n, dim). Optionally L2-normalize for cosine via IP."""
    model = get_model(model_name)
    vectors = model.encode(
        list(texts),
        batch_size=batch_size,
        show_progress_bar=len(texts) > 16,
        convert_to_numpy=True,
        normalize_embeddings=normalize,
    )
    return np.asarray(vectors, dtype=np.float32)


def embed_query(query: str, model_name: str = DEFAULT_MODEL) -> np.ndarray:
    return embed_texts([query], model_name=model_name, normalize=True)[0]
