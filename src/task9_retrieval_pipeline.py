"""Task 9: hybrid retrieval with reranking and vectorless fallback."""

from concurrent.futures import ThreadPoolExecutor

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank, rerank_rrf
from .task8_pageindex_vectorless import pageindex_search

SCORE_THRESHOLD = 0.3
DEFAULT_TOP_K = 5
RERANK_METHOD = "cross_encoder"


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """Run dense and lexical retrieval, fuse, rerank and fallback."""
    if not query.strip() or top_k <= 0:
        return []
    candidate_count = max(top_k * 2, 10)
    with ThreadPoolExecutor(max_workers=2) as executor:
        dense_future = executor.submit(semantic_search, query, candidate_count)
        sparse_future = executor.submit(lexical_search, query, candidate_count)
        dense_results = dense_future.result()
        sparse_results = sparse_future.result()

    merged = rerank_rrf([dense_results, sparse_results], candidate_count)
    for item in merged:
        item["source"] = "hybrid"
    final_results = (
        rerank(query, merged, top_k, RERANK_METHOD)
        if use_reranking and merged
        else merged[:top_k]
    )
    if not final_results or final_results[0]["score"] < score_threshold:
        return pageindex_search(query, top_k)
    return final_results[:top_k]


if __name__ == "__main__":
    for result in retrieve("hình phạt tàng trữ trái phép chất ma tuý", 3):
        print(f"[{result['score']:.3f}] [{result['source']}] {result['content'][:100]}")
