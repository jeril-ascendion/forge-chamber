from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.models import SessionProgressItem, SkillScoresResponse
from backend.db.crud import get_engineer, get_sessions_for_engineer, get_skill_scores
from backend.db.database import get_db

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/skills", response_model=SkillScoresResponse)
async def skills(
    db: AsyncSession = Depends(get_db),
) -> SkillScoresResponse:
    engineer = await get_engineer(db)
    if not engineer:
        return SkillScoresResponse(
            technical_depth=0,
            communication=0,
            debate_resilience=0,
            ai_native=0,
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

    sessions = await get_sessions_for_engineer(db, engineer.id)
    return [
        SessionProgressItem(
            date=s.started_at.isoformat() if s.started_at else "",
            topic=None,  # Would require join to rooms — kept simple for now
            xp=s.xp_earned,
            scores={
                "technical_depth": s.technical_depth_score,
                "communication": s.communication_score,
                "debate_resilience": s.debate_resilience_score,
                "ai_native": s.ai_native_score,
            },
        )
        for s in sessions
    ]
