import os
import json
from src.task10_generation import generate_with_citation

queries = [
    "Tội tàng trữ trái phép chất ma túy bị xử phạt như thế nào?",
    "Gần đây có vụ việc hay chuyên án nào bắt giữ tội phạm ma túy đáng chú ý không?"
]

results = []
for q in queries:
    print(f"Đang xử lý query: {q}")
    try:
        res = generate_with_citation(q)
        results.append({
            "query": q,
            "answer": res.get("answer", "No answer generated"),
            "context_length": len(res.get("context", "")),
        })
        print(f"-> Thành công")
    except Exception as e:
        print(f"-> Lỗi: {e}")

print("\n=== KẾT QUẢ ĐÁNH GIÁ ===")
for r in results:
    print(f"\nCâu hỏi: {r['query']}")
    print(f"Trả lời:\n{r['answer']}")
    print("-" * 50)
