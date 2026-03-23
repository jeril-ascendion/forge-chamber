import logging
from pathlib import Path

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.core.config import settings
from backend.db.models import Base

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def _enable_foreign_keys(dbapi_conn, connection_record):  # type: ignore[no-untyped-def]
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


async def init_db() -> None:
    """Create all tables and enable foreign keys. Idempotent."""
    # Ensure the data directory exists
    db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    # Enable foreign keys on every connection
    event.listen(engine.sync_engine, "connect", _enable_foreign_keys)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database initialized at %s", db_path)


async def get_db() -> AsyncSession:  # type: ignore[misc]
    """Dependency for FastAPI route injection."""
    async with async_session() as session:
        yield session
