# Báo cáo kết quả RAG Evaluation

Báo cáo này trình bày kết quả đánh giá tự động (Automated Evaluation) sử dụng framework **DeepEval** trên bộ Golden Dataset gồm 33 cặp câu hỏi - đáp án.

---

## 1. Kết quả Tổng hợp (A/B Testing)

Chúng tôi thực hiện so sánh 2 cấu hình (Configurations) của hệ thống RAG:
- **Config A**: Hybrid Search (Semantic + Lexical) + Jina Reranker
- **Config B**: Dense Only (Chỉ Semantic Search), Không dùng Reranker

| Metric | Config A (Hybrid + Reranker) | Config B (Dense Only) |
|--------|------------------------------|-----------------------|
| **Faithfulness** | 1.000 | 1.000 |
| **Answer Relevancy** | 0.852 | 0.654 |
| **Context Recall** | 0.848 | 0.666 |
| **Context Precision** | 0.583 | 0.359 |

**Nhận xét chung:**
- **Config A** vượt trội hoàn toàn so với Config B trên các chỉ số truy xuất (`Context Recall` và `Context Precision`). Điều này chứng tỏ việc kết hợp BM25 và Jina Reranker giúp tìm kiếm chính xác và đầy đủ các tài liệu pháp luật/tin tức hơn hẳn so với chỉ dùng vector.
- Câu trả lời của cả 2 cấu hình đều đạt độ trung thực tuyệt đối (`Faithfulness = 1.0`), cho thấy LLM tuân thủ chặt chẽ tài liệu cung cấp và không bịa thông tin.

---

## 2. Phân tích Worst Performers (Các trường hợp tệ nhất)

**Câu hỏi**: "Những nghệ sĩ nào bị truy tố cùng Chi Dân?"
- **Kết quả trả về**: Hệ thống đôi khi không liệt kê được đầy đủ "An Tây" và "Trúc Phương" nếu các bài báo bị cắt nhỏ (chunking) quá đà khiến tên các nhân vật nằm ở các chunk khác nhau.
- **Phân tích lỗi**: Do `Context Precision` đôi lúc bị giảm nếu chunk chứa đáp án nằm ở vị trí thứ 4 hoặc 5 trong kết quả trả về, khiến LLM lặp lại thiếu sót.
- **Đề xuất cải tiến**: Tăng `chunk_size` hoặc sử dụng Parent-Child Document Retrieval để giữ trọn vẹn ngữ cảnh của bài báo dài.

**Câu hỏi**: "Điều kiện để được hoãn chấp hành án phạt tù đối với phụ nữ có thai?"
- **Kết quả trả về**: Thiếu một số điều kiện ràng buộc ngách.
- **Phân tích lỗi**: Do `Context Recall` của văn bản pháp luật bị nhiễu với các điều luật khác có từ vựng tương tự.
- **Đề xuất cải tiến**: Áp dụng Metadata Filtering (lọc theo metadata loại tài liệu `legal` vs `news`) trước khi chạy Semantic Search.

---
*Báo cáo được tạo tự động bởi Evaluation Pipeline của nhóm.*
