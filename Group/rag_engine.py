from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()


def query_rag(
    query: str,
    top_k: int = 5,
    history: list[dict] | None = None,
    use_hybrid: bool = True,
    use_reranker: bool = True,
) -> dict:
    """Public RAG wrapper used by the UI and evaluation scripts."""
    try:
        return generate_with_citation(query, history=history, top_k=top_k, use_hybrid=use_hybrid, use_reranker=use_reranker)
    except Exception as exc:
        return {
            "answer": f"Lỗi từ RAG Engine: {exc}",
            "context": "",
            "sources": [],
        }


if __name__ == "__main__":
    result = query_rag("Tội tàng trữ trái phép chất ma túy bị xử phạt thế nào?")
    print(result["answer"])
