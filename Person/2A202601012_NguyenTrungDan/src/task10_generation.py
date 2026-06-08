"""
Task 10 - Generation with citations.

The production path can call an LLM, but this implementation includes an
extractive local generator so the assignment runs without API keys. It only uses
retrieved context and cites the source file for every selected statement.
"""

import re

try:
    from .task9_retrieval_pipeline import retrieve
except ImportError:
    from task9_retrieval_pipeline import retrieve


TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

SYSTEM_PROMPT = """Answer the question in Vietnamese using only provided context.
Every factual claim must include a citation like [Source, Year].
If evidence is insufficient, say: Tôi không thể xác minh thông tin này từ nguồn hiện có."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """
    Reorder chunks to reduce lost-in-the-middle.

    Example: [1, 2, 3, 4, 5] -> [1, 3, 5, 4, 2]
    """
    if len(chunks) <= 2:
        return chunks

    first_pass = [chunks[i] for i in range(0, len(chunks), 2)]
    second_pass = [chunks[i] for i in range(len(chunks) - 1, 0, -1) if i % 2 == 1]
    return first_pass + second_pass


def format_context(chunks: list[dict]) -> str:
    """
    Format chunks into a prompt context with source labels.
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        source = metadata.get("source", f"Source {i}")
        doc_type = metadata.get("type", "unknown")
        score = chunk.get("score", 0.0)
        context_parts.append(
            f"[Document {i} | Source: {source} | Type: {doc_type} | Score: {score:.3f}]\n"
            f"{chunk.get('content', '')}"
        )
    return "\n\n---\n\n".join(context_parts)


def _citation(metadata: dict) -> str:
    source = metadata.get("source", "Nguon khong ro")
    year_match = re.search(r"(20\d{2}|19\d{2})", source)
    year = year_match.group(1) if year_match else "n.d."
    clean_source = re.sub(r"\.(md|pdf|docx?|json)$", "", source, flags=re.I)
    return f"[{clean_source}, {year}]"


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?。])\s+|\n+", text)
    return [part.strip(" -\t") for part in parts if len(part.strip()) > 40]


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """
    End-to-end RAG generation with citation.

    Returns:
        {'answer': str, 'sources': list[dict], 'retrieval_source': str}
    """
    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
            "sources": [],
            "retrieval_source": "none",
        }

    reordered = reorder_for_llm(chunks)
    selected_claims = []
    for chunk in reordered:
        citation = _citation(chunk.get("metadata", {}))
        for sentence in _sentences(chunk.get("content", "")):
            selected_claims.append(f"{sentence} {citation}")
            break
        if len(selected_claims) >= 3:
            break

    if not selected_claims:
        answer = "Tôi không thể xác minh thông tin này từ nguồn hiện có."
    else:
        answer = (
            f"Dựa trên các nguồn đã truy xuất cho câu hỏi '{query}', "
            + " ".join(selected_claims)
        )

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": chunks[0].get("source", "hybrid") if chunks else "none",
    }


if __name__ == "__main__":
    result = generate_with_citation("Hinh phat tang tru trai phep chat ma tuy?")
    print(result["answer"])
