# Bài Tập Nhóm - Core RAG Engine

Chào các bạn, mình là **Đặng Sỹ Tiến (Thành viên 1)** phụ trách phần Core RAG Engine Integrator.

Thư mục `Group/` này chứa toàn bộ các file cốt lõi cần thiết để hệ thống RAG hoạt động hoàn chỉnh mà không cần cài đặt lại từ đầu. Mình đã xây dựng xong toàn bộ đường ống truy xuất (retrieval) và tạo sinh (generation) với cơ chế tìm kiếm lai (Hybrid Search) và Fallback thông minh.

---

## 🛠 Cấu trúc thư mục

- **`data/`**: Chứa toàn bộ cơ sở dữ liệu đã thu thập (bao gồm 4 văn bản luật và 10 tin tức thật), đồng thời đã lưu trữ sẵn trong Vector Database (ChromaDB) ở mục `data/chroma_db/`. Các bạn **không cần** chạy lại script load/chunk data.
- **`src/`**: Chứa các script từ task 4 đến task 10 (Chunking, Semantic/Lexical Search, Reranking bằng Jina, Generation bằng Gemini).
- **`.env`**: File biến môi trường chứa API Key.
- **`requirements.txt`**: Danh sách thư viện bắt buộc.
- **`rag_engine.py`**: **File quan trọng nhất!** Đây là Wrapper (cầu nối) mình viết riêng để nhóm dễ dàng sử dụng.

---

## 🚀 Hướng dẫn sử dụng cho Team

Để thuận tiện cho việc code UI (TV2) và code phần Evaluation (TV3), mình đã đóng gói mọi thứ vào file `rag_engine.py`.

Các bạn chỉ cần import hàm `query_rag` và sử dụng như sau:

```python
from Group.rag_engine import query_rag

# Đặt câu hỏi
cau_hoi = "Tội tàng trữ trái phép chất ma túy bị xử phạt như thế nào?"

# Gọi hệ thống RAG xử lý
ket_qua = query_rag(cau_hoi, top_k=5)

# In kết quả
print("Câu trả lời:", ket_qua["answer"])
print("Trích dẫn nguồn:", ket_qua["context"])
```

### Phân công công việc tiếp theo:
1. **Thành viên 2 (UI):** Dùng `Streamlit` tạo giao diện chatbot đơn giản. Import hàm `query_rag` ở trên để lấy câu trả lời hiển thị cho người dùng.
2. **Thành viên 3 (Eval):** Dùng `DeepEval` hoặc `Ragas` đọc file `golden_dataset.json`, loop qua từng câu hỏi, dùng `query_rag` lấy câu trả lời thực tế rồi so sánh với đáp án chuẩn.
3. **Thành viên 4 (DevOps):** Chuẩn bị Notebook demo tổng hợp và Slides báo cáo.

Nếu code báo lỗi thiếu module, nhớ chạy `pip install -r Group/requirements.txt`.
Chúc nhóm hoàn thành tốt bài!
