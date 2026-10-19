# RAG Q&A with Citations

**Author:** Miles Robinson · **Year:** 2026  
**Stack:** sentence-transformers (MiniLM) · FAISS · Gradio · optional FLAN-T5-small

A local **retrieval-augmented generation** demo over a small cybersecurity + AI educational corpus. Every answer returns **citations** (source file, section, similarity score, snippet).

This is **Project 2** in an AI engineering portfolio (after the [SMS spam classifier](https://github.com/1ipkiy/sms-spam-classifier)): the common interview signal for applied AI roles.

---

## Problem statement

LLMs alone invent facts and cannot point at your documents. RAG fixes that by:

1. Chunking your corpus
2. Embedding chunks into vectors
3. Retrieving top-k neighbors for a question
4. Answering **from those chunks** with citations you can verify

The goal is a **reproducible, CPU-only** pipeline with real retrieval metrics — not a chat wrapper around a paid API.

---

## Architecture choice

| Piece | Choice | Why |
|-------|--------|-----|
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Free, ~80MB, strong on short text, CPU-friendly (384-dim) |
| Vector store | **FAISS** `IndexFlatIP` | No daemon, tiny deps, exact search is fine for dozens of chunks; L2-normalized vectors → cosine via inner product |
| Generation (default) | **Extractive / template RAG** | Honest grounding: quoted passages + citation IDs; works fully offline after model download |
| Generation (optional) | `google/flan-t5-small` | Small CPU generative rewrite; falls back to extractive if unavailable |
| UI | Gradio | Fast local demo with visible citations |

**Why not Chroma?** Chroma is great for app-style persistence, but FAISS keeps this portfolio lean and makes the index files easy to inspect (`index/faiss.index` + `index/chunks.json`).

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

## Results (retrieval eval)

> Numbers from `python evaluate.py` on this machine (CPU). See `results/metrics.json`.

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
├── HOW_I_BUILT_IT.md      # first-person build walkthrough
├── BREAK_IT.md            # intentional failure lab (≥8 experiments)
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

## How to run

### 1. Setup

```bash
cd rag-qa
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Ingest (build the index)

```bash
python ingest.py
```

First run downloads MiniLM (~80MB). Creates `index/faiss.index`, `index/chunks.json`, `index/config.json`.

### 3. Evaluate retrieval

```bash
python evaluate.py
```

Prints hit/miss per question and writes `results/metrics.json`.

### 4. CLI query

```bash
python query.py "What is RAG?"
python query.py "Explain IAM authentication vs authorization" --mode flan-t5-small
```

### 5. Gradio demo

```bash
python app.py
```

Open `http://127.0.0.1:7861`. You should see the answer plus a citations panel (filename, section, score, snippet).

---

## Learn by breaking it

| Doc | Purpose |
|-----|---------|
| [`HOW_I_BUILT_IT.md`](HOW_I_BUILT_IT.md) | First-person: chunk → embed → FAISS → retrieve → cite → eval → Gradio |
| [`BREAK_IT.md`](BREAK_IT.md) | Lab guide — chunk size, overlap, bad k, wrong model mix, empty index, … |

---

## Design notes

- **CPU-only, free stack** — no paid LLM API required for the default path.
- **Citations are first-class** — interviewers care that you can ground and verify.
- **Index is not committed** — always produce it with `ingest.py`.
- Educational corpus only; not production security advice.

---

## License

Code and original `data/` docs are for portfolio / educational use.

---

*Miles Robinson · Cybersecurity + AI Engineering · CPCC → UNC Charlotte · 2026*
