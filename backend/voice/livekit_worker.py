"""
Forge Chamber — LiveKit Agent Worker

Runs as a separate process alongside the FastAPI backend.
Connects to LiveKit Cloud and handles voice sessions with
the multi-agent debate engine.

Usage:
    python voice/livekit_worker.py dev      # development mode
    python voice/livekit_worker.py start    # production mode
"""

import asyncio
import json
import logging
import os
import signal
import sys

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
)
from livekit.plugins import deepgram, silero
from livekit.plugins.openai import LLM as OpenAILLM

from backend.agents.debate_engine import DebateEngine
from backend.agents.personas import PERSONAS
from backend.agents.synthesizer import calculate_xp, synthesize_session
from backend.voice.tts_router import get_tts_for_agent

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

logger = logging.getLogger("forge-chamber-worker")

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.3-70b-versatile"


def _build_groq_llm() -> OpenAILLM:
    """Create an OpenAI-compatible LLM pointed at Groq."""
    return OpenAILLM(
        base_url=GROQ_BASE_URL,
        api_key=os.environ.get("GROQ_API_KEY", ""),
        model=GROQ_MODEL,
    )


# ---------------------------------------------------------------------------
# Agent entrypoint
# ---------------------------------------------------------------------------


async def entrypoint(ctx: JobContext) -> None:
    logger.info("Job received — room=%s", ctx.room.name)

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Parse metadata — expects JSON: {"topic": "...", "agents": [...], "session_id": "..."}
    metadata = {}
    try:
        raw_meta = ctx.room.metadata or ""
        if raw_meta.startswith("{"):
            metadata = json.loads(raw_meta)
        else:
            # Simple string = agent key (backward compat from E4)
            metadata = {"agents": [raw_meta.strip() or "sre"]}
    except json.JSONDecodeError:
        metadata = {"agents": ["sre"]}

    topic = metadata.get("topic", "Engineering best practices")
    agents = metadata.get("agents", ["sre", "sys_arch", "cloud_eng"])
    session_id = metadata.get("session_id", "")
    max_turns = metadata.get("max_turns", 20)

    # Validate agent keys
    agents = [a for a in agents if a in PERSONAS]
    if not agents:
        agents = ["sre", "sys_arch", "cloud_eng"]

    # Use first agent's voice for the LiveKit VoiceAssistant TTS
    primary_agent = agents[0]

    # Data channel callback — publishes messages to the LiveKit room
    async def data_callback(msg: dict) -> None:
        try:
            payload = json.dumps(msg).encode("utf-8")
            await ctx.room.local_participant.publish_data(payload, reliable=True)
            logger.debug("Published data: %s", msg.get("type", "unknown"))
        except Exception as exc:
            logger.warning("Failed to publish data: %s", exc)

    # Create the debate engine
    engine = DebateEngine(
        topic=topic,
        agents=agents,
        session_id=session_id,
        max_turns=max_turns,
        data_callback=data_callback,
    )

    # Also create a LiveKit Agent for voice I/O
    # The debate engine generates text; the Agent handles STT/TTS
    agent = Agent(
        instructions=(
            f"You are facilitating a Forge Chamber debate on: {topic}. "
            "Listen to the student and relay their input to the debate panel."
        ),
        stt=deepgram.STT(model="nova-2", language="en-US"),
        vad=silero.VAD.load(),
        llm=_build_groq_llm(),
        tts=get_tts_for_agent(primary_agent),
        allow_interruptions=True,
    )

    session = AgentSession()
    await session.start(agent=agent, room=ctx.room)

    # Greet and start debate
    await session.say(
        f"Welcome to Forge Chamber. Today's topic: {topic}. "
        f"Our panel: {', '.join(PERSONAS[a]['name'] + ' the ' + PERSONAS[a]['role'] for a in agents)}. "
        "Listen in, and jump in anytime. Let's begin.",
        allow_interruptions=True,
    )

    logger.info(
        "Debate session started — topic=%s agents=%s session_id=%s",
        topic,
        agents,
        session_id,
    )

    # Run debate in background, speak each turn via TTS
    async def run_debate_with_voice() -> None:
        """Run debate loop, speaking each agent's turn aloud."""
        original_callback = engine._data_callback

        async def voice_callback(msg: dict) -> None:
            # Forward to data channel
            if original_callback:
                await original_callback(msg)

            # Speak agent turns aloud
            if msg.get("type") == "turn_committed" and msg.get("speaker_type") == "agent":
                speaker_key = msg.get("speaker_key", primary_agent)
                text = msg.get("text", "")
                if text:
                    # Switch TTS voice for this agent
                    # Note: in production, we'd switch the TTS voice per agent
                    # For now, speak with primary agent voice
                    await session.say(text, allow_interruptions=True)

            elif msg.get("type") == "quiz_event":
                question = msg.get("question", "")
                if question:
                    await session.say(
                        f"Question for the student: {question}",
                        allow_interruptions=True,
                    )

        engine._data_callback = voice_callback

        transcript = await engine.start_debate()

        # Debate complete — synthesize
        logger.info("Debate complete, synthesizing debrief...")
        debrief = await synthesize_session(transcript)
        xp = calculate_xp(debrief.get("scores", {}), transcript)

        # Speak summary
        comment = debrief.get("overall_comment", "Session complete.")
        await session.say(
            f"Session complete. {comment} You earned {xp['total']} XP.",
            allow_interruptions=True,
        )

        # Publish debrief via data channel
        await data_callback({
            "type": "session_complete",
            "debrief": debrief,
            "xp": xp,
        })

        # POST results to backend API
        try:
            import httpx

            api_url = f"http://127.0.0.1:{os.environ.get('FORGE_PORT', '8765')}"
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{api_url}/session/{session_id}/end",
                    json={
                        "transcript": [
                            {
                                "speaker_type": t["speaker_type"],
                                "speaker_key": t.get("speaker_key"),
                                "speaker_name": t.get("speaker_name"),
                                "text": t["text"],
                                "turn_number": t.get("turn_number", 0),
                                "is_quiz_event": t.get("is_quiz_event", False),
                            }
                            for t in transcript
                        ]
                    },
                    timeout=30,
                )
                logger.info("Session results POSTed to backend")
        except Exception as exc:
            logger.warning("Failed to POST session results: %s", exc)

    # Run debate in a task
    debate_task = asyncio.create_task(run_debate_with_voice())

    # Keep alive until debate completes or room closes
    try:
        await debate_task
    except asyncio.CancelledError:
        engine.stop()
        logger.info("Debate cancelled for room %s", ctx.room.name)
    except Exception as exc:
        logger.error("Debate error: %s", exc, exc_info=True)


# ---------------------------------------------------------------------------
# Graceful shutdown
# ---------------------------------------------------------------------------


def _handle_sigterm(signum: int, frame: object) -> None:
    logger.info("Received SIGTERM, shutting down worker")
    sys.exit(0)


signal.signal(signal.SIGTERM, _handle_sigterm)


# ---------------------------------------------------------------------------
# Worker entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            ws_url=os.environ.get("LIVEKIT_URL", ""),
            api_key=os.environ.get("LIVEKIT_API_KEY", ""),
            api_secret=os.environ.get("LIVEKIT_API_SECRET", ""),
            agent_name="forge-chamber-agent",
        )
    )
