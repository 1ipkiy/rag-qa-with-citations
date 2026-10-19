"""Answer generation: extractive RAG (default) + optional FLAN-T5-small.

Default path is extractive/template synthesis — honest, offline, CPU-friendly.
Set generator='flan-t5-small' to rewrite with a small local instruct model.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any


def _format_citations(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cites = []
    for i, c in enumerate(chunks, start=1):
        cites.append(
            {
                "id": f"[{i}]",
                "chunk_id": c.get("chunk_id", ""),
                "source": c.get("source", ""),
                "section": c.get("section", ""),
                "score": round(float(c.get("score", 0.0)), 4),
                "snippet": c.get("text", "")[:400],
            }
        )
    return cites


def generate_extractive(query: str, chunks: list[dict[str, Any]]) -> dict[str, Any]:
    """Synthesize an answer from retrieved chunks with explicit quotes + citation IDs."""
    if not chunks:
        return {
            "answer": (
                "I could not find relevant passages in the indexed corpus. "
                "Try rephrasing, or re-run ingest.py after adding documents to data/."
            ),
            "mode": "extractive",
            "citations": [],
        }

    citations = _format_citations(chunks)
    lines = [
        f"**Question:** {query}",
        "",
        "Based on the retrieved sources, here is a grounded summary:",
        "",
    ]
    for cite, chunk in zip(citations, chunks):
        excerpt = chunk["text"].strip().replace("\n", " ")
        if len(excerpt) > 280:
            excerpt = excerpt[:277] + "..."
        lines.append(
            f"- {cite['id']} From `{cite['source']}`"
            + (f" § {cite['section']}" if cite["section"] else "")
            + f" (score={cite['score']}): \"{excerpt}\""
        )

    lines.extend(
        [
            "",
            "_Mode: extractive RAG — answer is synthesized from retrieved quotes, "
            "not free-form LLM invention._",
        ]
    )
    return {
        "answer": "\n".join(lines),
        "mode": "extractive",
        "citations": citations,
    }


@lru_cache(maxsize=1)
def _load_flan(model_name: str = "google/flan-t5-small"):
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    import torch

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    model.eval()
    device = torch.device("cpu")
    model.to(device)
    return tokenizer, model, device


def generate_flan_t5(
    query: str,
    chunks: list[dict[str, Any]],
    model_name: str = "google/flan-t5-small",
    max_new_tokens: int = 192,
) -> dict[str, Any]:
    """Generate a short answer with FLAN-T5-small, then attach the same citations."""
    if not chunks:
        return generate_extractive(query, chunks)

    citations = _format_citations(chunks)
    context_parts = []
    for cite, chunk in zip(citations, chunks):
        context_parts.append(f"{cite['id']} ({cite['source']}): {chunk['text']}")
    context = "\n\n".join(context_parts)

    prompt = (
        "Answer the question using only the context. "
        "Include citation ids like [1] or [2] in your answer.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n\nAnswer:"
    )

    try:
        import torch

        tokenizer, model, device = _load_flan(model_name)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                num_beams=2,
                early_stopping=True,
            )
        text = tokenizer.decode(out[0], skip_special_tokens=True).strip()
        if not text:
            return generate_extractive(query, chunks)
        answer = text + "\n\n_Mode: generative (google/flan-t5-small) grounded on retrieved context._"
        return {"answer": answer, "mode": "flan-t5-small", "citations": citations}
    except Exception as exc:  # noqa: BLE001 — fall back honestly
        fallback = generate_extractive(query, chunks)
        fallback["answer"] = (
            f"_FLAN-T5 unavailable ({exc}); using extractive mode._\n\n" + fallback["answer"]
        )
        fallback["mode"] = "extractive-fallback"
        return fallback


def generate_answer(
    query: str,
    chunks: list[dict[str, Any]],
    mode: str = "extractive",
) -> dict[str, Any]:
    mode = (mode or "extractive").lower()
    if mode in {"flan", "flan-t5", "flan-t5-small", "generative"}:
        return generate_flan_t5(query, chunks)
    return generate_extractive(query, chunks)
