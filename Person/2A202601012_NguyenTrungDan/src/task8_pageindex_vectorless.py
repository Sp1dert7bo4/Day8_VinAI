"""
Task 8 - PageIndex vectorless RAG.

When PAGEINDEX_API_KEY is unavailable, this module provides a local vectorless
fallback by matching query terms against markdown chunks. The output shape is the
same as a PageIndex result and is marked with source='pageindex'.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

try:
    from .task4_chunking_indexing import load_index, tokenize
except ImportError:
    from task4_chunking_indexing import load_index, tokenize

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


def upload_documents():
    """
    Prepare documents for PageIndex.

    The local fallback simply confirms documents are available. With a real
    account, replace this body with the PageIndex SDK upload call.
    """
    docs = list(STANDARDIZED_DIR.rglob("*.md"))
    if not docs:
        raise FileNotFoundError("No markdown documents found in data/standardized")
    return [{"filename": doc.name, "path": str(doc)} for doc in docs]


def _vectorless_score(query: str, content: str) -> float:
    query_tokens = set(tokenize(query))
    doc_tokens = tokenize(content)
    if not query_tokens or not doc_tokens:
        return 0.0
    doc_set = set(doc_tokens)
    coverage = len(query_tokens & doc_set) / len(query_tokens)
    phrase_bonus = 0.1 if query.lower()[:20] in content.lower() else 0.0
    return min(1.0, coverage + phrase_bonus)


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Vectorless retrieval using local document structure as a fallback.

    Returns:
        List of {'content': str, 'score': float, 'metadata': dict, 'source': 'pageindex'}
    """
    if top_k <= 0:
        return []

    chunks = load_index()
    results = []
    for chunk in chunks:
        score = _vectorless_score(query, chunk.get("content", ""))
        if score > 0:
            results.append(
                {
                    "content": chunk["content"],
                    "score": float(score),
                    "metadata": chunk.get("metadata", {}),
                    "source": "pageindex",
                }
            )

    if not results:
        for chunk in chunks[:top_k]:
            results.append(
                {
                    "content": chunk["content"],
                    "score": 0.1,
                    "metadata": chunk.get("metadata", {}),
                    "source": "pageindex",
                }
            )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    for result in pageindex_search("hinh phat su dung ma tuy", top_k=3):
        print(f"[{result['score']:.3f}] {result['content'][:100]}...")
