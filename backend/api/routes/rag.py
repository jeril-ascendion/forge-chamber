import json
import logging
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from backend.api.models import (
    DeleteSourceResponse,
    IngestResponse,
    IngestUrlRequest,
    RagSourceResponse,
)
from backend.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rag", tags=["rag"])

SOURCES_FILE = Path(settings.forge_data_dir) / "sources.json"


def _load_sources() -> list[dict]:
    if SOURCES_FILE.exists():
        return json.loads(SOURCES_FILE.read_text())
    return []


def _save_sources(sources: list[dict]) -> None:
    SOURCES_FILE.parent.mkdir(parents=True, exist_ok=True)
    SOURCES_FILE.write_text(json.dumps(sources, indent=2))


@router.post("/ingest-url", response_model=IngestResponse)
async def ingest_url(body: IngestUrlRequest) -> IngestResponse:
    """Ingest a URL into the RAG pipeline. Full implementation in E6."""
    source_id = str(uuid.uuid4())
    sources = _load_sources()
    sources.append({
        "id": source_id,
        "label": body.url,
        "chunks": 0,
        "ingested_at": datetime.utcnow().isoformat(),
    })
    _save_sources(sources)

    logger.info("RAG ingest-url stub: %s", body.url)
    return IngestResponse(status="ingested", chunks=0, title=body.url)


@router.post("/ingest-file", response_model=IngestResponse)
async def ingest_file(file: UploadFile) -> IngestResponse:
    """Ingest an uploaded file into the RAG pipeline. Full implementation in E6."""
    source_id = str(uuid.uuid4())
    filename = file.filename or "unnamed"

    sources = _load_sources()
    sources.append({
        "id": source_id,
        "label": filename,
        "chunks": 0,
        "ingested_at": datetime.utcnow().isoformat(),
    })
    _save_sources(sources)

    logger.info("RAG ingest-file stub: %s", filename)
    return IngestResponse(status="ingested", chunks=0, title=filename)


@router.get("/sources", response_model=list[RagSourceResponse])
async def list_sources() -> list[RagSourceResponse]:
    sources = _load_sources()
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
    sources = _load_sources()
    filtered = [s for s in sources if s["id"] != source_id]
    if len(filtered) == len(sources):
        raise HTTPException(status_code=404, detail="Source not found.")
    _save_sources(filtered)
    return DeleteSourceResponse(status="deleted")
