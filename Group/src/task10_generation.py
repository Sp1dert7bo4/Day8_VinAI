import os

import openai
from dotenv import load_dotenv

from src.task9_retrieval_pipeline import retrieve


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1")
MODEL_NAME = os.getenv("LLM_MODEL", "google/gemini-2.5-flash")


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Put the strongest chunks near the beginning and end of the context."""
    if not chunks:
        return []

    reordered = [None] * len(chunks)
    left, right = 0, len(chunks) - 1
    for index, chunk in enumerate(chunks):
        if index % 2 == 0:
            reordered[left] = chunk
            left += 1
        else:
            reordered[right] = chunk
            right -= 1
    return reordered


def format_context(chunks: list[dict]) -> str:
    parts = []
    for index, chunk in enumerate(chunks):
        source = chunk.get("metadata", {}).get("source", f"Unknown_{index}")
        parts.append(f"--- Source: {source} ---\n{chunk.get('content', '')}")
    return "\n\n".join(parts)


def _format_history(history: list[dict] | None, max_messages: int = 8) -> str:
    if not history:
        return ""

    lines = []
    for message in history[-max_messages:]:
        role = "Người dùng" if message.get("role") == "user" else "Trợ lý"
        content = str(message.get("content", "")).strip()
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _build_retrieval_query(query: str, history: list[dict] | None) -> str:
    """Give retrieval enough context for short follow-up questions."""
    if not history:
        return query

    previous_user_messages = [
        str(message.get("content", "")).strip()
        for message in history
        if message.get("role") == "user" and message.get("content")
    ]
    if not previous_user_messages:
        return query
    return f"{previous_user_messages[-1]}\nCâu hỏi tiếp nối: {query}"


def _build_sources(chunks: list[dict]) -> list[dict]:
    sources = []
    seen = set()
    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        source = metadata.get("source", "Không rõ nguồn")
        content = chunk.get("content", "").strip()
        key = (source, content)
        if key in seen:
            continue
        seen.add(key)
        sources.append(
            {
                "source": source,
                "content": content,
                "score": chunk.get("score"),
                "metadata": metadata,
            }
        )
    return sources


def generate_with_citation(
    query: str,
    history: list[dict] | None = None,
    top_k: int = 5,
) -> dict:
    """Run retrieval and answer with conversation-aware citations."""
    retrieval_query = _build_retrieval_query(query, history)
    chunks = retrieve(retrieval_query, top_k=top_k)
    reordered_chunks = reorder_for_llm(chunks)
    context = format_context(reordered_chunks)
    sources = _build_sources(chunks)
    conversation = _format_history(history)

    system_prompt = (
        "Bạn là trợ lý tư vấn phòng, chống ma túy tại Việt Nam. Trả lời đúng trọng tâm, "
        "rõ ràng, thân thiện và bằng tiếng Việt. Hiểu câu hỏi tiếp nối dựa trên lịch sử "
        "hội thoại. Chỉ dùng tài liệu tham khảo để đưa ra thông tin thực tế hoặc pháp lý; "
        "luôn ghi chú nguồn theo dạng [Source: <tên nguồn>]. Không bịa thông tin. Nếu tài "
        "liệu chưa đủ, hãy nói rõ giới hạn đó. Với tình huống khẩn cấp hoặc nguy hiểm, "
        "khuyến nghị người dùng liên hệ cơ quan chức năng hoặc cơ sở y tế phù hợp."
    )
    user_prompt = (
        f"Lịch sử hội thoại gần đây:\n{conversation or '(Chưa có)'}\n\n"
        f"Tài liệu tham khảo:\n{context or '(Không tìm thấy tài liệu phù hợp)'}\n\n"
        f"Câu hỏi hiện tại: {query}"
    )

    if not OPENAI_API_KEY:
        return {
            "answer": "Chưa cấu hình OPENAI_API_KEY nên hệ thống chưa thể tạo câu trả lời.",
            "context": context,
            "sources": sources,
        }

    try:
        client = openai.OpenAI(base_url=OPENAI_API_BASE, api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=1024,
        )
        answer = response.choices[0].message.content
        return {"answer": answer, "context": context, "sources": sources}
    except Exception as exc:
        return {
            "answer": f"Lỗi trong quá trình tạo sinh (LLM): {exc}",
            "context": context,
            "sources": sources,
        }


if __name__ == "__main__":
    print(generate_with_citation("Hình phạt đối với tội tàng trữ ma túy là gì?"))
