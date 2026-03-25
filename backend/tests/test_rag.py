"""Tests for the RAG pipeline: ingestion, retrieval, source management."""

import pytest

from backend.rag.embedder import embed, load_embedder
from backend.rag.retriever import retrieve_context


@pytest.fixture(autouse=True)
def _init_embedder():
    load_embedder()


@pytest.fixture
def data_dir(tmp_path):
    return str(tmp_path)


def test_embed_returns_vectors():
    vecs = embed(["hello world", "test embedding"])
    assert len(vecs) == 2
    assert len(vecs[0]) == 384  # BAAI/bge-small-en-v1.5 outputs 384-dim


def test_ingest_file_txt(data_dir):
    from backend.rag.ingester import ingest_file

    content = ("Microservices architecture enables independent deployment. " * 50).encode()
    result = ingest_file(content, "test-article.txt", data_dir)

    assert result["status"] == "ingested"
    assert result["chunks"] >= 1
    assert result["title"] == "test article"


def test_ingest_file_md(data_dir):
    from backend.rag.ingester import ingest_file

    content = "# Architecture\n\nThis is a test document about system design.\n" * 20
    result = ingest_file(content.encode(), "design-doc.md", data_dir)

    assert result["status"] == "ingested"
    assert result["chunks"] >= 1


def test_retrieve_context_empty(data_dir):
    """Empty collection returns empty string, no error."""
    result = retrieve_context("microservices", data_dir, n=4)
    assert result == ""


def test_retrieve_context_returns_formatted_block(data_dir):
    from backend.rag.ingester import ingest_file

    content = ("Microservices break a monolith into independently deployable services. " * 30).encode()
    ingest_file(content, "micro.txt", data_dir)

    result = retrieve_context("microservices deployment", data_dir, n=2)

    assert "== REFERENCE MATERIAL ==" in result
    assert "[From:" in result
    assert "== END REFERENCE MATERIAL ==" in result


def test_list_and_delete_sources(data_dir):
    from backend.rag.ingester import ingest_file, list_ingested_sources, delete_source

    ingest_file(b"Test content one " * 50, "file1.txt", data_dir)
    ingest_file(b"Test content two " * 50, "file2.txt", data_dir)

    sources = list_ingested_sources(data_dir)
    assert len(sources) == 2

    # Delete first source
    deleted = delete_source(sources[0]["id"], data_dir)
    assert deleted is True

    remaining = list_ingested_sources(data_dir)
    assert len(remaining) == 1

    # Delete nonexistent
    deleted = delete_source("nonexistent-id", data_dir)
    assert deleted is False
