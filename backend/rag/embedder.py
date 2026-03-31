from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
import chromadb
from pathlib import Path

_embedding_function = None

def get_embedding_function():
    global _embedding_function
    if _embedding_function is None:
        _embedding_function = ONNXMiniLM_L6_V2()
    return _embedding_function

def embed(texts: list[str]) -> list[list[float]]:
    ef = get_embedding_function()
    return ef(texts)

def get_chroma_collection(data_dir: str):
    Path(f"{data_dir}/chroma").mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=f"{data_dir}/chroma")
    return client.get_or_create_collection(
        name="forge_context",
        embedding_function=get_embedding_function()
    )

def load_embedder():
    get_embedding_function()
    print("Embedder loaded (ChromaDB ONNX MiniLM-L6-v2)")
