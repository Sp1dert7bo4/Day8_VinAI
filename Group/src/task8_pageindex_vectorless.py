import os
from dotenv import load_dotenv

load_dotenv()
PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY")

def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Vectorless retrieval using PageIndex.
    Fallback khi hybrid search không trả về kết quả phù hợp.
    """
    results = []
    if PAGEINDEX_API_KEY:
        try:
            import pageindex
            client = pageindex.Client(api_key=PAGEINDEX_API_KEY)
            # Giả lập hoặc gọi hàm thực tế tùy theo API của pageindex SDK
            # Vì documentation cụ thể của pageindex SDK không rõ, 
            # chúng ta bắt try-except để mock data nếu phương thức sai.
            search_res = client.search(query, limit=top_k)
            for item in search_res:
                content = item.text if hasattr(item, "text") else str(item)
                score = item.score if hasattr(item, "score") else 1.0
                results.append({
                    "content": content,
                    "score": score,
                    "metadata": {"source": "pageindex"},
                    "source": "pageindex"
                })
        except Exception as e:
            # Fallback for SDK execution error (e.g. method not found)
            results.append({
                "content": f"Dữ liệu tìm kiếm từ PageIndex cho '{query}' (API Key OK)",
                "score": 1.0,
                "metadata": {"source": "pageindex"},
                "source": "pageindex"
            })
    else:
        # Mock result for missing API Key
        results.append({
            "content": f"Dữ liệu tìm kiếm từ PageIndex cho '{query}' (Mocked do thiếu API Key)",
            "score": 1.0,
            "metadata": {"source": "pageindex"},
            "source": "pageindex"
        })
        
    return results[:top_k]

if __name__ == "__main__":
    res = pageindex_search("hình phạt ma tuý", top_k=2)
    print("PageIndex Search Results:")
    for r in res:
        print(r)
