"""FAISS vector store with JSON metadata sidecar.

Why FAISS: pure local library, no daemon, tiny footprint for a small corpus,
and IndexFlatIP + L2-normalized vectors = cosine similarity. Chroma is nicer
for apps that want a persistent client API; FAISS keeps the portfolio deps light.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from .chunking import Chunk


class FaissStore:
    def __init__(self, index_dir: Path):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.index_dir / "faiss.index"
        self.meta_path = self.index_dir / "chunks.json"
        self.config_path = self.index_dir / "config.json"
        self._index = None
        self._chunks: list[dict[str, Any]] = []

    def build(
        self,
        chunks: list[Chunk],
        vectors: np.ndarray,
        embedding_model: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> None:
        import faiss

        if len(chunks) == 0:
            raise ValueError("No chunks to index")
        if vectors.shape[0] != len(chunks):
            raise ValueError("vectors and chunks length mismatch")

        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(np.ascontiguousarray(vectors.astype(np.float32)))

        faiss.write_index(index, str(self.index_path))
        self._chunks = [c.to_dict() for c in chunks]
        self.meta_path.write_text(json.dumps(self._chunks, indent=2), encoding="utf-8")
        config = {
            "embedding_model": embedding_model,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "num_chunks": len(chunks),
            "dim": dim,
            "metric": "inner_product_cosine",
            "store": "faiss.IndexFlatIP",
        }
        self.config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        self._index = index

    def load(self) -> None:
        import faiss

        if not self.index_path.exists() or not self.meta_path.exists():
            raise FileNotFoundError(
                f"Index not found under {self.index_dir}. Run: python ingest.py"
            )
        self._index = faiss.read_index(str(self.index_path))
        self._chunks = json.loads(self.meta_path.read_text(encoding="utf-8"))

    @property
    def config(self) -> dict[str, Any]:
        if self.config_path.exists():
            return json.loads(self.config_path.read_text(encoding="utf-8"))
        return {}

    def search(self, query_vector: np.ndarray, top_k: int = 4) -> list[dict[str, Any]]:
        if self._index is None:
            self.load()
        assert self._index is not None

        q = np.ascontiguousarray(query_vector.reshape(1, -1).astype(np.float32))
        k = min(top_k, len(self._chunks))
        scores, indices = self._index.search(q, k)

        results: list[dict[str, Any]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            item = dict(self._chunks[int(idx)])
            item["score"] = float(score)
            results.append(item)
        return results
