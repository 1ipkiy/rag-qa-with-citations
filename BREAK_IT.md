# Break It: Intentional Failure Lab (RAG)

**Author:** Miles Robinson · **2026**

I learn this project by **breaking retrieval and citations on purpose**, writing expected vs actual, then fixing it. Experiments map to real files under `src/`, `ingest.py`, `evaluate.py`, and `app.py`.

**Rules:**

1. Work on a branch or stash before big edits.
2. After each experiment, restore defaults and re-run `python ingest.py && python evaluate.py`.
3. Do not invent metrics — re-run eval and read `results/metrics.json`.

Default settings to restore:

```text
chunk_size=500, chunk_overlap=80, top_k=4
embedding_model=sentence-transformers/all-MiniLM-L6-v2
generator=extractive
```

---

## Experiment 1 — Tiny chunks (e.g. 80 chars, 0 overlap)

### What I change
```bash
python ingest.py --chunk-size 80 --chunk-overlap 0
python evaluate.py
```

### What I expect vs what happens
- **Expect:** "Smaller chunks = more precise."
- **Happens:** Snippets become fragmented; citations look like random half-sentences; hit rate may still look okay on this tiny corpus but answers feel broken.

### Why it broke
Chunks lose surrounding context. Similarity may still match keywords, but humans (and generators) cannot use the evidence.

### How to fix it
```bash
python ingest.py --chunk-size 500 --chunk-overlap 80
```

### What I learned
Chunk size is a product decision, not only a hyperparameter. Citations must be readable.

---

## Experiment 2 — Huge overlap (≥ chunk size)

### What I change
```bash
python ingest.py --chunk-size 200 --chunk-overlap 200
```
(or set overlap > size in code)

### What I expect vs what happens
- **Expect:** Safer boundaries.
- **Happens:** `ValueError: chunk_overlap must be smaller than chunk_size` (guard in `chunking.py`), or if you bypass it, near-duplicate chunks flood top-k.

### Why it broke
Overlap must be strictly smaller than window size. Excessive overlap wastes index slots with duplicates.

### How to fix it
Keep `chunk_overlap < chunk_size` (default 80 < 500).

### What I learned
Validate ingest parameters early; silent duplicate-heavy indexes are worse than a loud error.

---

## Experiment 3 — top_k = 1

### What I change
```bash
python evaluate.py --top-k 1
python query.py "What is RAG?" --top-k 1
```

### What I expect vs what happens
- **Expect:** Cleaner answers.
- **Happens:** Still often hits on this corpus, but you lose backup context; multi-aspect questions get thinner evidence; Gradio citations panel looks sparse.

### Why it broke
Single-neighbor retrieval is brittle when the best chunk is a near miss.

### How to fix it
Use `top_k=4` (default) for demos; tune with eval.

### What I learned
Report hit rate at a stated k. Changing k without re-evaluating is lying to yourself.

---

## Experiment 4 — Delete / skip the index

### What I change
```bash
rm -f index/faiss.index index/chunks.json
python query.py "What is IAM?"
# or open Gradio without ingest
```

### What I expect vs what happens
- **Expect:** Mysterious ML error.
- **Happens:** Clear `FileNotFoundError` / Gradio message telling you to run `ingest.py`.

### Why it broke
Serving code assumed an index exists.

### How to fix it
```bash
python ingest.py
```

### What I learned
UX for missing artifacts matters in portfolio demos.

---

## Experiment 5 — Query a topic not in the corpus

### What I change
```bash
python query.py "What is the capital of France?"
```

### What I expect vs what happens
- **Expect:** Model refuses.
- **Happens (extractive):** You still get *some* nearest neighbors (cyber/AI text) with low-ish scores — grounded quotes that do not answer the question. That is retrieval doing its job, not magic understanding.

### Why it broke
Vector search always returns neighbors. Without a score threshold or abstain policy, the UI can look overconfident.

### How to fix it
Add a minimum score cutoff (future work) or manually judge low scores. Document that RAG ≠ world knowledge.

