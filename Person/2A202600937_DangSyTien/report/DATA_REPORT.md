# Báo Cáo Dữ Liệu Thu Thập: Pháp Luật & Tin Tức Ma Tuý (Lab 8)

Báo cáo này tổng hợp thông tin chi tiết về các nguồn dữ liệu pháp luật (Task 1) và bài báo tin tức (Task 2) đã được tìm kiếm và lựa chọn để đưa vào hệ thống RAG Pipeline v2.

---

## 📁 1. Dữ Liệu Văn Bản Pháp Luật (Task 1 — Legal Documents)

Chúng ta đã xác định được **3 văn bản pháp luật chính thống** quy định chi tiết về phòng chống ma túy, cai nghiện và các chất cấm tại Việt Nam. Dưới đây là danh sách và đường dẫn tải xuống trực tiếp (PDF/Word):

| # | Tên Văn Bản | Cơ Quan Ban Hành | Số Hiệu & Ngày Ban Hành | Nội Dung Chính | Link Tải Trực Tiếp |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Luật Phòng, chống ma túy 2021** | Quốc hội Khóa XIV | `73/2021/QH14` <br> 30/03/2021 | Quy định chung về phòng chống ma túy, quản lý người sử dụng trái phép, các biện pháp cai nghiện và trách nhiệm liên quan. | [Tải về PDF](https://camau.gov.vn/wps/wcm/connect/91629853-2bdc-444a-be92-e4d6501c518b/tai-lieu-gioi-thieu-luat-phong-chong-ma-tuy-2021.pdf) |
| **2** | **Nghị định 105/2021/NĐ-CP** | Chính phủ | `105/2021/NĐ-CP` <br> 04/12/2021 | Hướng dẫn chi tiết thi hành Luật Phòng chống ma túy về kiểm soát các hoạt động hợp pháp liên quan và phối hợp điều tra. | [Tải về PDF](https://camau.gov.vn/sites/default/files/Ngh%E1%BB%8B%20%C4%91%E1%BB%8Bnh%20105.pdf) |
| **3** | **Nghị định 116/2021/NĐ-CP** | Chính phủ | `116/2021/NĐ-CP` <br> 21/12/2021 | Quy định chi tiết các điều của Luật về cai nghiện ma túy bắt buộc, cai nghiện tự nguyện và các chính sách hỗ trợ người cai nghiện. | [Tải về PDF](https://haiphong.gov.vn/sites/default/files/Nghi-dinh-116-2021-ND-CP.pdf) |

---

## 📰 2. Danh Sách Bài Báo Crawl Tin Tức Nghệ Sĩ (Task 2 — News Articles)

Để đáp ứng yêu cầu crawl tối thiểu **5 bài báo** về các nghệ sĩ Việt Nam liên quan tới ma túy, chúng ta sẽ sử dụng 5 đường dẫn chính thức từ hai tờ báo uy tín lớn nhất Việt Nam (**Tuổi Trẻ** và **VnExpress**):

### Danh sách 5 URL được chọn:
1.  **Bài báo về ca sĩ Chi Dân và người mẫu An Tây bị truy tố:**
    *   *Tiêu đề dự kiến:* Truy tố ca sĩ Chi Dân, người mẫu An Tây, KOL Trúc Phương vì ma túy.
    *   *Nguồn:* Báo Tuổi Trẻ.
    *   *URL:* `https://tuoitre.vn/truy-to-ca-si-chi-dan-nguoi-mau-an-tay-nguyen-do-truc-phuong-vi-ma-tuy-20241114112104523.htm`
2.  **Bài báo khởi tố người mẫu An Tây và KOL Trúc Phương:**
    *   *Tiêu đề dự kiến:* Khởi tố người mẫu An Tây và KOL Trúc Phương.
    *   *Nguồn:* Báo Tuổi Trẻ.
    *   *URL:* `https://tuoitre.vn/khoi-to-nguoi-mau-an-tay-va-kol-truc-phuong-20241113171804245.htm`
3.  **Bài báo về diễn viên Hữu Tín bị bắt vì sử dụng ma túy:**
    *   *Tiêu đề dự kiến:* Diễn viên Hữu Tín bị bắt vì dùng ma túy tại căn hộ chung cư.
    *   *Nguồn:* Báo VnExpress.
    *   *URL:* `https://vnexpress.net/dien-vien-huu-tin-bi-bat-vi-dung-ma-tuy-4475458.html`
4.  **Bài báo về ca sĩ Chu Bin bị bắt quả tang tổ chức sử dụng ma túy:**
    *   *Tiêu đề dự kiến:* Ca sĩ Chu Bin và nhiều người khác bị tạm giam vì tổ chức sử dụng ma túy.
    *   *Nguồn:* Báo Tuổi Trẻ.
    *   *URL:* `https://tuoitre.vn/ca-si-chu-bin-va-nhieu-nguoi-khac-bi-tam-giam-vi-to-chuc-su-dung-ma-tuy-20240614182402123.htm`
5.  **Bài báo về diễn viên Lệ Hằng (phim 'Xin hãy tin em') bị bắt vì mua bán ma túy:**
    *   *Tiêu đề dự kiến:* Diễn viên Lệ Hằng bị bắt quả tang vì mua bán ma túy trái phép.
    *   *Nguồn:* Báo VnExpress.
    *   *URL:* `https://vnexpress.net/dien-vien-le-hang-phim-xin-hay-tin-em-bi-bat-vi-mua-ban-ma-tuy-4591423.html`

---

## 🛠️ 3. Phương Án Triển Khai Tiếp Theo

1.  **Thực hiện tải tự động văn bản pháp luật (Task 1):**
    Tôi đã chuẩn bị sẵn một script tải tự động (`download_laws.py`) để tải toàn bộ 3 file PDF trên và lưu trực tiếp vào thư mục `data/landing/legal/` theo đúng tên tệp chuẩn hóa của Lab.
2.  **Cập nhật cấu hình crawl bài báo (Task 2):**
    Chúng ta sẽ ghi 5 đường dẫn tin tức trên vào danh sách `ARTICLE_URLS` trong tệp [src/task2_crawl_news.py](file:///c:/Users/Admin/Downloads/Day08_2A202600937_DangSyTien/src/task2_crawl_news.py), sau đó tiến hành viết hàm crawl.
3.  **Chuẩn hóa dữ liệu sang Markdown (Task 3):**
    Gọi module `MarkItDown` để chuyển đổi toàn bộ PDF của Luật và JSON của Tin tức vừa tải về thành các file Markdown phục vụ cho việc cắt nhỏ (Chunking) ở Task 4.
