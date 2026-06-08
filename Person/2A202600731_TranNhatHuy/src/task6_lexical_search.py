"""Task 6: lexical retrieval using BM25."""

import re

from rank_bm25 import BM25Okapi

from .task4_chunking_indexing import load_index

CORPUS: list[dict] = []
_BM25 = None


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower(), flags=re.UNICODE)


def build_bm25_index(corpus: list[dict]):
    """Build a BM25 index from a list of chunk dictionaries."""
    return BM25Okapi([_tokenize(item["content"]) for item in corpus])


def _ensure_index():
    global CORPUS, _BM25
    if _BM25 is None:
        CORPUS = load_index()
        _BM25 = build_bm25_index(CORPUS) if CORPUS else None


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Return positive-score BM25 results sorted descending."""
    if not query.strip() or top_k <= 0:
        return []
    _ensure_index()
    if _BM25 is None:
        return []
    scores = _BM25.get_scores(_tokenize(query))
    indices = scores.argsort()[::-1][:top_k]
    return [
        {
            "content": CORPUS[index]["content"],
            "score": float(scores[index]),
            "metadata": CORPUS[index].get("metadata", {}),
        }
        for index in indices
        if scores[index] > 0
    ]


if __name__ == "__main__":
    for result in lexical_search("Điều 249 tàng trữ trái phép chất ma tuý", 5):
        print(f"[{result['score']:.3f}] {result['content'][:100]}")
