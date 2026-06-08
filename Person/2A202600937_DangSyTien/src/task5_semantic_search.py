import os
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"
COLLECTION_NAME = "DrugLawDocs"

def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Performs semantic search on the ChromaDB vector store.
    Returns:
        List of {'content': str, 'score': float, 'metadata': dict}
    """
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    try:
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
    except Exception:
        # Collection might not exist
        return []

    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    formatted_results = []
    if not results["documents"] or not results["documents"][0]:
        return formatted_results

    docs = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for doc, meta, dist in zip(docs, metadatas, distances):
        # We configured "hnsw:space": "cosine" in task 4, so distance is 1 - cosine_sim
        # Convert distance to score (higher is better)
        score = 1.0 - dist
        formatted_results.append({
            "content": doc,
            "score": score,
            "metadata": meta
        })
    
    # Sort descending by score
    formatted_results.sort(key=lambda x: x["score"], reverse=True)
    return formatted_results

if __name__ == "__main__":
    query = "hình phạt đối với tội phạm ma tuý"
    print(f"Query: {query}")
    results = semantic_search(query, top_k=3)
    if not results:
        print("No results found. Have you indexed documents yet?")
    for i, r in enumerate(results):
        print(f"\n--- Result {i+1} (Score: {r['score']:.4f}) ---")
        print(f"Source: {r['metadata'].get('source', 'Unknown')}")
        print(r['content'][:200].replace('\n', ' ') + "...")