### What I learned
Out-of-domain questions are a feature for demos: show scores and let the user see the miss.

---

## Experiment 6 — Remove one expected document

### What I change
Temporarily move `data/phishing_overview.md` out of `data/`, re-ingest, run eval.

```bash
mkdir -p /tmp/rag-hold
mv data/phishing_overview.md /tmp/rag-hold/
python ingest.py && python evaluate.py
# restore:
mv /tmp/rag-hold/phishing_overview.md data/
python ingest.py && python evaluate.py
```

### What I expect vs what happens
- **Expect:** Phishing questions miss.
- **Happens:** `q03` / `q04` show **MISS** in evaluate output; hit_rate@4 drops below 1.0.

### Why it broke
You cannot retrieve a file that was never indexed.

### How to fix it
Put the file back and re-ingest.

### What I learned
Eval questions are contracts against the corpus. Corpus drift without eval updates looks like "the model got worse."

---

## Experiment 7 — Mismatched embedding model at query time

### What I change
In `src/retrieve.py`, force a different model name than `index/config.json` (conceptually), or rebuild with MiniLM then pretend another model produced the query vector.

Practical demo — rebuild index normally, then in a one-off Python shell embed the query with a **random vector** instead of MiniLM:

```python
import numpy as np
from src.store import FaissStore
store = FaissStore("index"); store.load()
rng = np.random.default_rng(0)
q = rng.normal(size=(384,)).astype("float32")
q /= np.linalg.norm(q)
print([r["source"] for r in store.search(q, top_k=4)])
```

### What I expect vs what happens
- **Expect:** Still somehow works.
- **Happens:** Random / wrong-space queries return arbitrary docs; eval would collapse.

### Why it broke
Nearest neighbor is only meaningful in the **same** embedding space used at ingest.

### How to fix it
Always read `embedding_model` from `index/config.json` (already done in `retrieve.py`).

### What I learned
Version the model name with the index. Silent space mismatch is a classic production bug.

---

## Experiment 8 — Empty or whitespace question in Gradio

### What I change
Open `python app.py`, click Ask with an empty box.

### What I expect vs what happens
- **Expect:** Stack trace.
- **Happens:** Friendly "Enter a question." message (`app.py`).

### Why it broke (if unhandled)
Empty strings still get embedded and retrieve noise.

### How to fix it
Keep the empty-check before retrieve.

### What I learned
Guardrails at the UI boundary are part of ML engineering.

---

## Experiment 9 — Swapped citation IDs vs displayed order

### What I change
In `src/generate.py`, reverse the citation numbering while leaving chunk order the same (or vice versa).

### What I expect vs what happens
- **Expect:** Looks fine.
- **Happens:** Answer says `[1]` but the citations panel's first card is a different chunk — trust destroyed.

### Why it broke
Citation IDs are a contract between prose and the evidence list.

### How to fix it
Build citations from the same ordered list used in the answer (`_format_citations` + zip).

### What I learned
Grounding bugs are often bookkeeping bugs.

---

## Experiment 10 — Skip evaluate and "eyeball" quality

### What I change
Only run `app.py`, never `evaluate.py`. Claim "retrieval works" in the README from vibes.

### What I expect vs what happens
- **Expect:** Faster portfolio shipping.
- **Happens:** You cannot report hit rate; regressions after chunking tweaks go unnoticed.

### Why it broke
Unmeasured systems do not improve.

### How to fix it
Always keep `eval/questions.json` + `evaluate.py` in the loop. README numbers must come from `results/metrics.json`.

### What I learned
Interview signal is **measurement**, not only a pretty Gradio theme.

---

## Quick restore checklist

```bash
source .venv/bin/activate
python ingest.py --chunk-size 500 --chunk-overlap 80
python evaluate.py --top-k 4
python query.py "What are the five NIST CSF functions?"
```

Confirm hit_rate@4 is back to the committed `results/metrics.json` ballpark for this corpus.

---

*Miles Robinson · 2026*
