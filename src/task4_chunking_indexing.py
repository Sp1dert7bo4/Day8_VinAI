"""Task 4: load, chunk, embed and index standardized Markdown documents."""

import json
import re
from pathlib import Path

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
INDEX_DIR = Path(__file__).parent.parent / "data" / "index"
INDEX_PATH = INDEX_DIR / "chunks.json"

# 500 characters keeps retrieval precise while retaining useful context.
# A 50-character overlap preserves sentences near chunk boundaries.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

# Hashing vectors run fully offline. Task 5 uses TF-IDF cosine over this corpus.
EMBEDDING_MODEL = "sklearn-hashing-vectorizer"
EMBEDDING_DIM = 384
VECTOR_STORE = "local-json"


def load_documents() -> list[dict]:
    """Load all non-empty Markdown documents with source metadata."""
    documents = []
    for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8").strip()
        if content:
            documents.append({
                "content": content,
                "metadata": {
                    "source": md_file.name,
                    "type": md_file.parent.name,
                    "path": str(md_file.relative_to(STANDARDIZED_DIR)),
                },
            })
    return documents


def _split_text(text: str) -> list[str]:
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        if end < len(text):
            window = text[start:end]
            split_at = max(
                window.rfind("\n\n"),
                window.rfind("\n"),
                window.rfind(". "),
                window.rfind(" "),
            )
            if split_at >= int(CHUNK_SIZE * 0.6):
                end = start + split_at + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - CHUNK_OVERLAP, start + 1)
    return chunks


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Split documents using a recursive-style boundary-aware strategy."""
    chunks = []
    for document in documents:
        for index, content in enumerate(_split_text(document["content"])):
            chunks.append({
                "content": content,
                "metadata": {**document.get("metadata", {}), "chunk_index": index},
            })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Add compact local hashing embeddings to chunks."""
    if not chunks:
        return []
    from sklearn.feature_extraction.text import HashingVectorizer

    vectorizer = HashingVectorizer(
        n_features=EMBEDDING_DIM, alternate_sign=False, norm="l2"
    )
    vectors = vectorizer.transform([chunk["content"] for chunk in chunks])
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector.toarray()[0].tolist()
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> Path:
    """Persist chunks in a local JSON vector store."""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(chunks, ensure_ascii=False), encoding="utf-8")
    return INDEX_PATH


def load_index(build_if_missing: bool = True) -> list[dict]:
    """Load the local index, building it on first use."""
    if INDEX_PATH.exists():
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    if not build_if_missing:
        return []
    chunks = embed_chunks(chunk_documents(load_documents()))
    index_to_vectorstore(chunks)
    return chunks


def run_pipeline() -> list[dict]:
    """Run load, chunk, embed and index."""
    documents = load_documents()
    chunks = embed_chunks(chunk_documents(documents))
    index_to_vectorstore(chunks)
    print(f"Loaded {len(documents)} documents; indexed {len(chunks)} chunks.")
    return chunks


if __name__ == "__main__":
    run_pipeline()
