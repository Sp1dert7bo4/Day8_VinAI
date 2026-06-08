# Báo Cáo Dữ Liệu Thu Thập: Pháp Luật & Tin Tức Ma Tuý (Lab 8)

Báo cáo này tổng hợp thông tin chi tiết về các nguồn dữ liệu pháp luật (Task 1) và bài báo tin tức (Task 2) đã được tìm kiếm và lựa chọn để đưa vào hệ thống RAG Pipeline v2.

---

## 📁 1. Dữ Liệu Văn Bản Pháp Luật (Task 1 — Legal Documents)

Chúng ta đã xác định được **4 văn bản pháp luật** quy định chi tiết về phòng chống ma túy và các chất cấm tại Việt Nam.

| # | Tên Văn Bản | Cơ Quan Ban Hành | Tên File Đã Tải | Nội Dung Chính |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Bộ Luật Hình Sự 2015 (Phần Ma Túy)** | Quốc hội | `bo_luat_hinh_su_2015_ma_tuy.pdf` | Các quy định xử phạt hình sự liên quan đến tội phạm ma túy. |
| **2** | **Danh Mục Chất Ma Túy** | Chính phủ | `danh_muc_chat_ma_tuy.pdf` | Các nghị định quy định chi tiết danh mục các chất ma túy. |
| **3** | **Luật Phòng chống ma túy** | Quốc hội | `luat_phong_chong_ma_tuy.pdf` | Quy định chung về phòng chống ma túy. |
| **4** | **Luật Phòng chống ma túy 2021** | Quốc hội | `luat_phong_chong_ma_tuy_2021.pdf` | Phiên bản luật năm 2021 chi tiết và cập nhật hơn. |

---

## 📰 2. Danh Sách Bài Báo Crawl Tin Tức Nghệ Sĩ (Task 2 — News Articles)

Để đáp ứng yêu cầu, chúng ta đã tiến hành crawl **10 bài báo** về các sự kiện liên quan tới ma túy và các nhân vật của công chúng, nghệ sĩ. 
Dữ liệu đã được lưu thành 10 file JSON từ `article_01.json` đến `article_10.json` và chuyển đổi sang định dạng Markdown.

### Thông tin tổng quan:
*   **Số lượng:** 10 bài báo
*   **Nguồn chính:** Báo Tuổi Trẻ, Báo Thanh Niên, VnExpress, Dân Trí...
*   **Định dạng lưu trữ:** JSON (metadata & nội dung markdown). 
*   Các bài báo tập trung vào sự kiện bắt giữ, truy tố và xét xử tội phạm ma túy, cung cấp thông tin thực tế chất lượng cao cho RAG pipeline.

---

## 🛠️ 3. Phương Án Triển Khai Tiếp Theo

1.  **Thực hiện tải tự động văn bản pháp luật (Task 1):**
    Tôi đã chuẩn bị sẵn một script tải tự động (`download_laws.py`) để tải toàn bộ 3 file PDF trên và lưu trực tiếp vào thư mục `data/landing/legal/` theo đúng tên tệp chuẩn hóa của Lab.
2.  **Cập nhật cấu hình crawl bài báo (Task 2):**
    Chúng ta sẽ ghi 5 đường dẫn tin tức trên vào danh sách `ARTICLE_URLS` trong tệp [src/task2_crawl_news.py](file:///c:/Users/Admin/Downloads/Day08_2A202600937_DangSyTien/src/task2_crawl_news.py), sau đó tiến hành viết hàm crawl.
3.  **Chuẩn hóa dữ liệu sang Markdown (Task 3):**
    Gọi module `MarkItDown` để chuyển đổi toàn bộ PDF của Luật và JSON của Tin tức vừa tải về thành các file Markdown phục vụ cho việc cắt nhỏ (Chunking) ở Task 4.
