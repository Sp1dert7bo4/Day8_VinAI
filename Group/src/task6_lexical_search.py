import re
from pathlib import Path
import chromadb
from rank_bm25 import BM25Okapi

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"
COLLECTION_NAME = "DrugLawDocs"

# Global caching
_bm25_index = None
_corpus_docs = None
_corpus_metas = None

def _tokenize(text: str) -> list[str]:
    # Simple tokenization
    return re.findall(r'\w+', text.lower())

def build_bm25_index():
    global _bm25_index, _corpus_docs, _corpus_metas
    
    if _bm25_index is not None:
        return
        
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception:
        # DB might not exist
        return
        
    data = collection.get()
    _corpus_docs = data["documents"]
    _corpus_metas = data["metadatas"]
    
    if not _corpus_docs:
        return
        
    tokenized_corpus = [_tokenize(doc) for doc in _corpus_docs]
    _bm25_index = BM25Okapi(tokenized_corpus)

def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    if _bm25_index is None:
        build_bm25_index()
        
    if _bm25_index is None or not _corpus_docs:
        return []
        
    tokenized_query = _tokenize(query)
    scores = _bm25_index.get_scores(tokenized_query)
    
    results = []
    for i, score in enumerate(scores):
        if score > 0:
            results.append({
                "content": _corpus_docs[i],
                "score": float(score),
                "metadata": _corpus_metas[i]
            })
            
    # Sort descending by score
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

if __name__ == "__main__":
    query = "hình phạt ma tuý"
    print(f"Query: {query}")
    results = lexical_search(query, top_k=3)
    if not results:
        print("No results found. Have you indexed documents yet?")
    for i, r in enumerate(results):
        print(f"\n--- Result {i+1} (Score: {r['score']:.4f}) ---")
        print(f"Source: {r['metadata'].get('source', 'Unknown')}")
        print(r['content'][:200].replace('\n', ' ') + "...")
