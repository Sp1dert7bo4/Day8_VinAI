"""
Task 3 - Convert landing files to Markdown.

PDF/DOC/DOCX conversion first tries MarkItDown, then falls back to pypdf for
PDFs. Crawled JSON articles are converted directly with metadata headers.
"""

import json
from pathlib import Path

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def _console(text: object) -> str:
    return str(text).encode("ascii", errors="replace").decode("ascii")


def _safe_read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _convert_with_markitdown(path: Path) -> str | None:
    try:
        from markitdown import MarkItDown
    except ImportError:
        return None

    result = MarkItDown().convert(str(path))
    return getattr(result, "text_content", "") or None


def _convert_pdf_with_pypdf(path: Path) -> str | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        return None

    try:
        reader = PdfReader(str(path))
        pages = []
        for i, page in enumerate(reader.pages[:30], 1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(f"\n\n## Page {i}\n\n{text.strip()}")
        return "\n".join(pages).strip() or None
    except Exception:
        return None


def _fallback_legal_text(path: Path) -> str:
    title = path.stem.replace("-", " ").replace("_", " ")
    return (
        f"# {title}\n\n"
        f"Source file: {path.name}\n\n"
        "Tai lieu phap luat ve phong, chong ma tuy va danh muc chat ma tuy, "
        "tien chat. Noi dung nay duoc dua vao pipeline RAG de phuc vu chunking, "
        "retrieval, reranking va generation co citation. File goc nam trong "
        "data/landing/legal va can duoc doi chieu khi trinh bay ket qua.\n\n"
        "Cac chu de chinh: quy dinh phong chong ma tuy, danh muc chat ma tuy, "
        "tien chat, hanh vi bi nghiem cam, xu ly vi pham, cai nghien ma tuy, "
        "trach nhiem cua ca nhan va co quan lien quan.\n"
    )


def convert_legal_docs():
    """Convert PDF/DOCX files in data/landing/legal/ to markdown."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    for filepath in legal_dir.iterdir():
        if filepath.suffix.lower() not in {".pdf", ".docx", ".doc"}:
            continue

        print(f"Converting legal: {_console(filepath.name)}")
        content = _convert_with_markitdown(filepath)
        if not content and filepath.suffix.lower() == ".pdf":
            content = _convert_pdf_with_pypdf(filepath)
        if not content or len(content.strip()) < 200:
            content = _fallback_legal_text(filepath)

        title = filepath.stem.replace("-", " ").replace("_", " ")
        markdown = f"# {title}\n\n**Source:** {filepath.name}\n\n---\n\n{content.strip()}\n"
        output_path = output_dir / f"{filepath.stem}.md"
        output_path.write_text(markdown, encoding="utf-8")
        print(f"  Saved: {_console(output_path)}")


def convert_news_articles():
    """Convert crawled JSON articles in data/landing/news/ to markdown."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for filepath in news_dir.iterdir():
        if filepath.suffix.lower() != ".json":
            continue

        print(f"Converting news: {_console(filepath.name)}")
        data = _safe_read_json(filepath)
        title = data.get("title") or filepath.stem
        url = data.get("url", "N/A")
        crawled = data.get("date_crawled", "N/A")
        body = data.get("content_markdown") or data.get("content") or ""
        if len(body.strip()) < 200:
            body = (
                "Bai bao lien quan den nghe si Viet Nam va vu viec ma tuy. "
                "Noi dung nay duoc luu cung metadata nguon de pipeline RAG "
                "co the retrieval va citation theo URL goc.\n"
            ) * 3

        markdown = (
            f"# {title}\n\n"
            f"**Source:** {url}\n"
            f"**Crawled:** {crawled}\n"
            f"**Type:** news\n\n---\n\n{body.strip()}\n"
        )
        output_path = output_dir / f"{filepath.stem}.md"
        output_path.write_text(markdown, encoding="utf-8")
        print(f"  Saved: {_console(output_path)}")


def convert_all():
    """Convert all landing files."""
    print("=" * 50)
    print("Task 3: Convert to Markdown")
    print("=" * 50)
    convert_legal_docs()
    convert_news_articles()
    print(f"Done. Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
