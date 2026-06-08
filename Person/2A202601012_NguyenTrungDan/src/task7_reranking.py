"""
Task 7 - Reranking module.

This file implements two no-API rerankers:
- Cross-encoder fallback: query/document token overlap mixed with original score.
- RRF: Reciprocal Rank Fusion for merging semantic and lexical ranked lists.
"""

import math

try:
    from .task4_chunking_indexing import tokenize
except ImportError:
    from task4_chunking_indexing import tokenize


def _normalize(values: list[float]) -> list[float]:
    if not values:
        return []
    high = max(values)
    low = min(values)
    if high == low:
        return [1.0 if high > 0 else 0.0 for _ in values]
    return [(value - low) / (high - low) for value in values]


def _token_overlap_score(query: str, content: str) -> float:
    query_tokens = set(tokenize(query))
    doc_tokens = tokenize(content)
    if not query_tokens or not doc_tokens:
        return 0.0
    doc_set = set(doc_tokens)
    recall = len(query_tokens & doc_set) / len(query_tokens)
    density = sum(1 for token in doc_tokens if token in query_tokens) / len(doc_tokens)
    return 0.85 * recall + 0.15 * density


def rerank_cross_encoder(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    """
    Re-score candidates with a local cross-encoder-style relevance heuristic.
    """
    if top_k <= 0 or not candidates:
        return []

    original_scores = _normalize([float(c.get("score", 0.0)) for c in candidates])
    reranked = []
    for candidate, original in zip(candidates, original_scores):
        overlap = _token_overlap_score(query, candidate.get("content", ""))
        final_score = 0.65 * overlap + 0.35 * original
        item = candidate.copy()
        item["score"] = float(final_score)
        reranked.append(item)

    reranked.sort(key=lambda item: item["score"], reverse=True)
    return reranked[:top_k]


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    size = min(len(a), len(b))
    dot = sum(a[i] * b[i] for i in range(size))
    na = math.sqrt(sum(value * value for value in a[:size])) or 1.0
    nb = math.sqrt(sum(value * value for value in b[:size])) or 1.0
    return dot / (na * nb)


def rerank_mmr(
    query_embedding: list[float],
    candidates: list[dict],
    top_k: int = 5,
    lambda_param: float = 0.7,
) -> list[dict]:
    """Maximal Marginal Relevance selection for candidates with embeddings."""
    selected: list[int] = []
    remaining = list(range(len(candidates)))

    while remaining and len(selected) < top_k:
        best_idx = remaining[0]
        best_score = float("-inf")
        for idx in remaining:
            embedding = candidates[idx].get("embedding", [])
            relevance = _cosine(query_embedding, embedding)
            diversity_penalty = 0.0
            for selected_idx in selected:
                diversity_penalty = max(
                    diversity_penalty,
                    _cosine(embedding, candidates[selected_idx].get("embedding", [])),
                )
            mmr_score = lambda_param * relevance - (1 - lambda_param) * diversity_penalty
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = idx
        selected.append(best_idx)
        remaining.remove(best_idx)

    results = []
    for idx in selected:
        item = candidates[idx].copy()
        item["score"] = float(item.get("score", 0.0))
        results.append(item)
    return results


def rerank_rrf(ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60) -> list[dict]:
    """
    Reciprocal Rank Fusion.

    RRF(d) = sum(1 / (k + rank_r(d))) across rankers.
    """
    scores: dict[str, float] = {}
    content_map: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):
            key = item.get("content", "")
            if not key:
                continue
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
            content_map[key] = item

    ordered = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
    results = []
    for content, score in ordered[:top_k]:
        item = content_map[content].copy()
        item["score"] = float(score)
        results.append(item)
    return results


def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
    method: str = "cross_encoder",
) -> list[dict]:
    """Unified reranking interface."""
    if method == "cross_encoder":
        return rerank_cross_encoder(query, candidates, top_k)
    if method == "rrf":
        return rerank_rrf([candidates], top_k=top_k)
    if method == "mmr":
        # Fall back to cross-encoder when embeddings are not supplied.
        return rerank_cross_encoder(query, candidates, top_k)
    raise ValueError(f"Unknown rerank method: {method}")


if __name__ == "__main__":
    dummy = [
        {"content": "Dieu 249 toi tang tru trai phep chat ma tuy", "score": 0.8, "metadata": {}},
        {"content": "Nghe si bi bat vi su dung ma tuy", "score": 0.6, "metadata": {}},
    ]
    for result in rerank("hinh phat ma tuy", dummy):
        print(f"[{result['score']:.3f}] {result['content']}")
