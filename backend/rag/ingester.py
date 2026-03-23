"""
Forge Chamber — Document Ingestion

Ingests URLs and files into ChromaDB via LlamaIndex chunking
and sentence-transformer embeddings.
"""

import hashlib
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path

from llama_index.core.node_parser import SentenceSplitter

from backend.rag.embedder import embed, get_chroma_collection

logger = logging.getLogger(__name__)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def _sources_path(data_dir: str) -> Path:
    return Path(data_dir) / "sources.json"


def _load_sources(data_dir: str) -> list[dict]:
    p = _sources_path(data_dir)
    if p.exists():
        return json.loads(p.read_text())
    return []


def _save_sources(data_dir: str, sources: list[dict]) -> None:
    p = _sources_path(data_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(sources, indent=2))


def _chunk_id(source: str, index: int, chunk_text: str) -> str:
    """Deterministic chunk ID from source + index + text prefix."""
    raw = f"{source}:{index}:{chunk_text[:50]}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _split_text(text: str) -> list[str]:
    """Split text into chunks using LlamaIndex SentenceSplitter."""
    splitter = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    from llama_index.core import Document

    docs = [Document(text=text)]
    nodes = splitter.get_nodes_from_documents(docs)
    return [n.get_content() for n in nodes if n.get_content().strip()]


# ---------------------------------------------------------------------------
# URL ingestion
# ---------------------------------------------------------------------------


def ingest_url(url: str, data_dir: str) -> dict:
    """Ingest a web URL into the RAG pipeline."""
    from llama_index.readers.web import SimpleWebPageReader

    logger.info("Ingesting URL: %s", url)

    reader = SimpleWebPageReader(html_to_text=True)
    documents = reader.load_data([url])

    if not documents:
        raise ValueError(f"No content fetched from {url}")

    full_text = "\n\n".join(doc.text for doc in documents if doc.text)
    title = url.split("/")[-1].replace("-", " ").replace(".html", "").strip() or url

    # Chunk
    chunks = _split_text(full_text)
    if not chunks:
        raise ValueError(f"No chunks produced from {url}")

    # Generate IDs and metadata
    source_id = str(uuid.uuid4())
    ids = [_chunk_id(url, i, c) for i, c in enumerate(chunks)]
    metadatas = [
        {"source": source_id, "source_label": url, "source_type": "url", "chunk_index": i}
        for i in range(len(chunks))
    ]

    # Upsert to ChromaDB
    collection = get_chroma_collection(data_dir)
    embeddings = embed(chunks)
    collection.upsert(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)

    # Update sources.json
    sources = _load_sources(data_dir)
    sources.append({
        "id": source_id,
        "label": url,
        "chunks": len(chunks),
        "source_type": "url",
        "ingested_at": datetime.utcnow().isoformat(),
    })
    _save_sources(data_dir, sources)

    logger.info("Ingested URL %s: %d chunks", url, len(chunks))
    return {"status": "ingested", "chunks": len(chunks), "title": title}


# ---------------------------------------------------------------------------
# File ingestion
# ---------------------------------------------------------------------------


def ingest_file(content: bytes, filename: str, data_dir: str) -> dict:
    """Ingest a file (PDF, DOCX, TXT, MD) into the RAG pipeline."""
    logger.info("Ingesting file: %s", filename)

    tmp_dir = Path(data_dir) / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / filename

    try:
        tmp_path.write_bytes(content)
        ext = Path(filename).suffix.lower()

        if ext == ".pdf":
            from llama_index.readers.file import PDFReader

            reader = PDFReader()
            documents = reader.load_data(tmp_path)
            full_text = "\n\n".join(doc.text for doc in documents if doc.text)
        elif ext == ".docx":
            from llama_index.readers.file import DocxReader

            reader = DocxReader()
            documents = reader.load_data(tmp_path)
            full_text = "\n\n".join(doc.text for doc in documents if doc.text)
        elif ext in (".txt", ".md"):
            full_text = content.decode("utf-8", errors="replace")
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        if not full_text.strip():
            raise ValueError(f"No text extracted from {filename}")

        title = Path(filename).stem.replace("-", " ").replace("_", " ")

        # Chunk
        chunks = _split_text(full_text)
        if not chunks:
            raise ValueError(f"No chunks produced from {filename}")

        # Generate IDs and metadata
        source_id = str(uuid.uuid4())
        ids = [_chunk_id(filename, i, c) for i, c in enumerate(chunks)]
        metadatas = [
            {"source": source_id, "source_label": filename, "source_type": "file", "chunk_index": i}
            for i in range(len(chunks))
        ]

        # Upsert to ChromaDB
        collection = get_chroma_collection(data_dir)
        embeddings = embed(chunks)
        collection.upsert(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)

        # Update sources.json
        sources = _load_sources(data_dir)
        sources.append({
            "id": source_id,
            "label": filename,
            "chunks": len(chunks),
            "source_type": "file",
            "ingested_at": datetime.utcnow().isoformat(),
        })
        _save_sources(data_dir, sources)

        logger.info("Ingested file %s: %d chunks", filename, len(chunks))
        return {"status": "ingested", "chunks": len(chunks), "title": title}

    finally:
        if tmp_path.exists():
            tmp_path.unlink()


# ---------------------------------------------------------------------------
# Source management
# ---------------------------------------------------------------------------


def list_ingested_sources(data_dir: str) -> list[dict]:
    """List all ingested sources."""
    return _load_sources(data_dir)


def delete_source(source_id: str, data_dir: str) -> bool:
    """Delete a source and all its chunks from ChromaDB."""
    sources = _load_sources(data_dir)
    source = next((s for s in sources if s["id"] == source_id), None)
    if not source:
        return False

    # Remove chunks from ChromaDB
    try:
        collection = get_chroma_collection(data_dir)
        # Get all chunk IDs for this source
        results = collection.get(where={"source": source_id})
        if results["ids"]:
            collection.delete(ids=results["ids"])
            logger.info("Deleted %d chunks for source %s", len(results["ids"]), source_id)
    except Exception as exc:
        logger.warning("Failed to delete chunks from ChromaDB: %s", exc)

    # Remove from sources.json
    filtered = [s for s in sources if s["id"] != source_id]
    _save_sources(data_dir, filtered)

    return True
