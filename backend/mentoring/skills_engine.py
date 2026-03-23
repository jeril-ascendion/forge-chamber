"""
Forge Chamber — Skills Engine

Weighted skill score updates, XP calculation with breakdown,
and streak tracking.
"""

import datetime
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Engineer, SkillScore

logger = logging.getLogger(__name__)

SKILL_DOMAINS = ["technical_depth", "communication", "debate_resilience", "ai_native"]
WEIGHT_EXISTING = 0.70
WEIGHT_NEW = 0.30
MAX_DROP_PER_SESSION = 0.5


async def update_skill_scores(
    engineer_id: str,
    new_scores: dict[str, float],
    db: AsyncSession,
) -> dict[str, float]:
    """Update skill scores using rolling weighted average.

    First session: scores stored directly as baseline.
    Subsequent: new_avg = existing * 0.70 + new * 0.30
    Floor: score cannot drop more than 0.5 in one session.
    """
    updated: dict[str, float] = {}

    for domain in SKILL_DOMAINS:
        new_val = new_scores.get(domain, 0.0)
        new_val = max(1.0, min(5.0, new_val))

        result = await db.execute(
            select(SkillScore).where(
                SkillScore.engineer_id == engineer_id,
                SkillScore.domain == domain,
            )
        )
        existing = result.scalar_one_or_none()

        if existing and existing.session_count > 0:
            # Weighted average
            raw = existing.score * WEIGHT_EXISTING + new_val * WEIGHT_NEW

            # Floor: can't drop more than 0.5
            floor = existing.score - MAX_DROP_PER_SESSION
            final = max(raw, floor)
            final = max(1.0, min(5.0, final))

            existing.score = final
            existing.session_count += 1
            existing.updated_at = datetime.datetime.utcnow()
            updated[domain] = final
        elif existing:
            # First real session — store as baseline
            existing.score = new_val
            existing.session_count = 1
            existing.updated_at = datetime.datetime.utcnow()
            updated[domain] = new_val
        else:
            # No row yet — create
            db.add(SkillScore(
                id=str(uuid.uuid4()),
                engineer_id=engineer_id,
                domain=domain,
                score=new_val,
                session_count=1,
            ))
            updated[domain] = new_val

    await db.commit()
    logger.info("Updated skills for %s: %s", engineer_id, updated)
    return updated


def calculate_xp(
    transcript: list[dict],
    duration_seconds: int = 0,
    streak: int = 0,
) -> dict:
    """Calculate XP earned from a session with full breakdown."""
    base = 50

    # Participation: +10 per human turn, max 100
    human_turns = sum(1 for t in transcript if t.get("speaker_type") == "human")
    participation = min(human_turns * 10, 100)

    # Quiz: +15 per answered quiz (human spoke right after quiz event)
    quiz_xp = 0
    for i, t in enumerate(transcript):
        if t.get("is_quiz_event"):
            if i + 1 < len(transcript) and transcript[i + 1].get("speaker_type") == "human":
                quiz_xp += 15

    # Duration: +20 if >= 15 minutes
    duration_bonus = 20 if duration_seconds >= 900 else 0

    # Streak: +10 per consecutive day, max 70
    streak_bonus = min(streak * 10, 70)

    total = base + participation + quiz_xp + duration_bonus + streak_bonus

    return {
        "total": total,
        "breakdown": {
            "base": base,
            "participation": participation,
            "quiz": quiz_xp,
            "duration_bonus": duration_bonus,
            "streak": streak_bonus,
        },
    }


async def get_current_streak(engineer_id: str, db: AsyncSession) -> int:
    """Calculate current session streak for an engineer."""
    engineer = await db.get(Engineer, engineer_id)
    if not engineer or not engineer.last_session_date:
        return 1

    try:
        last_date = datetime.date.fromisoformat(engineer.last_session_date)
    except ValueError:
        return 1

    today = datetime.date.today()
    delta = (today - last_date).days

    if delta == 0:
        # Same day — streak stays (return current count based on sessions)
        return max(1, min(engineer.total_sessions, 7))
    elif delta == 1:
        # Yesterday — streak continues
        return max(1, min(engineer.total_sessions, 7))
    else:
        # Gap > 1 day — streak resets
        return 1
