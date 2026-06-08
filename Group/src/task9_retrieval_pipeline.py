from src.task5_semantic_search import semantic_search
from src.task6_lexical_search import lexical_search
from src.task7_reranking import rerank, rerank_rrf
from src.task8_pageindex_vectorless import pageindex_search

def retrieve(query: str, top_k: int = 5, score_threshold: float = 0.01, use_hybrid: bool = True, use_reranker: bool = True) -> list[dict]:
    """
    1. Chạy semantic_search (+ lexical_search nếu use_hybrid=True)
    2. Merge kết quả bằng RRF (nếu use_hybrid)
    3. Rerank (nếu use_reranker)
    4. Nếu top result score < threshold -> fallback PageIndex
    5. Return top_k results
    """
    fetch_k = top_k * 2 if use_reranker else top_k
    
    # 1. Semantic Search
    sem_results = semantic_search(query, top_k=fetch_k)
    
    # 2. Hybrid (nếu bật)
    if use_hybrid:
        lex_results = lexical_search(query, top_k=fetch_k)
        if sem_results or lex_results:
            candidates = rerank_rrf([sem_results, lex_results], top_n=fetch_k)
        else:
            candidates = []
    else:
        candidates = sem_results
        
    # 3. Rerank (nếu bật)
    if use_reranker and candidates:
        reranked = rerank(query, candidates, top_k=top_k)
    else:
        reranked = candidates[:top_k]
        
    # Mark source as hybrid or dense
    source_tag = "hybrid" if use_hybrid else "dense"
    for r in reranked:
        r["source"] = source_tag
        
    # 4. Fallback Logic
    max_score = reranked[0].get("score", 0) if reranked else 0
    if not reranked or (max_score < score_threshold and use_reranker):
        print(f"Retrieval score ({max_score:.4f}) < threshold ({score_threshold}). Fallback to PageIndex.")
        pageindex_results = pageindex_search(query, top_k=top_k)
        return pageindex_results
        
    # 5. Return Top K
    return reranked

if __name__ == "__main__":
    query = "quy định xử phạt ma tuý"
    print(f"Query: {query}")
    results = retrieve(query, top_k=2)
    for i, r in enumerate(results):
        print(f"\n--- Result {i+1} (Score: {r.get('score', 0):.4f}, Source: {r.get('source')}) ---")
        print(r['content'][:200].replace('\n', ' ') + "...")
