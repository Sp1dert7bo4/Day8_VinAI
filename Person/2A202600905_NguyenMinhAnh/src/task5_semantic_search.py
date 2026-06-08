"""
Task 5 — Semantic Search Module.

Viết module tìm kiếm ngữ nghĩa (dense retrieval) trên vector store.

Yêu cầu:
    - Input: query string + top_k
    - Output: danh sách chunks có score, sorted descending
    - Phải tương thích với embedding model và vector store ở Task 4
"""


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm ngữ nghĩa sử dụng vector similarity.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,      # Nội dung chunk
            'score': float,      # Cosine similarity score
            'metadata': dict     # source, doc_type, chunk_index
        }
        Sorted by score descending.
    """
    import chromadb
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("BAAI/bge-m3")
    query_embedding = model.encode(query).tolist()

    client = chromadb.PersistentClient(path="./chroma_db")
    try:
        collection = client.get_collection("DrugLawDocs")
    except Exception:
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    docs = []
    if results and results['documents'] and len(results['documents']) > 0:
        for i in range(len(results['documents'][0])):
            distance = results['distances'][0][i]
            # In chromadb, cosine distance is returned, score = 1 - distance
            docs.append({
                "content": results['documents'][0][i],
                "score": 1 - distance,
                "metadata": results['metadatas'][0][i]
            })

    # Sort descending by score
    docs = sorted(docs, key=lambda x: x['score'], reverse=True)
    return docs


if __name__ == "__main__":
    # Test
    results = semantic_search("hình phạt cho tội tàng trữ ma tuý", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
