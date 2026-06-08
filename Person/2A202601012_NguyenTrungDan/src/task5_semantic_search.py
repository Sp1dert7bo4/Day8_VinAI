"""
Task 5 - Semantic search module.

Uses deterministic hashed bag-of-words cosine similarity as a local dense
retrieval fallback. It mirrors the vector-store interface without requiring a
running Weaviate instance.
"""

import math

try:
    from .task4_chunking_indexing import EMBEDDING_DIM, load_index, tokenize
except ImportError:  # Allows running this file directly.
    from task4_chunking_indexing import EMBEDDING_DIM, load_index, tokenize


def _vectorize(text: str, dim: int = EMBEDDING_DIM) -> dict[int, float]:
    counts: dict[int, float] = {}
    for token in tokenize(text):
        idx = hash(token) % dim
        counts[idx] = counts.get(idx, 0.0) + 1.0
    norm = math.sqrt(sum(v * v for v in counts.values())) or 1.0
    return {idx: value / norm for idx, value in counts.items()}


def _cosine_sparse(a: dict[int, float], b: dict[int, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(value * b.get(idx, 0.0) for idx, value in a.items())


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Search chunks by vector similarity.

    Returns:
        List of {'content': str, 'score': float, 'metadata': dict}
        sorted by score descending.
    """
    if top_k <= 0:
        return []

    chunks = load_index()
    query_vector = _vectorize(query)
    results = []
    for chunk in chunks:
        score = _cosine_sparse(query_vector, _vectorize(chunk["content"]))
        if score > 0:
            results.append(
                {
                    "content": chunk["content"],
                    "score": float(score),
                    "metadata": chunk.get("metadata", {}),
                }
            )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    for result in semantic_search("hinh phat ma tuy", top_k=5):
        print(f"[{result['score']:.3f}] {result['content'][:100]}...")
