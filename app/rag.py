"""
RAG (Retrieval-Augmented Generation) module.

Manages a ChromaDB vector store of reference reports and Indian sector
regulations. Documents are ingested via the admin upload endpoint and
retrieved at prompt-generation time to ground LLM outputs.
"""
import os
import re
from pathlib import Path
from typing import List, Optional

import chromadb
from chromadb.config import Settings

# Persist vector DB alongside the app data
_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
_COLLECTION_NAME = "reference_docs"
_EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

_client: Optional[chromadb.ClientAPI] = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection

    _client = chromadb.PersistentClient(
        path=_DB_PATH,
        settings=Settings(anonymized_telemetry=False),
    )

    from chromadb.utils import embedding_functions
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=_EMBED_MODEL)

    _collection = _client.get_or_create_collection(
        name=_COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    import PyPDF2
    from io import BytesIO
    reader = PyPDF2.PdfReader(BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_text_from_docx(file_bytes: bytes) -> str:
    import docx2txt
    from io import BytesIO
    return docx2txt.process(BytesIO(file_bytes))


def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]


def ingest_document(
    file_bytes: bytes,
    filename: str,
    doc_type: str = "reference",
    sector: Optional[str] = None,
) -> int:
    """
    Ingest a PDF or DOCX document into the vector store.

    Args:
        file_bytes: Raw file content
        filename: Original filename (used to detect extension)
        doc_type: "reference" | "regulation"
        sector: Optional sector tag (e.g. "bakery", "textile")

    Returns:
        Number of chunks stored
    """
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        text = _extract_text_from_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        text = _extract_text_from_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use PDF or DOCX.")

    chunks = _chunk_text(text)
    if not chunks:
        return 0

    collection = _get_collection()

    # Stable chunk IDs based on filename + position so re-uploads overwrite
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", filename)
    ids = [f"{safe_name}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {"filename": filename, "doc_type": doc_type, "sector": sector or "", "chunk_index": i}
        for i in range(len(chunks))
    ]

    collection.upsert(documents=chunks, ids=ids, metadatas=metadatas)
    return len(chunks)


def retrieve(
    query: str,
    n_results: int = 5,
    doc_type: Optional[str] = None,
    sector: Optional[str] = None,
) -> str:
    """
    Retrieve the most relevant chunks for a query.

    Returns a single formatted string ready to be injected into a prompt.
    """
    collection = _get_collection()
    if collection.count() == 0:
        return ""

    where: Optional[dict] = None
    if doc_type and sector:
        where = {"$and": [{"doc_type": doc_type}, {"sector": sector}]}
    elif doc_type:
        where = {"doc_type": doc_type}
    elif sector:
        where = {"sector": sector}

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
        where=where if where else None,
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    if not docs:
        return ""

    parts = []
    for doc, meta in zip(docs, metas):
        source = meta.get("filename", "unknown")
        parts.append(f"[Source: {source}]\n{doc}")

    return "\n\n---\n\n".join(parts)


def list_documents() -> List[dict]:
    """Return a deduplicated list of ingested documents with metadata."""
    collection = _get_collection()
    if collection.count() == 0:
        return []

    results = collection.get(include=["metadatas"])
    seen = {}
    for meta in results.get("metadatas", []):
        fname = meta.get("filename", "")
        if fname not in seen:
            seen[fname] = {
                "filename": fname,
                "doc_type": meta.get("doc_type", ""),
                "sector": meta.get("sector", ""),
            }
    return list(seen.values())


def delete_document(filename: str) -> int:
    """Remove all chunks for a given filename. Returns chunks deleted."""
    collection = _get_collection()
    results = collection.get(where={"filename": filename}, include=["metadatas"])
    ids = results.get("ids", [])
    if ids:
        collection.delete(ids=ids)
    return len(ids)
