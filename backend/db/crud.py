import datetime
import json
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.db.models import Engineer, Room, Session, SkillScore, Turn

SKILL_DOMAINS = [
    "technical_depth",
    "communication",
    "debate_resilience",
    "ai_native",
]

# ---------------------------------------------------------------------------
# Engineer ID persistence
# ---------------------------------------------------------------------------

_engineer_id_file = Path(settings.forge_data_dir) / "engineer_id.txt"


def _read_persisted_engineer_id() -> str | None:
    if _engineer_id_file.exists():
        return _engineer_id_file.read_text().strip() or None
    return None


def _persist_engineer_id(engineer_id: str) -> None:
    _engineer_id_file.parent.mkdir(parents=True, exist_ok=True)
    _engineer_id_file.write_text(engineer_id)


# ---------------------------------------------------------------------------
# Engineer CRUD
# ---------------------------------------------------------------------------


async def create_engineer(
    db: AsyncSession,
    name: str,
    role_track: str,
    skill_level: str = "mid",
) -> Engineer:
    engineer_id = _read_persisted_engineer_id() or str(uuid.uuid4())

    # Check if engineer already exists (re-setup scenario)
    existing = await db.get(Engineer, engineer_id)
    if existing:
        existing.name = name
        existing.role_track = role_track
        existing.skill_level = skill_level
        await db.commit()
        await db.refresh(existing)
        return existing

    engineer = Engineer(
        id=engineer_id,
        name=name,
        role_track=role_track,
        skill_level=skill_level,
    )
    db.add(engineer)
    await db.commit()
    await db.refresh(engineer)

    _persist_engineer_id(engineer.id)

    # Initialize skill scores at 0
    for domain in SKILL_DOMAINS:
        score = SkillScore(
            id=str(uuid.uuid4()),
            engineer_id=engineer.id,
            domain=domain,
            score=0.0,
            session_count=0,
        )
        db.add(score)
    await db.commit()

    return engineer


async def get_engineer(db: AsyncSession) -> Engineer | None:
    engineer_id = _read_persisted_engineer_id()
    if not engineer_id:
        return None
    return await db.get(Engineer, engineer_id)


async def update_xp(db: AsyncSession, engineer_id: str, xp: int) -> None:
    engineer = await db.get(Engineer, engineer_id)
    if engineer:
        engineer.total_xp += xp
        engineer.total_sessions += 1
        await db.commit()


# ---------------------------------------------------------------------------
# Skill scores
# ---------------------------------------------------------------------------


async def get_skill_scores(db: AsyncSession, engineer_id: str) -> dict[str, float]:
    result = await db.execute(
        select(SkillScore).where(SkillScore.engineer_id == engineer_id)
    )
    scores = result.scalars().all()
    return {s.domain: s.score for s in scores}


async def update_skill_scores(
    db: AsyncSession,
    engineer_id: str,
    scores: dict[str, float],
) -> None:
    for domain, new_score in scores.items():
        result = await db.execute(
            select(SkillScore).where(
                SkillScore.engineer_id == engineer_id,
                SkillScore.domain == domain,
            )
        )
        skill = result.scalar_one_or_none()
        if skill:
            # Running average weighted by session count
            total = skill.score * skill.session_count + new_score
            skill.session_count += 1
            skill.score = total / skill.session_count
            skill.updated_at = datetime.datetime.utcnow()
        else:
            db.add(
                SkillScore(
                    id=str(uuid.uuid4()),
                    engineer_id=engineer_id,
                    domain=domain,
                    score=new_score,
                    session_count=1,
                )
            )
    await db.commit()


# ---------------------------------------------------------------------------
# Room
# ---------------------------------------------------------------------------


async def create_room(
    db: AsyncSession,
    engineer_id: str,
    topic: str,
    agents: list[str],
    user_role: str,
    context_sources: list[str] | None = None,
) -> Room:
    room = Room(
        id=str(uuid.uuid4()),
        engineer_id=engineer_id,
        topic=topic,
        agents=json.dumps(agents),
        user_role=user_role,
        context_sources=json.dumps(context_sources) if context_sources else None,
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------


async def create_session(
    db: AsyncSession,
    room_id: str,
    engineer_id: str,
) -> Session:
    session = Session(
        id=str(uuid.uuid4()),
        room_id=room_id,
        engineer_id=engineer_id,
        started_at=datetime.datetime.utcnow(),
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_session(db: AsyncSession, session_id: str) -> Session | None:
    return await db.get(Session, session_id)


async def end_session(
    db: AsyncSession,
    session_id: str,
    transcript: str,
    debrief: str,
    scores: dict[str, float],
    xp_earned: int,
) -> Session | None:
    session = await db.get(Session, session_id)
    if not session:
        return None
    session.ended_at = datetime.datetime.utcnow()
    if session.started_at:
        delta = session.ended_at - session.started_at
        session.duration_seconds = int(delta.total_seconds())
    session.transcript = transcript
    session.debrief = debrief
    session.xp_earned = xp_earned
    session.technical_depth_score = scores.get("technical_depth")
    session.communication_score = scores.get("communication")
    session.debate_resilience_score = scores.get("debate_resilience")
    session.ai_native_score = scores.get("ai_native")
    await db.commit()
    await db.refresh(session)
    return session


async def get_sessions_for_engineer(
    db: AsyncSession,
    engineer_id: str,
) -> list[Session]:
    result = await db.execute(
        select(Session)
        .where(Session.engineer_id == engineer_id)
        .order_by(Session.started_at.desc())
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Turn
# ---------------------------------------------------------------------------


async def add_turn(
    db: AsyncSession,
    session_id: str,
    speaker_type: str,
    text: str,
    turn_number: int,
    speaker_key: str | None = None,
    speaker_name: str | None = None,
    is_quiz_event: bool = False,
) -> Turn:
    turn = Turn(
        id=str(uuid.uuid4()),
        session_id=session_id,
        speaker_type=speaker_type,
        speaker_key=speaker_key,
        speaker_name=speaker_name,
        text=text,
        is_quiz_event=is_quiz_event,
        turn_number=turn_number,
    )
    db.add(turn)
    await db.commit()
    await db.refresh(turn)
    return turn
