"""Tests for agent personas, orchestrator, synthesizer, XP, and badges."""

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agents.personas import PERSONAS, format_system_prompt
from backend.mentoring.skills_engine import calculate_xp


# ---------------------------------------------------------------------------
# Persona definitions
# ---------------------------------------------------------------------------


def test_persona_definitions():
    expected_keys = {"sre", "sys_arch", "cloud_eng", "java_dev", "ui_dev"}
    assert set(PERSONAS.keys()) == expected_keys

    required_fields = {"name", "role", "voice_id", "system", "greeting", "quiz_topics", "disagreement_triggers", "color"}
    for key, persona in PERSONAS.items():
        for field in required_fields:
            assert field in persona, f"{key} missing field: {field}"


def test_persona_system_prompts_contain_question_instruction():
    for key, persona in PERSONAS.items():
        assert "question" in persona["system"].lower(), f"{key} prompt missing question instruction"


def test_persona_quiz_topics_minimum():
    for key, persona in PERSONAS.items():
        assert len(persona["quiz_topics"]) >= 5, f"{key} has only {len(persona['quiz_topics'])} quiz topics"


def test_persona_disagreement_triggers_minimum():
    for key, persona in PERSONAS.items():
        assert len(persona["disagreement_triggers"]) >= 7, f"{key} has only {len(persona['disagreement_triggers'])} triggers"


def test_format_system_prompt_injects_topic():
    prompt = format_system_prompt("sre", topic="Microservices", transcript="test")
    assert "Microservices" in prompt


def test_format_system_prompt_injects_rag_context():
    prompt = format_system_prompt("sre", topic="Test", rag_context="RAG chunk here", transcript="")
    assert "REFERENCE MATERIAL" in prompt
    assert "RAG chunk here" in prompt


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


async def test_orchestrator_route_turn_fallback(mock_groq):
    """When Groq returns invalid JSON, fallback to round-robin."""
    from backend.agents.orchestrator import route_turn, initial_state

    _, mock_create = mock_groq
    mock_create.return_value.choices[0].message.content = "invalid json!!!"

    state = initial_state("Test topic", ["sre", "sys_arch"], "sess-1")
    state = await route_turn(state)

    assert state["active_speaker"] in ["sre", "sys_arch"]


async def test_orchestrator_no_same_agent_twice(mock_groq):
    """route_turn never returns same agent as last speaker."""
    from backend.agents.orchestrator import route_turn, initial_state

    _, mock_create = mock_groq

    state = initial_state("Test", ["sre", "sys_arch", "cloud_eng"], "sess-1")
    for i in range(8):
        # Set last speaker
        if state["active_speaker"]:
            state["transcript"].append({
                "speaker_key": state["active_speaker"],
                "speaker_name": "Agent",
                "text": f"Turn {i}",
                "turn_number": i,
            })

        # Make Groq return the SAME agent as last speaker (should be rejected)
        last = state["transcript"][-1]["speaker_key"] if state["transcript"] else None
        mock_create.return_value.choices[0].message.content = json.dumps({
            "next_speaker": last or "sre", "seed": "test", "tension_target": None
        })

        state = await route_turn(state)
        if last:
            assert state["active_speaker"] != last, f"Same agent twice at turn {i}"


# ---------------------------------------------------------------------------
# Synthesizer
# ---------------------------------------------------------------------------


async def test_synthesizer_returns_valid_structure(mock_groq, sample_transcript):
    from backend.agents.synthesizer import synthesize_session

    _, mock_create = mock_groq
    mock_create.return_value.choices[0].message.content = json.dumps({
        "key_insights": ["Insight 1", "Insight 2", "Insight 3"],
        "strong_moments": [{"turn": 3, "observation": "Good point"}],
        "knowledge_gaps": [{"topic": "CAP theorem", "suggested_study": "Read Brewer's paper"}],
        "scores": {"technical_depth": 4.0, "communication": 3.5, "debate_resilience": 3.0, "ai_native": 2.5},
        "overall_comment": "Solid session.",
    })

    result = await synthesize_session(sample_transcript)

    assert "key_insights" in result
    assert "scores" in result
    assert len(result["key_insights"]) == 3
    for domain in ["technical_depth", "communication", "debate_resilience", "ai_native"]:
        assert domain in result["scores"]
        assert 1.0 <= result["scores"][domain] <= 5.0


async def test_synthesizer_handles_json_failure(mock_groq, sample_transcript):
    from backend.agents.synthesizer import synthesize_session

    _, mock_create = mock_groq
    mock_create.return_value.choices[0].message.content = "not valid json at all"

    result = await synthesize_session(sample_transcript)

    # Should return fallback debrief, not raise
    assert "scores" in result
    assert result["scores"]["technical_depth"] == 2.0  # fallback score


# ---------------------------------------------------------------------------
# XP calculation
# ---------------------------------------------------------------------------


def test_calculate_xp_base():
    result = calculate_xp(transcript=[], duration_seconds=0, streak=0)
    assert result["total"] == 50
    assert result["breakdown"]["base"] == 50


def test_calculate_xp_with_participation(sample_transcript):
    result = calculate_xp(transcript=sample_transcript, duration_seconds=0, streak=0)
    human_turns = sum(1 for t in sample_transcript if t["speaker_type"] == "human")
    assert result["breakdown"]["participation"] == human_turns * 10


def test_calculate_xp_full_session_bonus():
    result = calculate_xp(transcript=[], duration_seconds=900, streak=0)
    assert result["breakdown"]["duration_bonus"] == 20


def test_calculate_xp_streak_bonus():
    result = calculate_xp(transcript=[], duration_seconds=0, streak=5)
    assert result["breakdown"]["streak"] == 50


# ---------------------------------------------------------------------------
# Badges
# ---------------------------------------------------------------------------


async def test_badges_first_debate(test_db):
    from backend.db.models import Engineer
    from backend.mentoring.badges import check_and_award_badges

    eng_id = str(uuid.uuid4())
    test_db.add(Engineer(id=eng_id, name="Test", role_track="SRE", total_sessions=1))
    await test_db.commit()

    new = await check_and_award_badges(eng_id, {}, [], 1, test_db)
    assert "first_debate" in new


async def test_badges_no_duplicates(test_db):
    from backend.db.models import Engineer
    from backend.mentoring.badges import check_and_award_badges

    eng_id = str(uuid.uuid4())
    test_db.add(Engineer(id=eng_id, name="Test", role_track="SRE", total_sessions=1))
    await test_db.commit()

    first = await check_and_award_badges(eng_id, {}, [], 1, test_db)
    second = await check_and_award_badges(eng_id, {}, [], 1, test_db)

    assert "first_debate" in first
    assert "first_debate" not in second  # no duplicate
