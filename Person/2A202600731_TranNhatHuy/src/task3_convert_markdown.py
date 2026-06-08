"""
Task 3 — Convert toàn bộ file trong data/landing/ thành Markdown.

Sử dụng MarkItDown của Microsoft:
    https://github.com/microsoft/markitdown

Cài đặt:
    pip install markitdown

Hướng dẫn:
    1. Scan toàn bộ file trong data/landing/ (PDF, DOCX, JSON)
    2. Convert sang Markdown
    3. Lưu vào data/standardized/ giữ nguyên cấu trúc thư mục
"""

import json
import sys
from pathlib import Path

from markitdown import MarkItDown

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def _conversion_text(result) -> str:
    """Lấy nội dung từ các phiên bản MarkItDown cũ và mới."""
    text = getattr(result, "text_content", None)
    if text is None:
        text = getattr(result, "markdown", None)
    if not text or not text.strip():
        raise ValueError("MarkItDown returned no text content")
    return text.strip()


def convert_legal_docs() -> tuple[int, list[str]]:
    """Convert PDF/DOCX files trong data/landing/legal/ sang markdown."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    md = MarkItDown()
    converted = 0
    errors = []

    for filepath in sorted(legal_dir.iterdir()):
        if filepath.suffix.lower() in (".pdf", ".docx", ".doc"):
            print(f"Converting: {filepath.name}")
            try:
                result = md.convert(str(filepath))
                content = _conversion_text(result)
                output_path = output_dir / f"{filepath.stem}.md"
                output_path.write_text(content + "\n", encoding="utf-8")
                converted += 1
                print(f"  Saved: {output_path}")
            except Exception as exc:
                message = f"{filepath.name}: {exc}"
                errors.append(message)
                print(f"  Skipped: {message}")

    return converted, errors


def convert_news_articles() -> tuple[int, list[str]]:
    """Convert JSON crawled articles trong data/landing/news/ sang markdown."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)
    converted = 0
    errors = []

    for filepath in sorted(news_dir.iterdir()):
        if filepath.suffix.lower() == ".json":
            print(f"Converting: {filepath.name}")
            try:
                data = json.loads(filepath.read_text(encoding="utf-8"))
                article_content = data.get("content_markdown") or data.get("content") or ""
                if not article_content.strip():
                    raise ValueError("JSON không có content_markdown/content")

                output_path = output_dir / f"{filepath.stem}.md"
                header = (
                    f"# {data.get('title', 'Unknown')}\n\n"
                    f"**Source:** {data.get('url', 'N/A')}\n\n"
                    f"**Crawled:** {data.get('date_crawled', 'N/A')}\n\n"
                    "---\n\n"
                )
                output_path.write_text(header + article_content.strip() + "\n", encoding="utf-8")
                converted += 1
                print(f"  Saved: {output_path}")
            except Exception as exc:
                message = f"{filepath.name}: {exc}"
                errors.append(message)
                print(f"  Skipped: {message}")

    return converted, errors


def convert_all():
    """Convert toàn bộ files."""
    print("=" * 50)
    print("Task 3: Convert to Markdown (MarkItDown)")
    print("=" * 50)

    print("\n--- Legal Documents ---")
    legal_count, legal_errors = convert_legal_docs()

    print("\n--- News Articles ---")
    news_count, news_errors = convert_news_articles()

    print(f"\nDone! Converted {legal_count} legal docs and {news_count} news articles.")
    print("Output tại:", OUTPUT_DIR)

    errors = legal_errors + news_errors
    if errors:
        print("\nFiles chưa convert được:")
        for error in errors:
            print(f"  - {error}")


if __name__ == "__main__":
    convert_all()
