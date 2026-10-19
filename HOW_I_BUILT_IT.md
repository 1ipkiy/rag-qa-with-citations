# How I Built This RAG Q&A System

**Author:** Miles Robinson · **2026**

This is my walkthrough of Project 2 — how I went from "interviewers keep asking about RAG" to a local cited Q&A app over my own docs. Written so I can re-read it when retrieval looks weird.

---

## 1. Why RAG (after the spam classifier)

Project 1 taught me train → eval → Gradio. Project 2 is the other skill stack people hire for: **grounded answers over private documents**.

I care about cybersecurity + AI, so the corpus mixes NIST CSF / phishing / IAM with embeddings / RAG / vector search. That way the demo is on-brand when I talk about both sides of my background.

---

## 2. Corpus first, model second

I wrote seven short original markdown files under `data/` (no textbook dumps). Roughly 200–600 words each. Why markdown?

- Easy to chunk and to edit
- Headings become useful **section** labels in citations
- I can swap docs later without changing code

If the corpus is garbage, no embedding model saves you. Start with clear docs.

---

## 3. Chunking (size + overlap)

In `src/chunking.py` I:

1. Split on `#` / `##` / `###` headings so sections stay somewhat coherent
2. Cut each section into ~**500 character** windows with **80 character overlap**

Overlap exists so a sentence that straddles a boundary still appears in at least one chunk. Too-small chunks lose context; too-large chunks dilute similarity. 500/80 was a practical starting point for these short docs — I got **42 chunks** from 7 files.

---

## 4. Embeddings: MiniLM on CPU

I use `sentence-transformers/all-MiniLM-L6-v2`:

- Outputs 384-dim vectors
- Fast on CPU
- Good enough semantic search for short educational text

`src/embeddings.py` L2-normalizes vectors so cosine similarity = inner product. That matches FAISS `IndexFlatIP`.

---

## 5. Why FAISS (not Chroma)

I picked **FAISS** because:

- No background server
- One binary index file + a JSON sidecar of chunk metadata
- Exact flat search is fine when N = 42

Chroma would be fine too; I wanted the portfolio dependency list small and the index inspectable. Decision is documented in `src/store.py` and the README.

At ingest time I write:

- `index/faiss.index` — vectors
- `index/chunks.json` — text, source, section, chunk_id
- `index/config.json` — model name, chunk settings, dim

Keeping the embedding model name next to the index matters: mixing vectors from two models silently breaks search.

---

## 6. Retrieve → generate (extractive by default)

`retrieve.py` embeds the question and returns top-k neighbors with scores.

For answers I default to **extractive / template RAG** (`src/generate.py`):

- List the top chunks as quoted evidence with `[1]`, `[2]`, …
- Show filename, section, and score
- Label the mode so nobody thinks a giant LLM invented the prose

That is intentional honesty. Interviewers like citations more than fluent hallucination.

Optional mode: `flan-t5-small` rewrites a short answer from the same context. If the model is missing or fails, I fall back to extractive instead of crashing.

---

## 7. Evaluation before the UI polish

I wrote 12 questions in `eval/questions.json`, each with `expected_sources` (filenames). `evaluate.py` measures:

- **Hit rate@k** — was a correct doc in the top-k?
- **MRR** — how high was the first correct doc?

My run on this corpus:

| Metric | Value |
|--------|------:|
| hit_rate@4 | 1.0 (12/12) |
| MRR | 1.0 |

Perfect scores on a tiny aligned corpus are **not** proof I solved retrieval forever. They prove the pipeline works end-to-end and that I measure. On a noisy real wiki these numbers would be the interesting part.

---

## 8. Gradio UI

`app.py` is the interview demo: question box → markdown answer → citations panel. Port **7861** so it does not collide with Project 1's spam demo on 7860.

If the index is missing, the UI tells you to run `ingest.py` instead of failing opaquely.

---

## 9. What I would do next

- Hybrid BM25 + vectors
- Better chunking (token-based, recursive)
- A faithfulness check (does the answer span appear in context?)
- Prompt-injection tests against retrieved docs (ties to my security track)

---

## Commands I actually use

```bash
source .venv/bin/activate
python ingest.py
python evaluate.py
python query.py "What is phishing?"
python app.py
```

---

*Miles Robinson · CPCC → UNC Charlotte · 2026*
