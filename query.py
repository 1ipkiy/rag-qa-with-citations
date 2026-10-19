#!/usr/bin/env python3
"""CLI: retrieve + answer one question with citations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.generate import generate_answer
from src.retrieve import retrieve


def main() -> None:
    parser = argparse.ArgumentParser(description="Query the RAG index")
    parser.add_argument("question", type=str, nargs="?", help="Question to ask")
    parser.add_argument("--index-dir", type=Path, default=ROOT / "index")
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument(
        "--mode",
        choices=["extractive", "flan-t5-small"],
        default="extractive",
        help="Answer mode (default: extractive)",
    )
    parser.add_argument("--json", action="store_true", help="Print raw JSON")
    args = parser.parse_args()

    if not args.question:
        raise SystemExit('Usage: python query.py "Your question here"')

    chunks = retrieve(args.question, index_dir=args.index_dir, top_k=args.top_k)
    result = generate_answer(args.question, chunks, mode=args.mode)

    if args.json:
        print(json.dumps({"question": args.question, **result, "retrieved": chunks}, indent=2))
        return

    print(result["answer"])
    print("\n--- Citations ---")
    for c in result["citations"]:
        print(
            f"{c['id']} {c['source']} | section={c['section']} | score={c['score']}\n"
            f"    {c['snippet'][:200]}..."
        )


if __name__ == "__main__":
    main()
