# Vector Search Basics

Vector search finds items whose embeddings are nearest to a query embedding. It powers semantic search and the retrieval step in RAG.

## Exact vs approximate search

**Exact search** (brute force) compares the query to every vector. It is fine for small corpora (hundreds or a few thousand chunks) and is what many portfolio demos use with FAISS `IndexFlatIP` or `IndexFlatL2`.

**Approximate Nearest Neighbor (ANN)** indexes (HNSW, IVF, etc.) trade a little recall for speed at larger scale. You usually do not need ANN until latency or corpus size forces it.

## FAISS in one paragraph

FAISS (Facebook AI Similarity Search) is a library for efficient similarity search over dense vectors. For a local CPU project, a flat inner-product index over L2-normalized embeddings is a solid default: cosine similarity becomes a dot product, and results are easy to reason about. You store parallel metadata (chunk text, source filename, chunk id) in a JSON or pickle sidecar because FAISS itself stores vectors, not documents.

## Why not only keyword search?

Keyword (BM25) search fails when the question uses different words than the document ("reset credentials" vs "password recovery"). Embeddings catch paraphrase. Hybrid search (BM25 + vectors) is often best in production; a pure vector baseline is enough to learn the RAG loop.

## Evaluating retrieval

Define questions with known relevant documents. Measure **hit rate@k**: fraction of questions where at least one correct source appears in the top-k results. Also track mean reciprocal rank (MRR) if you care about position. Report real numbers from a script — never invent metrics for a README.

## Operational tips

Rebuild the index when documents change. Version your embedding model name beside the index so you do not mix vectors from different models. Keep chunk size and overlap documented; they affect both quality and index size.
