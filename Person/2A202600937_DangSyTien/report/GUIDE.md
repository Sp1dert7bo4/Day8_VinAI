# Hướng Dẫn Thực Hành Chi Tiết: Triển Khai RAG Pipeline v2 (Lab 8)

Báo cáo này cung cấp hướng dẫn triển khai từng bước cho **10 nhiệm vụ cá nhân** và **bài tập nhóm** thuộc Lab 8. Làm theo tài liệu này sẽ giúp bạn hoàn thành tốt các phần việc và vượt qua bộ test kiểm thử tự động (`pytest`).

---

## 🚀 Bước 0: Thiết Lập Môi Trường Ban Đầu

1.  **Cài đặt các thư viện cần thiết:**
    Chạy lệnh sau tại thư mục gốc của dự án:
    ```bash
    pip install -r requirements.txt
    ```
    *(Các thư viện chính bao gồm: `crawl4ai`, `markitdown`, `langchain-text-splitters`, `sentence-transformers`, `weaviate-client` hoặc `chromadb`, `rank-bm25`, `pageindex`, `openai`, `deepeval` / `ragas`).*

2.  **Cấu hình API Keys:**
    Sao chép file `.env.example` thành `.env`:
    ```bash
    cp .env.example .env
    ```
    Mở file `.env` và cập nhật các khóa cần thiết:
    ```env
    OPENAI_API_KEY=your_openai_key
    GEMINI_API_KEY=your_gemini_key
    JINA_API_KEY=your_jina_reranker_key
    PAGEINDEX_API_KEY=your_pageindex_key
    WEAVIATE_URL=your_weaviate_cluster_url
    WEAVIATE_API_KEY=your_weaviate_api_key
    ```

---

## 📁 Giai Đoạn 1: Thu Thập & Chuẩn Hóa Dữ Liệu (Tasks 1 — 3)

