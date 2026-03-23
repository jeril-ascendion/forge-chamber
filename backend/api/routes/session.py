import json
import logging
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.models import (
    SessionDetailResponse,
    SessionEndRequest,
    SessionEndResponse,
    SessionStartRequest,
    SessionStartResponse,
    SessionSummaryResponse,
)
from backend.core.config import settings
from backend.db.crud import (
    add_turn,
    create_room,
    create_session,
    end_session,
    get_engineer,
    get_session,
    get_sessions_for_engineer,
    update_skill_scores,
    update_xp,
)
from backend.db.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/session", tags=["session"])


def _generate_livekit_token(engineer_name: str, room_name: str) -> str:
    """Generate a LiveKit access token. Requires livekit SDK and valid keys."""
    try:
        from livekit import api as lk_api

        token = lk_api.AccessToken(
            os.environ.get("LIVEKIT_API_KEY", settings.livekit_api_key),
            os.environ.get("LIVEKIT_API_SECRET", settings.livekit_api_secret),
        )
        token.with_identity(engineer_name)
        token.with_name(engineer_name)
        token.with_grants(
            lk_api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            )
        )
        return token.to_jwt()
    except Exception as exc:
        logger.warning("LiveKit token generation failed: %s — returning placeholder", exc)
        return "livekit-token-placeholder"


async def _dispatch_agent_to_room(room_name: str, agent_key: str) -> None:
    """Create a LiveKit room and dispatch the agent worker to it."""
    try:
        from livekit import api as lk_api

        lk_url = os.environ.get("LIVEKIT_URL", settings.livekit_url)
        lk_key = os.environ.get("LIVEKIT_API_KEY", settings.livekit_api_key)
        lk_secret = os.environ.get("LIVEKIT_API_SECRET", settings.livekit_api_secret)

        lk_client = lk_api.LiveKitAPI(lk_url, lk_key, lk_secret)

        # Create the room (idempotent — returns existing if already exists)
        await lk_client.room.create_room(
            lk_api.CreateRoomRequest(
                name=room_name,
                metadata=agent_key,
            )
        )

        # Dispatch agent worker to the room
        await lk_client.agent_dispatch.create_dispatch(
            lk_api.CreateAgentDispatchRequest(
                room=room_name,
                agent_name="forge-chamber-agent",
                metadata=agent_key,
            )
        )

        await lk_client.aclose()
        logger.info("Agent dispatched to room %s (agent_key=%s)", room_name, agent_key)
    except Exception as exc:
        logger.warning("Agent dispatch failed: %s — worker will pick up via room events", exc)


@router.post("/start", response_model=SessionStartResponse)
async def start_session(
    body: SessionStartRequest,
    db: AsyncSession = Depends(get_db),
) -> SessionStartResponse:
    engineer = await get_engineer(db)
    if not engineer:
        raise HTTPException(status_code=400, detail="Engineer profile not set up.")

    room_name = f"forge-{uuid.uuid4().hex[:8]}"

    room = await create_room(
        db,
        engineer_id=engineer.id,
        topic=body.topic,
        agents=body.agents,
        user_role=body.user_role,
    )

    session = await create_session(db, room_id=room.id, engineer_id=engineer.id)

    livekit_url = os.environ.get("LIVEKIT_URL", settings.livekit_url)
    livekit_token = _generate_livekit_token(engineer.name, room_name)

    # Dispatch agent worker to the LiveKit room
    agent_key = body.agents[0] if body.agents else "sre"
    await _dispatch_agent_to_room(room_name, agent_key)

    return SessionStartResponse(
        livekit_url=livekit_url,
        livekit_token=livekit_token,
        room_name=room_name,
        session_id=session.id,
    )


@router.get("/list", response_model=list[SessionSummaryResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
) -> list[SessionSummaryResponse]:
    engineer = await get_engineer(db)
    if not engineer:
        return []

    sessions = await get_sessions_for_engineer(db, engineer.id)
    return [
        SessionSummaryResponse(
            id=s.id,
            started_at=s.started_at,
            ended_at=s.ended_at,
            xp_earned=s.xp_earned,
        )
        for s in sessions
    ]


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> SessionDetailResponse:
    session = await get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return SessionDetailResponse(
        id=session.id,
        room_id=session.room_id,
        engineer_id=session.engineer_id,
        started_at=session.started_at,
        ended_at=session.ended_at,
        duration_seconds=session.duration_seconds,
        xp_earned=session.xp_earned,
        transcript=session.transcript,
        debrief=session.debrief,
        technical_depth_score=session.technical_depth_score,
        communication_score=session.communication_score,
        debate_resilience_score=session.debate_resilience_score,
        ai_native_score=session.ai_native_score,
    )


@router.post("/{session_id}/end", response_model=SessionEndResponse)
async def end_session_route(
    session_id: str,
    body: SessionEndRequest,
    db: AsyncSession = Depends(get_db),
) -> SessionEndResponse:
    session = await get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Persist individual turns
    for turn in body.transcript:
        await add_turn(
            db,
            session_id=session_id,
            speaker_type=turn.speaker_type,
            text=turn.text,
            turn_number=turn.turn_number,
            speaker_key=turn.speaker_key,
            speaker_name=turn.speaker_name,
            is_quiz_event=turn.is_quiz_event,
        )

    # Placeholder scores — real debrief synthesis comes in E5
    scores = {
        "technical_depth": 3.0,
        "communication": 3.0,
        "debate_resilience": 3.0,
        "ai_native": 3.0,
    }
    xp_earned = int(sum(scores.values()) * 25)

    transcript_json = json.dumps([t.model_dump() for t in body.transcript])
    debrief_json = json.dumps({
        "key_insights": ["Session recorded successfully."],
        "scores": scores,
        "overall_comment": "Debrief synthesis not yet implemented.",
    })

    await end_session(
        db,
        session_id=session_id,
        transcript=transcript_json,
        debrief=debrief_json,
        scores=scores,
        xp_earned=xp_earned,
    )

    await update_skill_scores(db, session.engineer_id, scores)
    await update_xp(db, session.engineer_id, xp_earned)

    return SessionEndResponse(
        debrief=json.loads(debrief_json),
        scores=scores,
        xp_earned=xp_earned,
    )
