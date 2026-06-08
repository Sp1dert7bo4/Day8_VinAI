"""Task 7: local reranking, MMR and Reciprocal Rank Fusion."""

import re

import numpy as np


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower(), flags=re.UNICODE))


def _cosine(left, right) -> float:
    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    denominator = np.linalg.norm(left) * np.linalg.norm(right)
    return float(np.dot(left, right) / denominator) if denominator else 0.0


def rerank_cross_encoder(
    query: str, candidates: list[dict], top_k: int = 5
) -> list[dict]:
    """Offline reranker combining token coverage and the retrieval score."""
    query_tokens = _tokens(query)
    reranked = []
    prior_scores = [float(item.get("score", 0)) for item in candidates]
    prior_max = max(prior_scores, default=0) or 1.0
    for candidate in candidates:
        overlap = len(query_tokens & _tokens(candidate.get("content", "")))
        coverage = overlap / max(len(query_tokens), 1)
        prior = float(candidate.get("score", 0)) / prior_max
        item = candidate.copy()
        item["score"] = float(0.75 * coverage + 0.25 * prior)
        reranked.append(item)
    return sorted(reranked, key=lambda item: item["score"], reverse=True)[:top_k]


def rerank_mmr(
    query_embedding: list[float],
    candidates: list[dict],
    top_k: int = 5,
    lambda_param: float = 0.7,
) -> list[dict]:
    """Select relevant and diverse candidates using MMR."""
    selected = []
    remaining = list(range(len(candidates)))
    while remaining and len(selected) < top_k:
        best_index = max(
            remaining,
            key=lambda index: (
                lambda_param * _cosine(query_embedding, candidates[index]["embedding"])
                - (1 - lambda_param)
                * max(
                    (
                        _cosine(
                            candidates[index]["embedding"],
                            candidates[selected_index]["embedding"],
                        )
                        for selected_index in selected
                    ),
                    default=0.0,
                )
            ),
        )
        selected.append(best_index)
        remaining.remove(best_index)
    return [candidates[index] for index in selected]


def rerank_rrf(
    ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60
) -> list[dict]:
    """Fuse multiple ranked lists with Reciprocal Rank Fusion."""
    scores = {}
    items = {}
    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):
            key = (
                item.get("metadata", {}).get("source"),
                item.get("metadata", {}).get("chunk_index"),
                item.get("content"),
            )
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
            items[key] = item
    results = []
    for key, score in sorted(scores.items(), key=lambda pair: pair[1], reverse=True)[:top_k]:
        item = items[key].copy()
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
        return rerank_rrf([candidates], top_k)
    if method == "mmr":
        raise ValueError("MMR requires query and candidate embeddings; call rerank_mmr")
    raise ValueError(f"Unknown rerank method: {method}")
