"""
Task 2 — Crawl bài báo về nghệ sĩ liên quan tới ma tuý.

Hướng dẫn:
    1. Crawl tối thiểu 5 bài báo từ các trang tin tức Việt Nam.
    2. Sử dụng Crawl4AI hoặc thư viện crawling tương tự.
    3. Lưu output vào data/landing/news/
    4. Mỗi bài lưu 1 file JSON với metadata (url, title, date_crawled, content).

Cài đặt:
    pip install crawl4ai
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from crawl4ai import AsyncWebCrawler

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"


def setup_directory():
    """Tạo thư mục data/landing/news/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# TODO: Điền danh sách URL bài báo cần crawl
ARTICLE_URLS = [
    # Ví dụ:
     "https://tuoitre.vn/rapper-binh-gold-bi-bat-vi-cuop-tai-san-duong-tinh-voi-ma-tuy-20250726185902989.htm",
     "https://tienphong.vn/cu-soc-miu-le-bi-bat-va-su-dang-so-cua-ma-tuy-post1842827.tpo",
     "https://vietnamnet.vn/de-nghi-truy-to-ca-si-chi-dan-cung-anh-trai-vi-to-chuc-su-dung-ma-tuy-2434484.html",
     "https://tuoitre.vn/bat-nguoi-mau-an-tay-ca-si-chi-dan-co-tien-truc-phuong-do-lien-quan-ma-tuy-20241114114826655.htm",
     'https://vietnamnet.vn/nam-ca-si-long-nhat-vua-bi-khoi-to-bat-tam-giam-vi-ma-tuy-2517561.html',
]


async def crawl_article(url: str) -> dict:
    """Crawl một bài báo và trả về nội dung cùng metadata."""
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        if not result.success:
            raise RuntimeError(f"Crawl thất bại: {result.error_message}")

        title = result.metadata.get("title", "Unknown") if result.metadata else "Unknown"
        content = result.markdown.raw_markdown if hasattr(
            result.markdown, "raw_markdown"
        ) else str(result.markdown)

        return {
            "url": url,
            "title": title,
            "date_crawled": datetime.now().isoformat(),
            "content_markdown": content,
        }


async def crawl_all():
    """Crawl toàn bộ bài báo trong ARTICLE_URLS."""
    setup_directory()

    for i, url in enumerate(ARTICLE_URLS, 1):
        print(f"[{i}/{len(ARTICLE_URLS)}] Crawling: {url}")
        article = await crawl_article(url)

        # Lưu file JSON
        filename = f"article_{i:02d}.json"
        filepath = DATA_DIR / filename
        filepath.write_text(
            json.dumps(article, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"  ✓ Saved: {filepath}")


if __name__ == "__main__":
    if not ARTICLE_URLS:
        print("⚠ Hãy điền ARTICLE_URLS trước khi chạy!")
        print("Gợi ý: tìm bài báo trên VnExpress, Tuổi Trẻ, Thanh Niên, ...")
    else:
        asyncio.run(crawl_all())
