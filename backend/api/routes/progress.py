from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.models import (
    BadgeResponse,
    ProgressSummaryResponse,
    SessionProgressItem,
    SkillScoresResponse,
)
from backend.db.crud import get_engineer, get_sessions_for_engineer, get_skill_scores
from backend.db.database import get_db
from backend.db.models import Room, Session
from backend.mentoring.badges import get_badges_for_engineer
from backend.mentoring.skills_engine import get_current_streak

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/skills", response_model=SkillScoresResponse)
async def skills(
    db: AsyncSession = Depends(get_db),
) -> SkillScoresResponse:
    engineer = await get_engineer(db)
    if not engineer:
        return SkillScoresResponse(
            technical_depth=0, communication=0, debate_resilience=0, ai_native=0,
        )

    scores = await get_skill_scores(db, engineer.id)
    return SkillScoresResponse(
        technical_depth=scores.get("technical_depth", 0),
        communication=scores.get("communication", 0),
        debate_resilience=scores.get("debate_resilience", 0),
        ai_native=scores.get("ai_native", 0),
    )


@router.get("/sessions", response_model=list[SessionProgressItem])
async def session_history(
    db: AsyncSession = Depends(get_db),
) -> list[SessionProgressItem]:
    engineer = await get_engineer(db)
    if not engineer:
        return []

    # Join sessions with rooms to get topic
    result = await db.execute(
        select(Session, Room.topic)
        .join(Room, Session.room_id == Room.id, isouter=True)
        .where(Session.engineer_id == engineer.id)
        .order_by(Session.started_at.desc())
        .limit(50)
    )
    rows = result.all()

    return [
        SessionProgressItem(
            session_id=s.id,
            date=s.started_at.isoformat() if s.started_at else "",
            topic=topic,
            duration_seconds=s.duration_seconds,
            xp=s.xp_earned,
            scores={
                "technical_depth": s.technical_depth_score,
                "communication": s.communication_score,
                "debate_resilience": s.debate_resilience_score,
                "ai_native": s.ai_native_score,
            },
        )
        for s, topic in rows
    ]


@router.get("/summary", response_model=ProgressSummaryResponse)
async def summary(
    db: AsyncSession = Depends(get_db),
) -> ProgressSummaryResponse:
    engineer = await get_engineer(db)
    if not engineer:
        return ProgressSummaryResponse(
            skills=SkillScoresResponse(
                technical_depth=0, communication=0, debate_resilience=0, ai_native=0,
            ),
            total_xp=0,
            total_sessions=0,
            current_streak=0,
            badges=[],
        )

    scores = await get_skill_scores(db, engineer.id)
    streak = await get_current_streak(engineer.id, db)
    badges_raw = await get_badges_for_engineer(engineer.id, db)
    badges = [
        BadgeResponse(
            key=b["key"],
            label=b["label"],
            description=b["description"],
            icon=b["icon"],
            earned_at=b["earned_at"],
        )
        for b in badges_raw
    ]

    return ProgressSummaryResponse(
        skills=SkillScoresResponse(
            technical_depth=scores.get("technical_depth", 0),
            communication=scores.get("communication", 0),
            debate_resilience=scores.get("debate_resilience", 0),
            ai_native=scores.get("ai_native", 0),
        ),
        total_xp=engineer.total_xp,
        total_sessions=engineer.total_sessions,
        current_streak=streak,
        badges=badges,
    )
