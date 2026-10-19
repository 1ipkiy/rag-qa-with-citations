# What Are Embeddings?

An embedding is a list of numbers (a vector) that represents text, an image, or another object in a way that captures meaning. Similar meanings land near each other in that vector space.

## Intuition

If you embed the sentences "reset my password" and "I forgot my login credentials," a good embedding model places them close together. "Quantum chromodynamics" should land farther away. Distance (or similarity) between vectors becomes a proxy for semantic relatedness.

Common similarity measures:

- **Cosine similarity** — angle between vectors (popular for text)
- **Dot product** — related to cosine when vectors are normalized
- **Euclidean distance** — straight-line distance

## How models produce them

Modern text embeddings often use transformer encoders (for example MiniLM or BERT-family models) trained so that related sentences score high similarity. The model maps variable-length text to a fixed-size vector (e.g., 384 dimensions for `all-MiniLM-L6-v2`).

Training objectives vary (contrastive learning, next-sentence style tasks, etc.), but the practical result for engineers is: call `model.encode(text)` and get a float array.

## Why engineers care

Embeddings unlock:

- **Semantic search** — find documents by meaning, not only keyword match
- **Clustering and topic discovery**
- **RAG (retrieval-augmented generation)** — retrieve relevant chunks before answering
- **Deduplication and near-duplicate detection**

They are not magic. Domain shift (medical jargon vs casual chat), chunk boundaries, and embedding model choice all change quality. Always evaluate retrieval on your own questions.

## Practical note

For CPU-friendly local demos, `sentence-transformers/all-MiniLM-L6-v2` is a common default: small, fast, and good enough for short educational corpora. Larger models can improve quality at the cost of memory and latency.
