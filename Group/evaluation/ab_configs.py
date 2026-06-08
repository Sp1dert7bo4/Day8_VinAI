"""A/B configurations for the group RAG evaluation.

TV4 owns these experiment settings. The core RAG engine should expose a
`retrieve(query, top_k, score_threshold, use_reranking)` function; if it does not
yet support one option, the runner falls back gracefully and records the issue.
"""

AB_CONFIGS = {
    "A_hybrid_with_rerank": {
        "description": "Hybrid retrieval with reranking enabled.",
        "top_k": 5,
        "score_threshold": 0.30,
        "use_reranking": True,
    },
    "B_hybrid_without_rerank": {
        "description": "Hybrid retrieval with reranking disabled.",
        "top_k": 5,
        "score_threshold": 0.30,
        "use_reranking": False,
    },
}

