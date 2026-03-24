import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.db.models import Base


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

os.environ.setdefault("FORGE_DATA_DIR", tempfile.mkdtemp(prefix="forge-test-"))
os.environ.setdefault("FORGE_PORT", "8765")
os.environ.setdefault("GROQ_API_KEY", "test-key")
os.environ.setdefault("LIVEKIT_URL", "wss://test.example.com")
os.environ.setdefault("LIVEKIT_API_KEY", "test-api-key")
os.environ.setdefault("LIVEKIT_API_SECRET", "test-api-secret")


# ---------------------------------------------------------------------------
# Database — in-memory SQLite
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    def _enable_fk(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()

    event.listen(engine.sync_engine, "connect", _enable_fk)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


# ---------------------------------------------------------------------------
# ChromaDB — in-memory ephemeral
# ---------------------------------------------------------------------------

@pytest.fixture
def test_chroma():
    import chromadb
    client = chromadb.EphemeralClient()
    return client


# ---------------------------------------------------------------------------
# Mock Groq LLM
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_groq():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"next_speaker": "sre", "seed": "What about SLOs?", "tension_target": null}'

    mock_create = AsyncMock(return_value=mock_response)
    mock_client.chat.completions.create = mock_create

    with patch("backend.agents.orchestrator._groq_client", return_value=mock_client):
        with patch("backend.agents.synthesizer._groq_client", return_value=mock_client):
            yield mock_client, mock_create


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_engineer():
    return {"name": "Test Engineer", "role_track": "SRE", "skill_level": "mid"}


@pytest.fixture
def sample_transcript():
    return [
        {"speaker_type": "agent", "speaker_key": "sre", "speaker_name": "Alex", "speaker_role": "SRE", "text": "I'm concerned about the blast radius of this microservices approach. What's your SLO strategy?", "turn_number": 0, "is_quiz_event": False},
        {"speaker_type": "agent", "speaker_key": "sys_arch", "speaker_name": "Maya", "speaker_role": "Systems Architect", "text": "Good point Alex. The service boundaries need clear API contracts. How do you plan to version them?", "turn_number": 1, "is_quiz_event": False},
        {"speaker_type": "agent", "speaker_key": "cloud_eng", "speaker_name": "Ravi", "speaker_role": "Cloud Engineer", "text": "Before we discuss boundaries, has anyone estimated the infrastructure cost? Each service needs its own resources.", "turn_number": 2, "is_quiz_event": False},
        {"speaker_type": "human", "speaker_key": "human", "speaker_name": "Student", "speaker_role": "Engineer", "text": "We would use a service mesh for observability and target 99.9% availability.", "turn_number": 3, "is_quiz_event": False},
        {"speaker_type": "agent", "speaker_key": "sre", "speaker_name": "Alex", "speaker_role": "SRE", "text": "99.9% gives you about 8.7 hours of downtime per year. Is that acceptable for a fintech product?", "turn_number": 4, "is_quiz_event": False},
        {"speaker_type": "agent", "speaker_key": "sys_arch", "speaker_name": "Maya", "speaker_role": "Systems Architect", "text": "I agree with the service mesh approach. What about data consistency across service boundaries?", "turn_number": 5, "is_quiz_event": False},
        {"speaker_type": "human", "speaker_key": "human", "speaker_name": "Student", "speaker_role": "Engineer", "text": "We'd use the saga pattern with compensating transactions for distributed workflows.", "turn_number": 6, "is_quiz_event": False},
        {"speaker_type": "agent", "speaker_key": "cloud_eng", "speaker_name": "Ravi", "speaker_role": "Cloud Engineer", "text": "Sagas add complexity. Have you considered the IaC requirements for managing all these services?", "turn_number": 7, "is_quiz_event": False},
        {"speaker_type": "system", "speaker_key": "sre", "speaker_name": "Alex", "speaker_role": "quiz", "text": "What is the difference between orchestration and choreography in saga patterns?", "turn_number": 8, "is_quiz_event": True},
        {"speaker_type": "human", "speaker_key": "human", "speaker_name": "Student", "speaker_role": "Engineer", "text": "Orchestration has a central coordinator, while choreography relies on event-driven communication between services.", "turn_number": 9, "is_quiz_event": False},
    ]


# ---------------------------------------------------------------------------
# FastAPI test client
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def test_client(test_db):
    from httpx import ASGITransport, AsyncClient
    from backend.main import app
    from backend.db.database import get_db

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()
