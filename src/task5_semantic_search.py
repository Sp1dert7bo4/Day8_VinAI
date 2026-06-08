"""Task 5: local semantic search using TF-IDF cosine similarity."""

from .task4_chunking_indexing import load_index


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Return chunks ranked by local TF-IDF cosine similarity."""
    if not query.strip() or top_k <= 0:
        return []
    chunks = load_index()
    if not chunks:
        return []

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    texts = [chunk["content"] for chunk in chunks]
    vectorizer = TfidfVectorizer(
        lowercase=True, analyzer="char_wb", ngram_range=(3, 5), max_features=30000
    )
    matrix = vectorizer.fit_transform(texts + [query])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    indices = scores.argsort()[::-1][:top_k]
    return [
        {
            "content": chunks[index]["content"],
            "score": float(scores[index]),
            "metadata": chunks[index].get("metadata", {}),
        }
        for index in indices
        if scores[index] > 0
    ]


if __name__ == "__main__":
    for result in semantic_search("hình phạt tàng trữ ma tuý", 5):
        print(f"[{result['score']:.3f}] {result['content'][:100]}")
