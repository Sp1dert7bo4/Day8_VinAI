"""
Task 6 - Lexical search module using BM25.

BM25 rewards exact keyword matches while normalizing document length. This is
useful for legal article numbers, drug names, and proper nouns that dense search
may blur.
"""

import math
from collections import Counter

try:
    from .task4_chunking_indexing import load_index, tokenize
except ImportError:
    from task4_chunking_indexing import load_index, tokenize

CORPUS: list[dict] = []


def _manual_bm25_scores(tokenized_corpus: list[list[str]], query_tokens: list[str]) -> list[float]:
    n_docs = len(tokenized_corpus)
    if not n_docs:
        return []

    avgdl = sum(len(doc) for doc in tokenized_corpus) / n_docs or 1.0
    dfs = Counter()
    doc_counters = []
    for doc in tokenized_corpus:
        counter = Counter(doc)
        doc_counters.append(counter)
        for token in counter:
            dfs[token] += 1

    k1 = 1.5
    b = 0.75
    scores = []
    for doc_tokens, counter in zip(tokenized_corpus, doc_counters):
        score = 0.0
        doc_len = len(doc_tokens) or 1
        for token in query_tokens:
            tf = counter.get(token, 0)
            if not tf:
                continue
            idf = math.log(1 + (n_docs - dfs[token] + 0.5) / (dfs[token] + 0.5))
            denom = tf + k1 * (1 - b + b * doc_len / avgdl)
            score += idf * (tf * (k1 + 1)) / denom
        scores.append(score)
    return scores


def build_bm25_index(corpus: list[dict]):
    """
    Build a BM25 index from corpus.

    Args:
        corpus: List of {'content': str, 'metadata': dict}
    """
    tokenized_corpus = [tokenize(doc["content"]) for doc in corpus]
    try:
        from rank_bm25 import BM25Okapi

        return BM25Okapi(tokenized_corpus)
    except ImportError:
        return tokenized_corpus


def _get_corpus() -> list[dict]:
    global CORPUS
    if not CORPUS:
        CORPUS = load_index()
    return CORPUS


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Keyword search using BM25.

    Returns:
        List of {'content': str, 'score': float, 'metadata': dict}
        sorted by score descending.
    """
    if top_k <= 0:
        return []

    corpus = _get_corpus()
    if not corpus:
        return []

    query_tokens = tokenize(query)
    tokenized_corpus = [tokenize(doc["content"]) for doc in corpus]
    bm25 = build_bm25_index(corpus)

    if hasattr(bm25, "get_scores"):
        scores = [float(score) for score in bm25.get_scores(query_tokens)]
    else:
        scores = _manual_bm25_scores(tokenized_corpus, query_tokens)

    ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
    results = []
    for idx, score in ranked[:top_k]:
        if score <= 0:
            continue
        doc = corpus[idx]
        results.append(
            {
                "content": doc["content"],
                "score": float(score),
                "metadata": doc.get("metadata", {}),
            }
        )
    return results


if __name__ == "__main__":
    for result in lexical_search("Dieu 249 ma tuy", top_k=5):
        print(f"[{result['score']:.3f}] {result['content'][:100]}...")
