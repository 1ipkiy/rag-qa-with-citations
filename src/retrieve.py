"""Retrieve top-k chunks for a query."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .embeddings import DEFAULT_MODEL, embed_query
from .store import FaissStore


def retrieve(
    query: str,
    index_dir: Path,
    top_k: int = 4,
    model_name: str = DEFAULT_MODEL,
) -> list[dict[str, Any]]:
    store = FaissStore(index_dir)
    store.load()
    # Prefer model name recorded at ingest time
    cfg = store.config
    model = cfg.get("embedding_model", model_name)
    qvec = embed_query(query, model_name=model)
    return store.search(qvec, top_k=top_k)
