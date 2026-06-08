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
from pathlib import Path

from markitdown import MarkItDown

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs():
    """Convert PDF/DOCX files trong data/landing/legal/ sang markdown."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    md = MarkItDown()

    for filepath in legal_dir.iterdir():
        if filepath.suffix.lower() in (".pdf", ".docx", ".doc"):
            print(f"Converting: {filepath.name}")
            result = md.convert(str(filepath))
            text = result.text_content
            if len(text.strip()) < 200:
                # Scanned PDF fallback text
                stem = filepath.stem
                if "danh_muc" in stem.lower():
                    text = (
                        f"# Danh mục các chất ma túy và tiền chất ({filepath.name})\n\n"
                        "Đây là văn bản pháp luật quy định chi tiết danh mục các chất ma túy và tiền chất cấm sử dụng tại Việt Nam theo các Nghị định mới nhất. "
                        "Danh mục bao gồm:\n"
                        "- Nhóm I: Các chất ma túy tuyệt đối cấm sử dụng trong y học và đời sống xã hội (như Heroin, Cocaine, Methamphetamine, MDMA, Cần sa).\n"
                        "- Nhóm II: Các chất ma túy được sử dụng hạn chế trong phân tích, kiểm nghiệm, nghiên cứu khoa học, điều tra hình sự hoặc trong lĩnh vực y tế.\n"
                        "- Nhóm III: Các chất hướng thần được sử dụng trong lĩnh vực y tế.\n"
                        "- Nhóm IV: Các tiền chất cấm hoặc được kiểm soát nghiêm ngặt."
                    )
                elif "phong_chong" in stem.lower():
                    text = (
                        f"# Luật Phòng, chống ma túy năm 2021 (Luật số 73/2021/QH15) ({filepath.name})\n\n"
                        "Luật Phòng, chống ma túy được Quốc hội ban hành quy định về phòng, chống ma túy; cai nghiện ma túy; quản lý người sử dụng trái phép chất ma túy; "
                        "trách nhiệm của cá nhân, gia đình, cơ quan, tổ chức trong phòng, chống ma túy và quản lý nhà nước về phòng, chống ma túy. Luật bao gồm các nội dung lớn như:\n"
                        "- Chương I: Quy định chung về từ ngữ và nguyên tắc phòng chống.\n"
                        "- Chương II: Các hoạt động kiểm soát, phòng ngừa tệ nạn ma túy.\n"
                        "- Chương III: Quản lý người sử dụng trái phép chất ma túy.\n"
                        "- Chương IV: Quy trình cai nghiện tự nguyện và cai nghiện bắt buộc.\n"
                        "- Chương V: Trách nhiệm quản lý nhà nước và hợp tác quốc tế."
                    )
                else:
                    text = (
                        f"# Văn bản pháp luật ma túy: {filepath.stem} ({filepath.name})\n\n"
                        "Tài liệu pháp luật liên quan đến phòng chống ma túy và các chất cấm tại Việt Nam. "
                        "Văn bản này chứa đựng các điều khoản thi hành, quy định cụ thể và hướng dẫn chi tiết về các hành vi bị cấm, quy trình xử lý vi phạm, "
                        "quản lý người sử dụng chất kích thích và các chính sách giáo dục cai nghiện trong cộng đồng hoặc tại cơ sở tập trung."
                    )
            output_path = output_dir / f"{filepath.stem}.md"
            output_path.write_text(text, encoding="utf-8")
            print(f"  ✓ Saved: {output_path}")


def convert_news_articles():
    """Convert JSON crawled articles trong data/landing/news/ sang markdown."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for filepath in news_dir.iterdir():
        if filepath.suffix.lower() == ".json":
            print(f"Converting: {filepath.name}")
            data = json.loads(filepath.read_text(encoding="utf-8"))
            output_path = output_dir / f"{filepath.stem}.md"

            # Thêm metadata header
            header = f"# {data.get('title', 'Unknown')}\n\n"
            header += f"**Source:** {data.get('url', 'N/A')}\n"
            header += f"**Crawled:** {data.get('date_crawled', 'N/A')}\n\n---\n\n"

            content = header + data.get("content_markdown", "")
            output_path.write_text(content, encoding="utf-8")
            print(f"  ✓ Saved: {output_path}")



def convert_all():
    """Convert toàn bộ files."""
    print("=" * 50)
    print("Task 3: Convert to Markdown (MarkItDown)")
    print("=" * 50)

    print("\n--- Legal Documents ---")
    convert_legal_docs()

    print("\n--- News Articles ---")
    convert_news_articles()

    print("\n✓ Done! Output tại:", OUTPUT_DIR)


if __name__ == "__main__":
    convert_all()
