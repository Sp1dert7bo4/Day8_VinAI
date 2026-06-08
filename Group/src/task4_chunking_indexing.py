import os
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Constants
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Path calculation
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
STD_DIR = DATA_DIR / "standardized"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"
COLLECTION_NAME = "DrugLawDocs"

def load_documents():
    """Reads all Markdown files from data/standardized/"""
    documents = []
    if not STD_DIR.exists():
        return documents
    
    for md_file in STD_DIR.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        # Ensure metadata contains string/int/float, no complex objects
        metadata = {
            "source": str(md_file.relative_to(DATA_DIR).as_posix()),
            "filename": md_file.name
        }
        documents.append({
            "content": content,
            "metadata": metadata
        })
    return documents

def chunk_documents(documents):
    """Chunks documents using RecursiveCharacterTextSplitter."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = []
    for doc in documents:
        splits = text_splitter.split_text(doc["content"])
        for i, split in enumerate(splits):
            meta = doc["metadata"].copy()
            meta["chunk_index"] = i
            chunks.append({
                "content": split,
                "metadata": meta
            })
    return chunks

def embed_chunks(chunks):
    """Placeholder per implementation plan.
    ChromaDB handles embedding internally via SentenceTransformerEmbeddingFunction."""
    pass

def index_to_vectorstore(chunks=None):
    """Initializes ChromaDB, creates collection and adds chunks."""
    if chunks is None:
        docs = load_documents()
        chunks = chunk_documents(docs)
        
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
        
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )
    
    if not chunks:
        return collection
        
    batch_size = 5400
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        ids = [f"{c['metadata']['filename']}_{c['metadata']['chunk_index']}" for c in batch]
        documents = [c["content"] for c in batch]
        metadatas = [c["metadata"] for c in batch]
        
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    return collection

if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents.")
    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks.")
    print("Indexing to ChromaDB...")
    index_to_vectorstore(chunks)
    print("Indexing completed!")
