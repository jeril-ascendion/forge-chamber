"""
Forge Chamber — Embedding Model & ChromaDB Singleton

Loads sentence-transformers all-MiniLM-L6-v2 once at startup.
Provides ChromaDB PersistentClient with a shared collection.
"""

import logging
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "forge_context"

# Module-level singletons — initialized via init_embedder()
_model: SentenceTransformer | None = None
_embed_fn: SentenceTransformerEmbeddingFunction | None = None
_chroma_clients: dict[str, chromadb.ClientAPI] = {}


def init_embedder() -> None:
    """Load the embedding model. Call once at startup."""
    global _model, _embed_fn
    if _model is not None:
        return

    logger.info("Loading embedding model: %s", MODEL_NAME)
    _model = SentenceTransformer(MODEL_NAME)
    _embed_fn = SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    logger.info("Embedding model loaded")


def embed(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts. Returns list of float vectors."""
    if _model is None:
        init_embedder()
    assert _model is not None
    embeddings = _model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()


def get_chroma_collection(data_dir: str) -> chromadb.Collection:
    """Get or create the ChromaDB collection for the given data directory."""
    if _embed_fn is None:
        init_embedder()
    assert _embed_fn is not None

    chroma_path = str(Path(data_dir) / "chroma")
    if chroma_path not in _chroma_clients:
        Path(chroma_path).mkdir(parents=True, exist_ok=True)
        _chroma_clients[chroma_path] = chromadb.PersistentClient(path=chroma_path)
        logger.info("ChromaDB initialized at %s", chroma_path)

    client = _chroma_clients[chroma_path]
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_embed_fn,
    )
