"""Task 8: vectorless structural fallback inspired by PageIndex."""

import re
from pathlib import Path

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower(), flags=re.UNICODE))


def upload_documents() -> list[dict]:
    """Build a local structural index of Markdown sections."""
    sections = []
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for index, section in enumerate(re.split(r"\n\s*\n", text)):
            section = section.strip()
            if len(section) >= 80:
                sections.append({
                    "content": section,
                    "metadata": {
                        "source": path.name,
                        "type": path.parent.name,
                        "section_index": index,
                    },
                })
    return sections


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Vectorless search based on exact terms and Markdown structure."""
    if not query.strip() or top_k <= 0:
        return []
    query_tokens = _tokens(query)
    results = []
    for section in upload_documents():
        content_tokens = _tokens(section["content"])
        score = len(query_tokens & content_tokens) / max(len(query_tokens), 1)
        if score > 0:
            results.append({
                **section,
                "score": float(score),
                "source": "pageindex",
            })
    return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]
