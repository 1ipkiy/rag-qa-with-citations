# RAG Q&A with Citations

**Author:** Miles Robinson · **Year:** 2026  
**Portfolio:** Project 2 of an AI engineering series  
**Stack:** sentence-transformers (MiniLM) · FAISS · Gradio · optional FLAN-T5-small

A local **retrieval-augmented generation** demo over a small cybersecurity + AI educational corpus. Every answer returns **citations** (source file, section, similarity score, snippet) you can verify. CPU-only, free stack, real retrieval metrics from a script.

Also see [SMS Spam vs Ham Classifier](https://github.com/1ipkiy/sms-spam-classifier) (Project 1).

---

## Problem statement

LLMs alone invent facts and cannot point at your documents. RAG fixes that by:

1. Chunking your corpus
2. Embedding chunks into vectors
3. Retrieving top-k neighbors for a question
4. Answering **from those chunks** with citations you can verify

The goal is a **reproducible, CPU-only** pipeline with real retrieval metrics — not a chat wrapper around a paid API. This is the grounded-documents skill stack interviewers hire for in applied AI roles.

---

## Corpus

Seven original short markdown docs under `data/` (~200–600 words each):

| File | Topic |
|------|--------|
| `nist_csf_overview.md` | NIST CSF five functions, profiles/tiers |
| `phishing_overview.md` | Phishing patterns and layered defenses |
| `iam_concepts.md` | AuthN / AuthZ, RBAC vs ABAC, SSO |
| `embeddings_explained.md` | What embeddings are and why they matter |
| `rag_explained.md` | RAG pipeline, citations, failure modes |
| `vector_search_basics.md` | FAISS, exact vs ANN, hit rate@k |
| `secure_coding_basics.md` | Secrets, prompt injection awareness, input trust |

Swap or add `.md` files anytime, then re-run `python ingest.py`.

---

## Approach

| Piece | Choice | Why |
|-------|--------|-----|
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Free, ~80MB, strong on short text, CPU-friendly (384-dim) |
| Vector store | **FAISS** `IndexFlatIP` | No daemon, tiny deps; L2-normalized vectors → cosine via inner product |
| Generation (default) | **Extractive / template RAG** | Honest grounding: quoted passages + citation IDs; works offline after model download |
| Generation (optional) | `google/flan-t5-small` | Small CPU generative rewrite; falls back to extractive if unavailable |
| UI | Gradio | Fast local demo with visible citations |
| Eval | Hit rate@k + MRR | 12 questions with expected sources in `eval/questions.json` |

**Why not Chroma?** FAISS keeps this portfolio lean and makes the index files easy to inspect (`index/faiss.index` + `index/chunks.json`).

Pipeline: `ingest.py` (chunk → embed → index) → `query.py` / `app.py` (retrieve → answer + cite) → `evaluate.py` (metrics).

---

## Results

> Numbers from `python evaluate.py` on this repo (CPU). See `results/metrics.json`.

| Metric | Value |
|--------|------:|
| Questions | 12 |
| Top-k | 4 |
| **Hit rate@4** | **1.0000** (12/12) |
| **MRR** | **1.0000** |

**Honesty note:** This is a small, topic-aligned educational corpus. High hit rate is expected when questions match document vocabulary. The point of the eval is the **measurement habit** — hit rate@k and MRR from a script, never invented README numbers. On a messier real corpus these scores would drop and that would be useful signal.

---

## Project structure

```
rag-qa/
├── README.md
├── HOW_I_BUILT_IT.md      # first-person build story
├── BREAK_IT.md            # intentional what-ifs lab
├── requirements.txt
├── .gitignore
├── ingest.py              # chunk → embed → FAISS index
├── query.py               # CLI Q&A with citations
├── evaluate.py            # hit rate@k + MRR → results/metrics.json
├── app.py                 # Gradio demo
├── data/*.md              # corpus (7 docs)
├── eval/questions.json    # 12 Q&A pairs with expected sources
├── src/
│   ├── chunking.py
│   ├── embeddings.py
│   ├── store.py           # FAISS + JSON metadata
│   ├── retrieve.py
│   └── generate.py        # extractive + optional FLAN-T5
├── index/                 # built by ingest.py (gitignored)
└── results/metrics.json   # written by evaluate.py
```

---

## Setup & run

```bash
cd rag-qa
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# build the vector index (downloads MiniLM ~80MB on first run)
python ingest.py

# retrieval metrics → results/metrics.json
python evaluate.py

# CLI Q&A with citations
python query.py "What is RAG?"
python query.py "Explain IAM authentication vs authorization" --mode flan-t5-small

# Gradio demo (default http://127.0.0.1:7861)
python app.py
```

`ingest.py` creates `index/faiss.index`, `index/chunks.json`, and `index/config.json` (gitignored; regenerate locally).

---

## Learn by breaking it

- [HOW_I_BUILT_IT.md](HOW_I_BUILT_IT.md) — first-person build story
- [BREAK_IT.md](BREAK_IT.md) — intentional what-ifs, why it broke, how to fix

---

## License / notes

Educational portfolio project. Original `data/` docs and code are for learning / interview demos, not production security advice. The FAISS index and model caches are not committed; always produce the index with `ingest.py`. CPU-only free stack — no paid LLM API required for the default extractive path.

*Miles Robinson · Cybersecurity + AI Engineering · CPCC → UNC Charlotte · 2026*
