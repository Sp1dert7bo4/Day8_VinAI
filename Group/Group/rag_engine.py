import os
from dotenv import load_dotenv

# Load variables if needed
load_dotenv()

# Import the core retrieval and generation modules
from src.task9_retrieval_pipeline import retrieve
from src.task10_generation import generate_with_citation

def query_rag(query: str, top_k: int = 5) -> dict:
    """
    Hàm wrapper chính cho RAG Engine.
    Các thành viên khác (đặc biệt là TV2 làm Chatbot UI) chỉ cần gọi hàm này.
    
    Args:
        query (str): Câu hỏi của người dùng.
        top_k (int): Số lượng tài liệu liên quan tối đa muốn lấy (mặc định: 5).
        
    Returns:
        dict: Chứa 'answer' (câu trả lời) và 'context' (các văn bản trích dẫn).
    """
    print(f"[RAG Engine] Đang xử lý câu hỏi: '{query}'...")
    # Vì task10_generation.py hiện đang gọi trực tiếp retrieve bên trong nó 
    # nên ta có thể gọi thẳng generate_with_citation.
    # Hàm này sẽ chạy chuỗi: Hybrid Search -> RRF -> Reranking -> LLM.
    
    try:
        result = generate_with_citation(query)
        return result
    except Exception as e:
        return {"answer": f"Lỗi từ RAG Engine: {str(e)}", "context": ""}

if __name__ == "__main__":
    # Test nhanh
    test_query = "Tội tàng trữ trái phép chất ma túy bị xử phạt như thế nào?"
    res = query_rag(test_query)
    print("\n--- KẾT QUẢ ---")
    print(res["answer"])
