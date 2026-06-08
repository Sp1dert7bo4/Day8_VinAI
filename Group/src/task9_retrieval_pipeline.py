from src.task5_semantic_search import semantic_search
from src.task6_lexical_search import lexical_search
from src.task7_reranking import rerank, rerank_rrf
from src.task8_pageindex_vectorless import pageindex_search

def retrieve(query: str, top_k: int = 5, score_threshold: float = 0.01) -> list[dict]:
    """
    1. Chạy semantic_search + lexical_search
    2. Merge kết quả (RRF)
    3. Rerank (Jina)
    4. Nếu top result score < threshold -> fallback PageIndex
    5. Return top_k results
    """
    # 1. Hybrid Search (Semantic + Lexical)
    sem_results = semantic_search(query, top_k=top_k*2)
    lex_results = lexical_search(query, top_k=top_k*2)
    
    # 2. Merge using Reciprocal Rank Fusion
    if sem_results or lex_results:
        fused = rerank_rrf([sem_results, lex_results], top_n=top_k*2)
        
        # 3. Rerank
        reranked = rerank(query, fused, top_k=top_k)
    else:
        reranked = []
        
    # Mark source as hybrid
    for r in reranked:
        r["source"] = "hybrid"
        
    # 4. Fallback Logic
    # Nếu kết quả rỗng hoặc max score < score_threshold
    max_score = reranked[0].get("score", 0) if reranked else 0
    if not reranked or max_score < score_threshold:
        print(f"Hybrid search score ({max_score:.4f}) < threshold ({score_threshold}). Fallback to PageIndex.")
        pageindex_results = pageindex_search(query, top_k=top_k)
        return pageindex_results
        
    # 5. Return Top K
    return reranked[:top_k]

if __name__ == "__main__":
    query = "quy định xử phạt ma tuý"
    print(f"Query: {query}")
    results = retrieve(query, top_k=2)
    for i, r in enumerate(results):
        print(f"\n--- Result {i+1} (Score: {r.get('score', 0):.4f}, Source: {r.get('source')}) ---")
        print(r['content'][:200].replace('\n', ' ') + "...")
