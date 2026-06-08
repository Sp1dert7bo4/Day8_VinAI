"""
Task 9 - Complete retrieval pipeline.

Pipeline:
1. Semantic search
2. Lexical/BM25 search
3. Merge with Reciprocal Rank Fusion
4. Rerank
5. Fallback to PageIndex-style vectorless search when results are weak
"""

try:
    from .task5_semantic_search import semantic_search
    from .task6_lexical_search import lexical_search
    from .task7_reranking import rerank, rerank_rrf
    from .task8_pageindex_vectorless import pageindex_search
except ImportError:
    from task5_semantic_search import semantic_search
    from task6_lexical_search import lexical_search
    from task7_reranking import rerank, rerank_rrf
    from task8_pageindex_vectorless import pageindex_search


SCORE_THRESHOLD = 0.3
DEFAULT_TOP_K = 5
RERANK_METHOD = "cross_encoder"


def _mark_source(results: list[dict], source: str) -> list[dict]:
    marked = []
    for item in results:
        copy = item.copy()
        copy["source"] = source
        marked.append(copy)
    return marked


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """
    Retrieve relevant chunks with hybrid search and fallback.

    Returns:
        List of {'content': str, 'score': float, 'metadata': dict, 'source': str}
    """
    if top_k <= 0:
        return []

    dense_results = semantic_search(query, top_k=top_k * 3)
    sparse_results = lexical_search(query, top_k=top_k * 3)

    merged = rerank_rrf([dense_results, sparse_results], top_k=top_k * 3)
    merged = _mark_source(merged, "hybrid")

    if use_reranking and merged:
        final_results = rerank(query, merged, top_k=top_k, method=RERANK_METHOD)
        final_results = _mark_source(final_results, "hybrid")
    else:
        final_results = merged[:top_k]

    best_score = final_results[0]["score"] if final_results else 0.0
    if not final_results or best_score < score_threshold:
        return pageindex_search(query, top_k=top_k)

    return final_results[:top_k]


if __name__ == "__main__":
    for query in [
        "Hinh phat cho toi tang tru trai phep chat ma tuy",
        "Nghe si nao bi bat vi ma tuy",
    ]:
        print(f"\nQuery: {query}")
        for i, result in enumerate(retrieve(query, top_k=3), 1):
            print(f"{i}. [{result['score']:.3f}] [{result['source']}] {result['content'][:80]}...")
