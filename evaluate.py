#!/usr/bin/env python3
"""Evaluate retrieval hit rate@k and MRR on eval/questions.json."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.retrieve import retrieve


def hit_at_k(retrieved_sources: list[str], expected: list[str]) -> bool:
    expected_set = {e.lower() for e in expected}
    return any(src.lower() in expected_set for src in retrieved_sources)


def reciprocal_rank(retrieved_sources: list[str], expected: list[str]) -> float:
    expected_set = {e.lower() for e in expected}
    for i, src in enumerate(retrieved_sources, start=1):
        if src.lower() in expected_set:
            return 1.0 / i
    return 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate RAG retrieval")
    parser.add_argument("--questions", type=Path, default=ROOT / "eval" / "questions.json")
    parser.add_argument("--index-dir", type=Path, default=ROOT / "index")
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "metrics.json")
    parser.add_argument("--top-k", type=int, default=4)
    args = parser.parse_args()

    if not args.questions.exists():
        raise SystemExit(f"Missing eval set: {args.questions}")

    items = json.loads(args.questions.read_text(encoding="utf-8"))
    if not isinstance(items, list) or not items:
        raise SystemExit("questions.json must be a non-empty list")

    per_question = []
    hits = 0
    mrr_sum = 0.0

    for item in items:
        qid = item["id"]
        question = item["question"]
        expected = item["expected_sources"]
        results = retrieve(question, index_dir=args.index_dir, top_k=args.top_k)
        sources = [r["source"] for r in results]
        hit = hit_at_k(sources, expected)
        rr = reciprocal_rank(sources, expected)
        hits += int(hit)
        mrr_sum += rr
        per_question.append(
            {
                "id": qid,
                "question": question,
                "expected_sources": expected,
                "retrieved_sources": sources,
                "scores": [round(float(r["score"]), 4) for r in results],
                "hit_at_k": hit,
                "reciprocal_rank": round(rr, 4),
            }
        )
        status = "HIT" if hit else "MISS"
        print(f"[{status}] {qid}: top={sources[:2]} expected={expected}")

    n = len(items)
    metrics = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "num_questions": n,
        "top_k": args.top_k,
        "hit_rate_at_k": round(hits / n, 4),
        "hits": hits,
        "mrr": round(mrr_sum / n, 4),
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "store": "faiss.IndexFlatIP",
        "per_question": per_question,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print()
    print(f"hit_rate@{args.top_k} = {metrics['hit_rate_at_k']} ({hits}/{n})")
    print(f"MRR            = {metrics['mrr']}")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
