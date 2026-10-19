#!/usr/bin/env python3
"""Index markdown files under data/ into a local FAISS store."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.chunking import chunk_corpus
from src.embeddings import DEFAULT_MODEL, embed_texts
from src.store import FaissStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest data/*.md into FAISS index")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--index-dir", type=Path, default=ROOT / "index")
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--chunk-overlap", type=int, default=80)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    args = parser.parse_args()

    if not args.data_dir.exists():
        raise SystemExit(f"Data directory not found: {args.data_dir}")

    print(f"Chunking markdown from {args.data_dir} ...")
    chunks = chunk_corpus(
        args.data_dir,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    print(f"  {len(chunks)} chunks from {len(list(args.data_dir.glob('*.md')))} files")

    print(f"Embedding with {args.model} (CPU) ...")
    vectors = embed_texts([c.text for c in chunks], model_name=args.model)
    print(f"  vectors shape: {vectors.shape}")

    store = FaissStore(args.index_dir)
    store.build(
        chunks=chunks,
        vectors=vectors,
        embedding_model=args.model,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    print(f"Wrote index → {args.index_dir}/faiss.index")
    print(f"Wrote metadata → {args.index_dir}/chunks.json")
    print("Done. Next: python query.py \"What is RAG?\"  OR  python evaluate.py  OR  python app.py")


if __name__ == "__main__":
    main()
