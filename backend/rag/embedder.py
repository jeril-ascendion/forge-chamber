from fastembed import TextEmbedding
import chromadb
from chromadb import EmbeddingFunction
from pathlib import Path

_model = None

def get_model() -> TextEmbedding:
    global _model
    if _model is None:
        _model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return _model

def embed(texts: list[str]) -> list[list[float]]:
    model = get_model()
    return [e.tolist() for e in model.embed(texts)]

class FastEmbedFunction(EmbeddingFunction):
    def __call__(self, input: list[str]) -> list[list[float]]:
        return embed(input)

def get_chroma_collection(data_dir: str):
    Path(f"{data_dir}/chroma").mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=f"{data_dir}/chroma")
    return client.get_or_create_collection(
        name="forge_context",
        embedding_function=FastEmbedFunction()
    )

def load_embedder():
    """Called at startup to warm up the model."""
    get_model()
    print("Embedder loaded (fastembed BAAI/bge-small-en-v1.5)")
