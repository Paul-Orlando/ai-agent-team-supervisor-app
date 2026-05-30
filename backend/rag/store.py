import chromadb
import os
import hashlib
from .embedder import embed_texts, embed_query

COLLECTION_NAME = "knowledge_base"
_client: chromadb.Client | None = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        _client = chromadb.PersistentClient(path=persist_dir)
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


async def add_chunks(chunks: list[str], source: str = "default") -> int:
    if not chunks:
        return 0
    collection = _get_collection()
    embeddings = await embed_texts(chunks)
    ids = [hashlib.md5(f"{source}:{i}:{c[:50]}".encode()).hexdigest() for i, c in enumerate(chunks)]

    # upsert avoids duplicate errors on restart
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=[{"source": source, "chunk_index": i} for i in range(len(chunks))],
    )
    return len(chunks)


async def query(text: str, n_results: int = 3) -> list[str]:
    collection = _get_collection()
    if collection.count() == 0:
        return []
    embedding = await embed_query(text)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(n_results, collection.count()),
        include=["documents"],
    )
    docs = results.get("documents", [[]])[0]
    return docs


def chunk_count() -> int:
    try:
        return _get_collection().count()
    except Exception:
        return 0
