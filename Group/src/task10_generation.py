import os
import openai
from dotenv import load_dotenv
from src.task9_retrieval_pipeline import retrieve

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1")
MODEL_NAME = os.getenv("LLM_MODEL", "google/gemini-2.5-flash")

def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """
    Sắp xếp chunks theo mô hình hình chuông (Lost in the Middle).
    Quan trọng nhất ở đầu và cuối, ít quan trọng ở giữa.
    """
    if not chunks:
        return []
    
    reordered = [None] * len(chunks)
    left, right = 0, len(chunks) - 1
    for i, chunk in enumerate(chunks):
        if i % 2 == 0:
            reordered[left] = chunk
            left += 1
        else:
            reordered[right] = chunk
            right -= 1
    return reordered

def format_context(chunks: list[dict]) -> str:
    """
    Chuẩn hóa bối cảnh gửi cho LLM hiển thị rõ xuất xứ của từng văn bản.
    """
    context_str = ""
    for i, chunk in enumerate(chunks):
        source = chunk.get("metadata", {}).get("source", f"Unknown_{i}")
        content = chunk.get("content", "")
        context_str += f"\n--- Source: {source} ---\n{content}\n"
    return context_str.strip()

def generate_with_citation(query: str) -> dict:
    """
    Thực hiện RAG pipeline, gọi LLM, trả về câu trả lời có trích dẫn.
    """
    chunks = retrieve(query, top_k=5)
    reordered_chunks = reorder_for_llm(chunks)
    context = format_context(reordered_chunks)
    
    system_prompt = (
        "Bạn là một trợ lý pháp lý AI. Hãy trả lời câu hỏi của người dùng dựa trên "
        "các tài liệu tham khảo được cung cấp bên dưới. Nếu có sử dụng thông tin, "
        "hãy luôn ghi chú trích dẫn rõ ràng [Source: <tên_nguồn>]. "
        "Nếu tài liệu không chứa thông tin để trả lời, hãy trả lời rằng "
        "tài liệu hiện tại không đề cập đến vấn đề này."
    )
    
    user_prompt = f"Tài liệu tham khảo:\n{context}\n\nCâu hỏi: {query}"
    
    if not OPENAI_API_KEY:
        # Fallback for testing environment without API key
        return {"answer": "Mocked answer for testing. Source: [Unknown]"}
        
    try:
        client = openai.OpenAI(
            base_url=OPENAI_API_BASE,
            api_key=OPENAI_API_KEY,
        )
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=1024
        )
        answer = response.choices[0].message.content
        return {"answer": answer, "context": context}
    except Exception as e:
        return {"answer": f"Lỗi trong quá trình tạo sinh (LLM): {str(e)}"}

if __name__ == "__main__":
    q = "Hình phạt đối với tội tàng trữ ma tuý là gì?"
    print(f"Query: {q}")
    res = generate_with_citation(q)
    print("\n--- Answer ---")
    print(res["answer"])
