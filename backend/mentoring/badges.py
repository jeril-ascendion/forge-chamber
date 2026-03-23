"""
Forge Chamber — Badge System

Checks conditions and awards badges after each session.
"""

import datetime
import logging
import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Badge, Engineer, Session

logger = logging.getLogger(__name__)

BADGE_DEFINITIONS = {
    "first_debate": {
        "label": "First Debate",
        "description": "Complete your first session",
        "icon": "🎯",
    },
    "sre_survivor": {
        "label": "SRE Survivor",
        "description": "Defend a position against Alex (SRE) successfully",
        "icon": "🛡️",
    },
    "architect_approved": {
        "label": "Architect Approved",
        "description": "Maya (Architect) agrees with your reasoning",
        "icon": "🏗️",
    },
    "streak_3": {
        "label": "3-Day Streak",
        "description": "3 consecutive days of debate",
        "icon": "🔥",
    },
    "streak_7": {
        "label": "Week Warrior",
        "description": "7 consecutive days of debate",
        "icon": "⚡",
    },
    "ten_sessions": {
        "label": "Veteran",
        "description": "Complete 10 sessions",
        "icon": "🏆",
    },
    "context_master": {
        "label": "Context Master",
        "description": "Use URL/file context in a session",
        "icon": "📚",
    },
    "quiz_ace": {
        "label": "Quiz Ace",
        "description": "Answer 5 quiz questions correctly in one session",
        "icon": "🎓",
    },
}


async def _get_earned_badges(engineer_id: str, db: AsyncSession) -> set[str]:
    result = await db.execute(
        select(Badge.badge_key).where(Badge.engineer_id == engineer_id)
    )
    return set(result.scalars().all())


async def _award(engineer_id: str, badge_key: str, db: AsyncSession) -> None:
    db.add(Badge(
        id=str(uuid.uuid4()),
        engineer_id=engineer_id,
        badge_key=badge_key,
    ))


async def check_and_award_badges(
    engineer_id: str,
    session_data: dict,
    transcript: list[dict],
    streak: int,
    db: AsyncSession,
) -> list[str]:
    """Check all badge conditions and award new ones. Returns newly earned badge keys."""
    earned = await _get_earned_badges(engineer_id, db)
    new_badges: list[str] = []
    engineer = await db.get(Engineer, engineer_id)
    if not engineer:
        return []

    total_sessions = engineer.total_sessions

    # first_debate
    if "first_debate" not in earned:
        await _award(engineer_id, "first_debate", db)
        new_badges.append("first_debate")

    # ten_sessions
    if "ten_sessions" not in earned and total_sessions >= 10:
        await _award(engineer_id, "ten_sessions", db)
        new_badges.append("ten_sessions")

    # streak_3
    if "streak_3" not in earned and streak >= 3:
        await _award(engineer_id, "streak_3", db)
        new_badges.append("streak_3")

    # streak_7
    if "streak_7" not in earned and streak >= 7:
        await _award(engineer_id, "streak_7", db)
        new_badges.append("streak_7")

    # sre_survivor: human spoke after an SRE agent challenged them
    if "sre_survivor" not in earned:
        for i, t in enumerate(transcript):
            if t.get("speaker_key") == "sre" and "?" in t.get("text", ""):
                if i + 1 < len(transcript) and transcript[i + 1].get("speaker_type") == "human":
                    await _award(engineer_id, "sre_survivor", db)
                    new_badges.append("sre_survivor")
                    break

    # architect_approved: sys_arch agent uses agreement words after human spoke
    if "architect_approved" not in earned:
        for i, t in enumerate(transcript):
            if t.get("speaker_type") == "human" and i + 1 < len(transcript):
                next_t = transcript[i + 1]
                if next_t.get("speaker_key") == "sys_arch":
                    text_lower = next_t.get("text", "").lower()
                    if any(w in text_lower for w in ["agree", "good point", "exactly", "well said", "you're right"]):
                        await _award(engineer_id, "architect_approved", db)
                        new_badges.append("architect_approved")
                        break

    # context_master: session had RAG context
    if "context_master" not in earned and session_data.get("has_context"):
        await _award(engineer_id, "context_master", db)
        new_badges.append("context_master")

    # quiz_ace: 5+ quiz answers in one session
    if "quiz_ace" not in earned:
        quiz_answers = 0
        for i, t in enumerate(transcript):
            if t.get("is_quiz_event") and i + 1 < len(transcript):
                if transcript[i + 1].get("speaker_type") == "human":
                    quiz_answers += 1
        if quiz_answers >= 5:
            await _award(engineer_id, "quiz_ace", db)
            new_badges.append("quiz_ace")

    if new_badges:
        await db.commit()
        logger.info("Awarded badges to %s: %s", engineer_id, new_badges)

    return new_badges


async def get_badges_for_engineer(engineer_id: str, db: AsyncSession) -> list[dict]:
    """Get all earned badges for an engineer."""
    result = await db.execute(
        select(Badge).where(Badge.engineer_id == engineer_id).order_by(Badge.earned_at)
    )
    badges = result.scalars().all()
    return [
        {
            "key": b.badge_key,
            "earned_at": b.earned_at.isoformat() if b.earned_at else "",
            **BADGE_DEFINITIONS.get(b.badge_key, {"label": b.badge_key, "description": "", "icon": "🏅"}),
        }
        for b in badges
    ]
