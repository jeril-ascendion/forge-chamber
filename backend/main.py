import io
import logging
import os
import signal
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Fix for PyInstaller bundled exe with console=False:
# sys.stdout/stderr are None when there's no console window.
# Uvicorn's logger crashes on sys.stdout.isatty(). Redirect to devnull.
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes.engineer import router as engineer_router
from backend.api.routes.health import router as health_router
from backend.api.routes.progress import router as progress_router
from backend.api.routes.rag import router as rag_router
from backend.api.routes.session import router as session_router
from backend.core.config import settings
from backend.core.logging import setup_logging
from backend.db.database import init_db

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    await init_db()
    # Load embedding model + init ChromaDB (before any routes)
    from backend.rag.embedder import load_embedder, get_chroma_collection

    load_embedder()
    get_chroma_collection(settings.forge_data_dir)
    logger.info(
        "Forge Chamber backend ready on port %s (data_dir=%s)",
        settings.forge_port,
        settings.forge_data_dir,
    )
    yield
    # Shutdown
    logger.info("Forge Chamber backend shutting down")


app = FastAPI(
    title="Forge Chamber",
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS — localhost only
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8765",
        "http://127.0.0.1:8765",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health_router)
app.include_router(engineer_router)
app.include_router(session_router)
app.include_router(rag_router)
app.include_router(progress_router)


# Global exception handler — always return JSON, never HTML
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )


# Graceful shutdown on SIGTERM
def _handle_sigterm(signum: int, frame: object) -> None:
    logger.info("Received SIGTERM, shutting down gracefully")
    sys.exit(0)


signal.signal(signal.SIGTERM, _handle_sigterm)


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=settings.forge_port,
        reload=True,
    )
