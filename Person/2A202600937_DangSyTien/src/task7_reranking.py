import os
import requests
from dotenv import load_dotenv

load_dotenv()
JINA_API_KEY = os.getenv("JINA_API_KEY")

def rerank_cross_encoder(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    """Uses Jina Reranker API to rerank candidates."""
    if not JINA_API_KEY:
        return sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)[:top_k]
        
    url = "https://api.jina.ai/v1/rerank"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {JINA_API_KEY}"
    }
    
    docs = [c["content"] for c in candidates]
    
    data = {
        "model": "jina-reranker-v2-base-multilingual",
        "query": query,
        "documents": docs,
        "top_n": top_k
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        res_json = response.json()
        
        results = []
        for item in res_json.get("results", []):
            idx = item["index"]
            score = item["relevance_score"]
            new_candidate = candidates[idx].copy()
            new_candidate["score"] = score
            results.append(new_candidate)
            
        return results
    except Exception as e:
        print(f"Jina Rerank error: {e}")
        # Fallback to returning original sorted if API fails
        return sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)[:top_k]

def rerank_rrf(lists_of_candidates: list[list[dict]], k: int = 60, top_n: int = 5) -> list[dict]:
    """Reciprocal Rank Fusion."""
    rrf_scores = {}
    content_map = {}
    
    for candidate_list in lists_of_candidates:
        for rank, candidate in enumerate(candidate_list):
            content = candidate["content"]
            if content not in rrf_scores:
                rrf_scores[content] = 0
                content_map[content] = candidate
            rrf_scores[content] += 1.0 / (k + rank + 1)
            
    # Sort by RRF score
    sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    
    results = []
    for content, score in sorted_items[:top_n]:
        item = content_map[content].copy()
        item["score"] = score
        results.append(item)
        
    return results

def rerank(query: str, candidates: list[dict], top_k: int = 5, method: str = "jina") -> list[dict]:
    """Main entry point for reranking."""
    if not candidates:
        return []
        
    if method == "jina" and JINA_API_KEY:
        return rerank_cross_encoder(query, candidates, top_k)
    else:
        sorted_candidates = sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)
        return sorted_candidates[:top_k]

if __name__ == "__main__":
    candidates = [
        {"content": "Tội tàng trữ ma tuý", "score": 0.8, "metadata": {}},
        {"content": "Nghệ sĩ bị bắt vì ma tuý", "score": 0.6, "metadata": {}},
        {"content": "Python programming", "score": 0.4, "metadata": {}},
    ]
    res = rerank("ma tuý", candidates, top_k=2)
    print("Reranked:", res)
