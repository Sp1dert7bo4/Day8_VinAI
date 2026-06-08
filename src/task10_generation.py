"""Task 10: evidence-grounded generation with citations."""

import os
import re

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve

load_dotenv()

# Five chunks balance evidence coverage and prompt length.
TOP_K = 5
# Conservative sampling values for factual RAG generation.
TOP_P = 0.9
TEMPERATURE = 0.3

SYSTEM_PROMPT = """Trả lời bằng tiếng Việt và chỉ sử dụng context được cung cấp.
Mọi nhận định phải có citation dạng [Nguồn]. Nếu không đủ bằng chứng, trả lời:
'Tôi không thể xác minh thông tin này từ nguồn hiện có'."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Place high-ranked chunks at the beginning and end of the context."""
    if len(chunks) <= 2:
        return list(chunks)
    return list(chunks[::2]) + list(reversed(chunks[1::2]))


def format_context(chunks: list[dict]) -> str:
    """Format chunks with explicit source labels for citation."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        source = metadata.get("source", f"Source {index}")
        doc_type = metadata.get("type", "unknown")
        parts.append(
            f"[Document {index} | Source: {source} | Type: {doc_type}]\n"
            f"{chunk.get('content', '').strip()}"
        )
    return "\n\n---\n\n".join(parts)


def _extractive_answer(query: str, chunks: list[dict]) -> str:
    """Create a deterministic cited answer when no external LLM is enabled."""
    query_tokens = set(re.findall(r"\w+", query.lower(), flags=re.UNICODE))
    statements = []
    for chunk in chunks:
        source = chunk.get("metadata", {}).get("source", "Nguồn không xác định")
        sentences = re.split(r"(?<=[.!?])\s+|\n+", chunk.get("content", ""))
        best = max(
            (sentence.strip() for sentence in sentences if len(sentence.strip()) >= 30),
            key=lambda sentence: len(
                query_tokens
                & set(re.findall(r"\w+", sentence.lower(), flags=re.UNICODE))
            ),
            default="",
        )
        if best:
            statements.append(f"{best} [{source}]")
        if len(statements) == 3:
            break
    return (
        "\n\n".join(statements)
        if statements
        else "Tôi không thể xác minh thông tin này từ nguồn hiện có"
    )


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Retrieve evidence and return an answer with source citations."""
    chunks = retrieve(query, top_k=top_k)
    reordered = reorder_for_llm(chunks)
    if not chunks:
        answer = "Tôi không thể xác minh thông tin này từ nguồn hiện có"
    elif os.getenv("RAG_USE_OPENAI") == "1" and os.getenv("OPENAI_API_KEY"):
        from openai import OpenAI

        context = format_context(reordered)
        response = OpenAI().chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        answer = response.choices[0].message.content
    else:
        answer = _extractive_answer(query, reordered)
    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": chunks[0].get("source", "none") if chunks else "none",
    }


if __name__ == "__main__":
    result = generate_with_citation("Hình phạt tàng trữ trái phép chất ma tuý?")
    print(result["answer"])
