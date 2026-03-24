"""Tests for the database layer: models, CRUD operations, skill scoring."""

import uuid

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from backend.db.models import Engineer, Room, Session, SkillScore, Badge
from backend.mentoring.skills_engine import update_skill_scores


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


async def test_init_db_creates_tables(test_db):
    """All required tables exist after init."""
    result = await test_db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = {row[0] for row in result.fetchall()}
    expected = {"engineers", "skill_scores", "rooms", "sessions", "turns", "badges"}
    assert expected.issubset(tables)


# ---------------------------------------------------------------------------
# Engineer CRUD
# ---------------------------------------------------------------------------


async def test_create_engineer(test_db):
    engineer = Engineer(
        id=str(uuid.uuid4()), name="Alice", role_track="SRE", skill_level="mid",
    )
    test_db.add(engineer)
    await test_db.commit()
    await test_db.refresh(engineer)

    assert engineer.name == "Alice"
    assert engineer.total_xp == 0
    assert engineer.total_sessions == 0


async def test_get_engineer_not_found(test_db):
    result = await test_db.get(Engineer, "nonexistent-id")
    assert result is None


async def test_update_xp(test_db):
    engineer = Engineer(id=str(uuid.uuid4()), name="Bob", role_track="Java Developer")
    test_db.add(engineer)
    await test_db.commit()

    engineer.total_xp += 100
    await test_db.commit()
    await test_db.refresh(engineer)

    assert engineer.total_xp == 100


# ---------------------------------------------------------------------------
# Session CRUD
# ---------------------------------------------------------------------------


async def test_create_and_get_session(test_db):
    import datetime

    eng_id = str(uuid.uuid4())
    room_id = str(uuid.uuid4())
    sess_id = str(uuid.uuid4())

    test_db.add(Engineer(id=eng_id, name="Carol", role_track="Cloud Engineer"))
    test_db.add(Room(id=room_id, engineer_id=eng_id, topic="Test", agents="[]", user_role="Eng"))
    await test_db.commit()

    session = Session(
        id=sess_id, room_id=room_id, engineer_id=eng_id,
        started_at=datetime.datetime.utcnow(),
    )
    test_db.add(session)
    await test_db.commit()

    fetched = await test_db.get(Session, sess_id)
    assert fetched is not None
    assert fetched.engineer_id == eng_id


async def test_foreign_key_constraints(test_db):
    import datetime

    session = Session(
        id=str(uuid.uuid4()),
        room_id="nonexistent-room",
        engineer_id="nonexistent-eng",
        started_at=datetime.datetime.utcnow(),
    )
    test_db.add(session)
    with pytest.raises(IntegrityError):
        await test_db.commit()
    await test_db.rollback()


# ---------------------------------------------------------------------------
# Skill score tests
# ---------------------------------------------------------------------------


async def test_update_skill_scores_first_session(test_db):
    eng_id = str(uuid.uuid4())
    test_db.add(Engineer(id=eng_id, name="Dan", role_track="SRE"))
    await test_db.commit()

    scores = {"technical_depth": 4.0, "communication": 3.5, "debate_resilience": 3.0, "ai_native": 2.5}
    result = await update_skill_scores(eng_id, scores, test_db)

    assert result["technical_depth"] == 4.0
    assert result["communication"] == 3.5


async def test_update_skill_scores_rolling_average(test_db):
    eng_id = str(uuid.uuid4())
    test_db.add(Engineer(id=eng_id, name="Eve", role_track="SRE"))
    await test_db.commit()

    # First session: baseline at 3.0
    await update_skill_scores(eng_id, {"technical_depth": 3.0}, test_db)

    # Second session: higher score → weighted avg, no floor needed
    result = await update_skill_scores(eng_id, {"technical_depth": 4.5}, test_db)

    # Expected: 3.0 * 0.70 + 4.5 * 0.30 = 2.1 + 1.35 = 3.45
    assert abs(result["technical_depth"] - 3.45) < 0.01


async def test_update_skill_scores_floor_mechanism(test_db):
    eng_id = str(uuid.uuid4())
    test_db.add(Engineer(id=eng_id, name="Frank", role_track="SRE"))
    await test_db.commit()

    # First session: baseline at 4.0
    await update_skill_scores(eng_id, {"technical_depth": 4.0}, test_db)

    # Second session: score tries to drop to 1.0
    # Raw: 4.0 * 0.70 + 1.0 * 0.30 = 3.1
    # Floor: 4.0 - 0.5 = 3.5
    # Result should be max(3.1, 3.5) = 3.5
    result = await update_skill_scores(eng_id, {"technical_depth": 1.0}, test_db)

    assert abs(result["technical_depth"] - 3.5) < 0.01
