"""
Task 4 - Chunking and lightweight local indexing.

The documented production choice is BAAI/bge-m3 + Weaviate. For this lab
submission the implementation also writes a local JSON index so tests and demos
can run without Docker, cloud accounts, or embedding API keys.
"""

import hashlib
import json
import math
import re
from pathlib import Path

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
INDEX_PATH = Path(__file__).parent.parent / "data" / "local_index.json"

# Recursive character chunking is robust for mixed legal PDFs and news markdown.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

# Production target. The local fallback below uses hashed bag-of-words vectors.
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
VECTOR_STORE = "local_json"


def tokenize(text: str) -> list[str]:
    """Unicode-friendly tokenizer for Vietnamese text."""
    return re.findall(r"[\wÀ-ỹ]+", text.lower(), flags=re.UNICODE)


def load_documents() -> list[dict]:
    """
    Read all markdown files from data/standardized/.

    Returns:
        List of {'content': str, 'metadata': {'source': str, 'type': str}}
    """
    documents = []
    for md_file in STANDARDIZED_DIR.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8", errors="replace").strip()
        if not content:
            continue
        doc_type = "legal" if "legal" in md_file.parts else "news"
        documents.append(
            {
                "content": content,
                "metadata": {
                    "source": md_file.name,
                    "path": str(md_file.relative_to(STANDARDIZED_DIR)),
                    "type": doc_type,
                },
            }
        )
    return documents


def _split_text(text: str) -> list[str]:
    if len(text) <= CHUNK_SIZE:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        window = text[start:end]
        if end < len(text):
            split_at = max(window.rfind("\n\n"), window.rfind(". "), window.rfind(" "))
            if split_at > CHUNK_SIZE * 0.55:
                end = start + split_at + 1
                window = text[start:end]
        cleaned = window.strip()
        if cleaned:
            chunks.append(cleaned)
        if end >= len(text):
            break
        start = max(0, end - CHUNK_OVERLAP)
    return chunks


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Chunk documents with recursive character splitting.

    Returns:
        List of {'content': str, 'metadata': dict}
    """
    chunks = []
    for doc in documents:
        for i, chunk_text in enumerate(_split_text(doc["content"])):
            chunks.append(
                {
                    "content": chunk_text,
                    "metadata": {**doc["metadata"], "chunk_index": i},
                }
            )
    return chunks


def _hash_embedding(text: str, dim: int = EMBEDDING_DIM) -> list[float]:
    vector = [0.0] * dim
    for token in tokenize(text):
        digest = hashlib.md5(token.encode("utf-8")).hexdigest()
        idx = int(digest[:8], 16) % dim
        vector[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Add deterministic local embeddings to each chunk.

    Returns:
        Each chunk dict with an 'embedding': list[float] key.
    """
    for chunk in chunks:
        chunk["embedding"] = _hash_embedding(chunk["content"])
    return chunks


def index_to_vectorstore(chunks: list[dict]):
    """Persist chunks to a local JSON vector-store fallback."""
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    serializable = []
    for chunk in chunks:
        item = chunk.copy()
        # Keep the index compact; search modules recompute hashed vectors.
        item.pop("embedding", None)
        serializable.append(item)
    INDEX_PATH.write_text(
        json.dumps(serializable, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return INDEX_PATH


def load_index() -> list[dict]:
    """Load local index, creating it from markdown files when needed."""
    if INDEX_PATH.exists():
        try:
            return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    docs = load_documents()
    chunks = chunk_documents(docs)
    index_to_vectorstore(chunks)
    return chunks


def run_pipeline():
    """Run load -> chunk -> embed -> local index."""
    print("=" * 50)
    print("Task 4: Chunking & Indexing")
    print(f"Chunking: {CHUNKING_METHOD} size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}")
    print(f"Embedding target: {EMBEDDING_MODEL} ({EMBEDDING_DIM} dim)")
    print(f"Vector store: {VECTOR_STORE}")
    print("=" * 50)

    docs = load_documents()
    print(f"Loaded {len(docs)} documents")
    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks")
    chunks = embed_chunks(chunks)
    index_to_vectorstore(chunks)
    print(f"Indexed to {INDEX_PATH}")


if __name__ == "__main__":
    run_pipeline()
