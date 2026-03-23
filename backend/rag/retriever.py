"""
Forge Chamber — Semantic Retrieval

Queries ChromaDB for relevant context chunks to inject
into agent system prompts during debate.
"""

import logging

from backend.rag.embedder import get_chroma_collection

logger = logging.getLogger(__name__)


def retrieve_context(query: str, data_dir: str, n: int = 4) -> str:
    """Retrieve top-N relevant chunks from ChromaDB and format as a context block.

    Returns empty string if no results or collection is empty.
    """
    try:
        collection = get_chroma_collection(data_dir)
        count = collection.count()
        if count == 0:
            return ""

        results = collection.query(
            query_texts=[query],
            n_results=min(n, count),
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        if not documents:
            return ""

        # Format as context block
        blocks = []
        for doc, meta in zip(documents, metadatas):
            source_label = meta.get("source_label", "unknown source")
            blocks.append(f"[From: {source_label}]\n{doc}")

        context = (
            "== REFERENCE MATERIAL ==\n"
            "Ground your response in this material where relevant. "
            "Do not quote directly — reason from it.\n\n"
            + "\n\n".join(blocks)
            + "\n== END REFERENCE MATERIAL =="
        )

        logger.debug("Retrieved %d chunks for query: %s...", len(documents), query[:60])
        return context

    except Exception as exc:
        logger.warning("RAG retrieval failed: %s", exc)
        return ""


def retrieve_for_agent_turn(last_utterances: list[str], data_dir: str) -> str:
    """Retrieve context for an agent turn using the last 2 utterances as query.

    Returns formatted context block or empty string.
    """
    if not last_utterances:
        return ""

    query = " ".join(last_utterances[-2:])
    return retrieve_context(query, data_dir, n=4)
