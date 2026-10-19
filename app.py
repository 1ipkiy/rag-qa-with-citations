#!/usr/bin/env python3
"""Gradio demo: question → answer + citations."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import gradio as gr

from src.generate import generate_answer
from src.retrieve import retrieve

INDEX_DIR = ROOT / "index"
EXAMPLES = [
    "What are the five functions of the NIST Cybersecurity Framework?",
    "How does phishing typically trick people?",
    "What is the difference between authentication and authorization?",
    "What is an embedding in machine learning?",
    "Why use RAG instead of only an LLM?",
    "What is FAISS used for?",
]


def format_citations_md(citations: list[dict]) -> str:
    if not citations:
        return "_No citations — index empty or no matches._"
    blocks = []
    for c in citations:
        blocks.append(
            f"### {c['id']} `{c['source']}`\n"
            f"- **Section:** {c.get('section') or '—'}\n"
            f"- **Score:** {c['score']}\n"
            f"- **Chunk ID:** `{c.get('chunk_id', '')}`\n\n"
            f"> {c['snippet']}"
        )
    return "\n\n".join(blocks)


def answer_question(question: str, top_k: int, mode: str):
    question = (question or "").strip()
    if not question:
        return "Enter a question.", ""
    if not (INDEX_DIR / "faiss.index").exists():
        return (
            "Index not found. From the project root run:\n\n"
            "```bash\npython ingest.py\n```",
            "",
        )
    chunks = retrieve(question, index_dir=INDEX_DIR, top_k=int(top_k))
    result = generate_answer(question, chunks, mode=mode)
    return result["answer"], format_citations_md(result["citations"])


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="RAG Q&A with Citations") as demo:
        gr.Markdown(
            """
# RAG Q&A with Citations
**Author:** Miles Robinson · 2026

Ask a question over a small cybersecurity + AI educational corpus.
Answers include **source filename, section, score, and snippet**.

Default mode is **extractive RAG** (quotes + citation IDs). Optional **FLAN-T5-small**
rewrites a short answer on CPU (first call downloads ~300MB).
            """
        )
        with gr.Row():
            question = gr.Textbox(
                label="Question",
                placeholder="e.g. What is RAG?",
                lines=2,
                scale=4,
            )
        with gr.Row():
            top_k = gr.Slider(1, 8, value=4, step=1, label="Top-k chunks")
            mode = gr.Dropdown(
                choices=["extractive", "flan-t5-small"],
                value="extractive",
                label="Answer mode",
            )
            btn = gr.Button("Ask", variant="primary")
        answer = gr.Markdown(label="Answer")
        citations = gr.Markdown(label="Citations")
        gr.Examples(examples=EXAMPLES, inputs=question)

        btn.click(answer_question, inputs=[question, top_k, mode], outputs=[answer, citations])
        question.submit(answer_question, inputs=[question, top_k, mode], outputs=[answer, citations])

        gr.Markdown(
            "_Local CPU demo · MiniLM embeddings · FAISS · corpus in `data/` · "
            "re-index with `python ingest.py`_"
        )
    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.launch(server_name="127.0.0.1", server_port=7861)
