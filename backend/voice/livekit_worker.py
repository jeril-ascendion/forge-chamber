"""
Forge Chamber — LiveKit Agent Worker

Runs as a separate process alongside the FastAPI backend.
Connects to LiveKit Cloud and handles voice sessions.

Usage:
    python voice/livekit_worker.py dev      # development mode
    python voice/livekit_worker.py start    # production mode
"""

import asyncio
import logging
import os
import signal
import sys

from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.plugins import deepgram, silero
from livekit.plugins.openai import LLM as OpenAILLM

from backend.voice.tts_router import get_tts_for_agent

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

logger = logging.getLogger("forge-chamber-worker")

# ---------------------------------------------------------------------------
# LLM configuration — Groq via OpenAI-compatible endpoint
# ---------------------------------------------------------------------------

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You are a helpful AI engineering mentor at Ascendion. "
    "Help engineers understand technical concepts clearly. "
    "Keep responses concise — 2-3 sentences maximum."
)


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

    # Determine which agent voice to use (default: sre)
    agent_key = (ctx.room.metadata or "sre").strip() or "sre"

    agent = Agent(
        instructions=SYSTEM_PROMPT,
        stt=deepgram.STT(
            model="nova-2",
            language="en-US",
        ),
        vad=silero.VAD.load(),
        llm=_build_groq_llm(),
        tts=get_tts_for_agent(agent_key),
        allow_interruptions=True,
    )

    session = AgentSession()
    await session.start(agent=agent, room=ctx.room)

    await session.say(
        "Welcome to Forge Chamber. I'm your engineering mentor. What would you like to discuss?",
        allow_interruptions=True,
    )

    logger.info("Agent session started in room %s", ctx.room.name)

    # Keep alive until room closes or process killed
    try:
        await asyncio.sleep(7200)  # 2 hour max session
    except asyncio.CancelledError:
        logger.info("Session cancelled for room %s", ctx.room.name)


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