### Task 1: Thu thập văn bản pháp luật về ma tuý
*   **File cần tác động:** Không cần sửa code, chỉ cần chuẩn bị dữ liệu.
*   **Việc cần làm:**
    1.  Tải **tối thiểu 3 file** văn bản pháp luật định dạng `.pdf` hoặc `.docx` về chủ đề ma túy hoặc chất cấm tại Việt Nam.
    2.  Lưu các file này vào thư mục: [data/landing/legal/](file:///c:/Users/Admin/Downloads/Day08_2A202600937_DangSyTien/data/landing/legal/).
*   **Gợi ý tài liệu:**
    *   *Luật Phòng, chống ma túy 2021* (luat-phong-chong-ma-tuy-2021.pdf)
    *   *Nghị định 105/2021/NĐ-CP* hướng dẫn thi hành luật (nghi-dinh-105-2021.pdf)
    *   *Nghị định 57/2022/NĐ-CP* ban hành danh mục chất ma túy (nghi-dinh-57-2022.docx)
*   **Yêu cầu kỹ thuật:** File tải về phải có kích thước lớn hơn **1 KB** để đảm bảo không bị rỗng.

### Task 2: Crawl bài báo tin tức bằng Crawl4AI
*   **File cần tác động:** [src/task2_crawl_news.py](file:///c:/Users/Admin/Downloads/Day08_2A202600937_DangSyTien/src/task2_crawl_news.py)
*   **Việc cần làm:**
    1.  Tìm **tối thiểu 5 bài báo** trực tuyến nói về các nghệ sĩ Việt Nam liên quan đến ma túy và điền URL vào biến `ARTICLE_URLS`.
    2.  Triển khai hàm `crawl_article(url)` sử dụng `AsyncWebCrawler` của Crawl4AI để cào nội dung bài báo và trả về metadata cùng content.
*   **Gợi ý mã nguồn triển khai:**
    ```python
    async def crawl_article(url: str) -> dict:
        from crawl4ai import AsyncWebCrawler
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            return {
                "url": url,
                "title": result.metadata.get("title") or "Tin tức nghệ sĩ liên quan ma tuý",
                "date_crawled": datetime.now().isoformat(),
                "content_markdown": result.markdown or ""
            }
    ```

### Task 3: Chuyển đổi định dạng sang Markdown bằng MarkItDown
*   **File cần tác động:** [src/task3_convert_markdown.py](file:///c:/Users/Admin/Downloads/Day08_2A202600937_DangSyTien/src/task3_convert_markdown.py)
*   **Việc cần làm:**
    1.  Hoàn thiện hàm `convert_legal_docs()`: Quét toàn bộ file trong `data/landing/legal/`, sử dụng `MarkItDown` để convert sang `.md`, lưu vào `data/standardized/legal/`.
    2.  Hoàn thiện hàm `convert_news_articles()`: Quét toàn bộ file `.json` trong `data/landing/news/`, trích xuất nội dung bài viết dạng Markdown và ghi vào file `.md` tương ứng trong `data/standardized/news/`.
*   **Gợi ý mã nguồn triển khai:**
    ```python
    def convert_legal_docs():
        legal_dir = LANDING_DIR / "legal"
        output_dir = OUTPUT_DIR / "legal"
        output_dir.mkdir(parents=True, exist_ok=True)
        md = MarkItDown()
        for filepath in legal_dir.iterdir():
            if filepath.suffix.lower() in (".pdf", ".docx", ".doc"):
                result = md.convert(str(filepath))
                output_path = output_dir / f"{filepath.stem}.md"
                output_path.write_text(result.text_content, encoding="utf-8")

    def convert_news_articles():
        news_dir = LANDING_DIR / "news"
        output_dir = OUTPUT_DIR / "news"
        output_dir.mkdir(parents=True, exist_ok=True)
        for filepath in news_dir.iterdir():
            if filepath.suffix.lower() == ".json":
                data = json.loads(filepath.read_text(encoding="utf-8"))
                output_path = output_dir / f"{filepath.stem}.md"
                header = f"# {data.get('title', 'Unknown')}\n\n**Source:** {data.get('url', 'N/A')}\n**Crawled:** {data.get('date_crawled', 'N/A')}\n\n---\n\n"
                content = header + data.get("content_markdown", "")
                output_path.write_text(content, encoding="utf-8")
    ```

---

## 🧠 Giai Đoạn 2: Chunking, Indexing & Retrieval Modules (Tasks 4 — 6)

### Task 4: Chunking & Indexing vào Vector Store
*   **File cần tác động:** [src/task4_chunking_indexing.py](file:///c:/Users/Admin/Downloads/Day08_2A202600937_DangSyTien/src/task4_chunking_indexing.py)
*   **Việc cần làm:**
    1.  Cấu hình kích thước chunk mong muốn (`CHUNK_SIZE`, `CHUNK_OVERLAP`) và giải thích lý do chọn trong ghi chú code.
    2.  Triển khai hàm `load_documents()` để đọc tất cả các file markdown đã được chuẩn hóa.
    3.  Triển khai hàm `chunk_documents(documents)` sử dụng `RecursiveCharacterTextSplitter`.
    4.  Triển khai hàm `embed_chunks(chunks)` sử dụng mô hình embedding (ví dụ: `BAAI/bge-m3` thông qua thư viện `sentence-transformers`).
    5.  Triển khai hàm `index_to_vectorstore(chunks)` để lưu các vector và metadata vào Vector DB (khuyên dùng Weaviate hoặc ChromaDB).
*   **Gợi ý mã nguồn triển khai:**
    ```python
    def load_documents() -> list[dict]:
        documents = []
        for md_file in STANDARDIZED_DIR.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            doc_type = "legal" if "legal" in str(md_file) else "news"
            documents.append({
                "content": content,
                "metadata": {"source": md_file.name, "type": doc_type}
            })
        return documents

    def chunk_documents(documents: list[dict]) -> list[dict]:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = []
        for doc in documents:
            splits = splitter.split_text(doc["content"])
            for i, chunk_text in enumerate(splits):
                chunks.append({
                    "content": chunk_text,
                    "metadata": {**doc["metadata"], "chunk_index": i}
                })
        return chunks
    ```

### Task 5: Xây dựng Module Semantic Search
*   **File cần tác động:** [src/task5_semantic_search.py](file:///c:/Users/Admin/Downloads/Day08_2A202600937_DangSyTien/src/task5_semantic_search.py)
*   **Việc cần làm:**
    1.  Nhận vào một chuỗi `query` và tham số giới hạn `top_k`.
    2.  Chuyển đổi `query` thành vector embedding bằng cùng mô hình đã dùng ở Task 4.
    3.  Thực hiện truy vấn độ tương đồng (Cosine Similarity) trên Vector DB và trả về danh sách các kết quả đã được sắp xếp giảm dần theo điểm tương đồng.
*   **Yêu cầu đầu ra:** Kết quả trả về phải là một `list[dict]` gồm các khóa `content`, `score`, và `metadata`.

### Task 6: Xây dựng Module Lexical Search (BM25)
*   **File cần tác động:** [src/task6_lexical_search.py](file:///c:/Users/Admin/Downloads/Day08_2A202600937_DangSyTien/src/task6_lexical_search.py)
*   **Việc cần làm:**
    1.  Thu thập toàn bộ kho dữ liệu văn bản (Corpus) từ tài liệu markdown hoặc Vector DB.
    2.  Khởi tạo chỉ mục BM25 sử dụng thư viện `rank-bm25`. Bạn nên viết tokenization tiếng Việt đơn giản (ví dụ dùng `split()` hoặc thư viện `underthesea`).
    3.  Tính toán điểm số BM25 cho câu truy vấn `query`, lọc lấy các kết quả có điểm số lớn hơn 0 và sắp xếp giảm dần theo điểm số để trả về.
*   **Gợi ý mã nguồn triển khai:**
    ```python
    def lexical_search(query: str, top_k: int = 10) -> list[dict]:
        tokenized_query = query.lower().split()
        scores = bm25_index.get_scores(tokenized_query)
        import numpy as np
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append({
                    "content": CORPUS[idx]["content"],
                    "score": float(scores[idx]),
                    "metadata": CORPUS[idx]["metadata"]
                })
        return results
    ```

---

## 🔀 Giai Đoạn 3: Reranking & Fallback RAG (Tasks 7 — 9)

### Task 7: Triển khai Module Reranking
*   **File cần tác động:** [src/task7_reranking.py](file:///c:/Users/Admin/Downloads/Day08_2A202600937_DangSyTien/src/task7_reranking.py)
*   **Việc cần làm:**
    Triển khai tối thiểu 1 trong 3 cơ chế rerank để tái sắp xếp thứ tự ưu tiên của danh sách ứng viên thu về:
    *   *Cách 1 (Khuyên dùng):* Gọi API **Jina Reranker v2** (`jina-reranker-v2-base-multilingual`) gửi kèm danh sách ứng viên để nhận điểm tương quan chính xác.
    *   *Cách 2:* Triển khai **MMR** (Maximal Marginal Relevance) để tối ưu hóa sự cân bằng giữa độ liên quan ngữ nghĩa và độ đa dạng nội dung (tránh trùng lặp thông tin).
    *   *Cách 3:* Triển khai **RRF** (Reciprocal Rank Fusion) để gộp thứ hạng từ kết quả của cả hai bộ tìm kiếm Semantic và Lexical.

### Task 8: Tích hợp PageIndex (Vectorless RAG)
*   **File cần tác động:** [src/task8_pageindex_vectorless.py](file:///c:/Users/Admin/Downloads/Day08_2A202600937_DangSyTien/src/task8_pageindex_vectorless.py)
*   **Việc cần làm:**
    1.  Đăng ký tài khoản trên trang chủ [pageindex.ai](https://pageindex.ai/) để lấy API Key.
    2.  Triển khai hàm `upload_documents()` để tải toàn bộ tài liệu đã chuẩn hóa lên hệ thống đám mây của PageIndex.
    3.  Triển khai hàm `pageindex_search(query, top_k)` thực hiện truy vấn trực tiếp thông qua PageIndex API để lấy thông tin. Đánh dấu nguồn dữ liệu bằng cờ `"source": "pageindex"`.

### Task 9: Xây dựng Pipeline Truy Xuất Hoàn Chỉnh (Có Fallback)
*   **File cần tác động:** [src/task9_retrieval_pipeline.py](file:///c:/Users/Admin/Downloads/Day08_2A202600937_DangSyTien/src/task9_retrieval_pipeline.py)
*   **Việc cần làm:**
    Kết hợp toàn bộ các module tìm kiếm lại với nhau để thực hiện luồng nghiệp vụ sau:
    1.  Nhận `query` đầu vào → Gọi song song **Semantic Search** và **Lexical Search**.
    2.  Gộp hai danh sách kết quả lại bằng thuật toán **RRF** (Reciprocal Rank Fusion) và gán nhãn `"source": "hybrid"`.
    3.  Chạy **Reranking** để lấy ra danh sách tối ưu nhất.
    4.  **Cơ chế Fallback:** Kiểm tra điểm tương đồng của kết quả tốt nhất (Top-1). Nếu điểm này nhỏ hơn ngưỡng `score_threshold` (ví dụ: `0.3`), hệ thống sẽ bỏ qua kết quả lai này và chuyển sang gọi **PageIndex Search** để làm dữ liệu dự phòng.
    5.  Trả về `top_k` kết quả cuối cùng.

---

## ✍️ Giai Đoạn 4: Sinh Câu Trả Lời Có Trích Dẫn (Task 10)

### Task 10: Tối ưu hóa prompt & Trích dẫn nguồn
*   **File cần tác động:** [src/task10_generation.py](file:///c:/Users/Admin/Downloads/Day08_2A202600937_DangSyTien/src/task10_generation.py)
*   **Việc cần làm:**
    1.  Triển khai hàm `reorder_for_llm(chunks)`: Sắp xếp lại danh sách tài liệu theo mô hình hình chuông (đưa các tài liệu có điểm số cao nhất ra hai biên: đầu và cuối danh sách, và đẩy tài liệu ít liên quan nhất vào giữa) nhằm khắc phục điểm yếu trí nhớ ngữ cảnh (*Lost in the Middle*) của LLM.
    2.  Triển khai hàm `format_context(chunks)`: Định dạng danh sách tài liệu thành chuỗi văn bản kèm theo ký hiệu nguồn cụ thể (ví dụ: `[Document 1 | Source: luat-phong-chong-ma-tuy.pdf]`).
    3.  Triển khai hàm `generate_with_citation(query)`: Thực hiện toàn bộ luồng RAG từ tìm kiếm tài liệu -> sắp xếp lại -> tạo prompt gửi lên LLM (OpenAI/Gemini) -> lấy câu trả lời kèm trích dẫn nguồn định dạng `[Nguồn, Năm]`.
*   **Yêu cầu an toàn chống ảo giác:** Nếu thông tin trong ngữ cảnh không đủ để trả lời câu hỏi, LLM buộc phải trả về câu trả lời mặc định: `"Tôi không thể xác minh thông tin này từ nguồn hiện có"`.

---

## 👥 Giai Đoạn 5: Triển Khai Bài Tập Nhóm (Group Project)

Hợp tác cùng các thành viên trong nhóm để thực hiện **1 trong 2 yêu cầu**:

### Lựa chọn 1: Xây dựng giao diện RAG Chatbot
1.  Tạo file ứng dụng giao diện (ví dụ `app.py` hoặc `main.py`).
2.  Sử dụng thư viện **Streamlit**, **Chainlit** hoặc **Gradio** để xây dựng khung chat.
3.  Tích hợp pipeline truy xuất từ `src/task9_retrieval_pipeline.py` và module sinh từ `src/task10_generation.py`.
4.  Cài đặt **Conversation Memory** để lưu trữ lịch sử trò chuyện giúp chatbot có thể hiểu các câu hỏi có tính liên đới ngữ cảnh.
5.  Thiết kế giao diện hiển thị các tài liệu gốc (source documents) một cách trực quan để người dùng kiểm chứng.

### Lựa chọn 2: Viết mã nguồn RAG Evaluation Pipeline
1.  **Thiết kế Golden Dataset:** Soạn thảo file [golden_dataset.json](file:///c:/Users/Admin/Downloads/Day08_2A202600937_DangSyTien/group_project/evaluation/golden_dataset.json) chứa tối thiểu 15 bộ câu hỏi/câu trả lời chuẩn mực được kiểm duyệt kỹ càng về mặt nội dung pháp luật.
2.  **Viết kịch bản đánh giá:** Hoàn thiện file [eval_pipeline.py](file:///c:/Users/Admin/Downloads/Day08_2A202600937_DangSyTien/group_project/evaluation/eval_pipeline.py) sử dụng một framework đánh giá như **DeepEval**, **RAGAS** hoặc **TruLens**. Đảm bảo đo lường đầy đủ 4 trục: *Faithfulness, Answer Relevance, Context Recall, Context Precision*.
3.  **Thực hiện kiểm thử A/B:** Chạy đánh giá trên ít nhất hai phiên bản hệ thống khác nhau để so sánh điểm số trung bình.
4.  **Báo cáo kết quả:** Cập nhật các thông số, bảng so sánh và phân tích nguyên nhân lỗi vào file [results.md](file:///c:/Users/Admin/Downloads/Day08_2A202600937_DangSyTien/group_project/evaluation/results.md).
