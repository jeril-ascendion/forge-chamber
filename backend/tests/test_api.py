"""Tests for FastAPI API routes — happy paths and error cases."""

import pytest


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


async def test_health_endpoint(test_client):
    res = await test_client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"


# ---------------------------------------------------------------------------
# Engineer
# ---------------------------------------------------------------------------


async def test_engineer_profile_not_found(test_client):
    res = await test_client.get("/engineer/profile")
    assert res.status_code == 404


async def test_engineer_setup(test_client):
    res = await test_client.post("/engineer/setup", json={
        "name": "Test User", "role_track": "SRE", "skill_level": "mid",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Test User"
    assert data["role_track"] == "SRE"
    assert "id" in data


async def test_engineer_setup_missing_name(test_client):
    res = await test_client.post("/engineer/setup", json={
        "role_track": "SRE",
    })
    assert res.status_code == 422


async def test_engineer_profile_after_setup(test_client):
    await test_client.post("/engineer/setup", json={
        "name": "Alice", "role_track": "Cloud Engineer", "skill_level": "senior",
    })
    res = await test_client.get("/engineer/profile")
    assert res.status_code == 200
    assert res.json()["name"] == "Alice"


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------


async def test_session_list_empty(test_client):
    res = await test_client.get("/session/list")
    assert res.status_code == 200
    assert res.json() == []


async def test_session_start_no_engineer(test_client):
    res = await test_client.post("/session/start", json={
        "topic": "Test", "agents": ["sre"], "user_role": "Engineer",
    })
    assert res.status_code == 400


# ---------------------------------------------------------------------------
# RAG
# ---------------------------------------------------------------------------


async def test_rag_sources_empty(test_client):
    res = await test_client.get("/rag/sources")
    assert res.status_code == 200
    assert res.json() == []


async def test_rag_delete_nonexistent(test_client):
    res = await test_client.delete("/rag/source/nonexistent-id")
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# Progress
# ---------------------------------------------------------------------------


async def test_progress_skills_no_sessions(test_client):
    res = await test_client.get("/progress/skills")
    assert res.status_code == 200
    data = res.json()
    assert data["technical_depth"] == 0
    assert data["communication"] == 0


async def test_progress_sessions_empty(test_client):
    res = await test_client.get("/progress/sessions")
    assert res.status_code == 200
    assert res.json() == []


async def test_progress_summary(test_client):
    res = await test_client.get("/progress/summary")
    assert res.status_code == 200
    data = res.json()
    assert "skills" in data
    assert "total_xp" in data
    assert "badges" in data
