import logging

from fastapi import APIRouter, HTTPException, UploadFile

from backend.api.models import (
    DeleteSourceResponse,
    IngestResponse,
    IngestUrlRequest,
    RagSourceResponse,
)
from backend.core.config import settings
from backend.rag.ingester import (
    delete_source as do_delete_source,
    ingest_file as do_ingest_file,
    ingest_url as do_ingest_url,
    list_ingested_sources,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/ingest-url", response_model=IngestResponse)
async def ingest_url(body: IngestUrlRequest) -> IngestResponse:
    """Ingest a URL into the RAG pipeline."""
    try:
        result = do_ingest_url(body.url, settings.forge_data_dir)
        return IngestResponse(
            status=result["status"],
            chunks=result["chunks"],
            title=result["title"],
        )
    except Exception as exc:
        logger.error("URL ingestion failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")


@router.post("/ingest-file", response_model=IngestResponse)
async def ingest_file(file: UploadFile) -> IngestResponse:
    """Ingest an uploaded file into the RAG pipeline."""
    filename = file.filename or "unnamed"
    try:
        content = await file.read()
        result = do_ingest_file(content, filename, settings.forge_data_dir)
        return IngestResponse(
            status=result["status"],
            chunks=result["chunks"],
            title=result["title"],
        )
    except Exception as exc:
        logger.error("File ingestion failed for %s: %s", filename, exc)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")


@router.get("/sources", response_model=list[RagSourceResponse])
async def list_sources() -> list[RagSourceResponse]:
    """List all ingested sources."""
    sources = list_ingested_sources(settings.forge_data_dir)
    return [
        RagSourceResponse(
            id=s["id"],
            label=s["label"],
            chunks=s["chunks"],
            ingested_at=s["ingested_at"],
        )
        for s in sources
    ]


@router.delete("/source/{source_id}", response_model=DeleteSourceResponse)
async def delete_source(source_id: str) -> DeleteSourceResponse:
    """Delete a source and its chunks from the RAG pipeline."""
    deleted = do_delete_source(source_id, settings.forge_data_dir)
    if not deleted:
        raise HTTPException(status_code=404, detail="Source not found.")
    return DeleteSourceResponse(status="deleted")
