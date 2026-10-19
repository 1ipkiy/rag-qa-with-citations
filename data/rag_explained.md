# What Is Retrieval-Augmented Generation (RAG)?

Retrieval-Augmented Generation (RAG) is a pattern that combines **document retrieval** with a **language model**. Instead of asking the model to answer only from its training memory, you first fetch relevant passages from your own corpus and then ask the model to answer using those passages.

## The basic pipeline

1. **Ingest** — Split documents into chunks; embed each chunk; store vectors in an index (FAISS, Chroma, etc.).
2. **Retrieve** — Embed the user question; find the top-k nearest chunks.
3. **Generate** — Pass the question plus retrieved text to a generator (or build an extractive answer from the chunks).
4. **Cite** — Show which sources supported the answer so users can verify.

Citations are not optional polish. They are how you show the system is grounded and how you debug bad answers.

## Why RAG exists

Large language models hallucinate facts and go stale. RAG lets you:

- Ground answers in **your** documents (policies, runbooks, notes)
- Update knowledge by re-indexing files without retraining a model
- Point users at evidence (filename, section, snippet)

## Failure modes

- **Bad chunking** — Truncating mid-sentence or splitting related context
- **Wrong embedding model** — Poor recall for your domain vocabulary
- **Too small k** — Miss the right passage
- **Too large k / noisy context** — Distract the generator
- **No evaluation** — You cannot improve what you do not measure

Retrieval hit rate (was the correct document in top-k?) is a simple, honest metric for portfolio projects.

## Extractive vs generative RAG

**Generative RAG** uses an LLM to rewrite an answer from context. **Extractive / template RAG** stitches quoted passages and labels them with citation IDs. Extractive systems are easier to run on CPU, more transparent, and still demonstrate the retrieval skills interviewers care about. Generative systems sound smoother but need a model and careful prompting to stay faithful to sources.
