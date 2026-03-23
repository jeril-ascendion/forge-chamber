"""
Forge Chamber — Debate Engine

Runs the multi-agent debate loop using the LangGraph orchestrator.
Provides data callbacks for publishing events to the LiveKit room.
"""

import asyncio
import json
import logging
from typing import Any, Callable, Coroutine

from backend.agents.orchestrator import (
    DebateState,
    _format_transcript_last_n,
    _groq_client,
    GROQ_GENERATION_MODEL,
    GROQ_ROUTING_MODEL,
    initial_state,
)
from backend.agents.personas import PERSONAS

logger = logging.getLogger(__name__)

DataCallback = Callable[[dict], Coroutine[Any, Any, None]]


class DebateEngine:
    """Manages a multi-agent debate session."""

    def __init__(
        self,
        topic: str,
        agents: list[str],
        session_id: str,
        rag_context: str = "",
        max_turns: int = 20,
        data_callback: DataCallback | None = None,
        data_dir: str = "./data",
    ) -> None:
        self.state = initial_state(
            topic=topic,
            agents=agents,
            session_id=session_id,
            rag_context=rag_context,
            max_turns=max_turns,
            data_dir=data_dir,
        )
        self._data_callback = data_callback
        self._human_event = asyncio.Event()
        self._running = False
        self._paused = False

    @property
    def transcript(self) -> list[dict]:
        return self.state["transcript"]

    async def _publish(self, msg: dict) -> None:
        """Send a data channel message via the callback."""
        if self._data_callback:
            try:
                await self._data_callback(msg)
            except Exception as exc:
                logger.warning("Data callback failed: %s", exc)

    async def _publish_speaker_change(self, agent_key: str) -> None:
        persona = PERSONAS[agent_key]
        await self._publish({
            "type": "speaker_change",
            "agent_key": agent_key,
            "agent_name": persona["name"],
            "agent_role": persona["role"],
        })

    async def _publish_turn(self, turn: dict) -> None:
        await self._publish({
            "type": "turn_committed",
            "speaker_type": turn["speaker_type"],
            "speaker_key": turn["speaker_key"],
            "speaker_name": turn["speaker_name"],
            "speaker_role": turn.get("speaker_role", ""),
            "text": turn["text"],
            "turn_number": turn["turn_number"],
        })

    async def _publish_quiz(self, question: str, agent_key: str) -> None:
        await self._publish({
            "type": "quiz_event",
            "question": question,
            "agent_key": agent_key,
            "timeout_seconds": 30,
        })

    # ------------------------------------------------------------------
    # Debate loop — runs the orchestrator graph step by step
    # ------------------------------------------------------------------

    async def start_debate(self) -> list[dict]:
        """Run the full debate loop. Returns the transcript."""
        self._running = True
        logger.info("Debate started: topic=%s agents=%s", self.state["topic"], self.state["agents"])

        while self._running and self.state["turn_count"] < self.state["max_turns"]:
            # Step 1: Route — pick next speaker
            await self._step_route()

            if not self._running:
                break

            speaker = self.state["active_speaker"]
            if not speaker:
                break

            # Publish speaker change
            await self._publish_speaker_change(speaker)

            # Step 2: Generate turn
            prev_count = len(self.state["transcript"])
            await self._step_generate()

            # Publish the new turn
            if len(self.state["transcript"]) > prev_count:
                new_turn = self.state["transcript"][-1]
                await self._publish_turn(new_turn)
                logger.info(
                    "Turn %d: %s (%s): %s",
                    new_turn["turn_number"],
                    new_turn["speaker_name"],
                    new_turn["speaker_key"],
                    new_turn["text"][:80] + "..." if len(new_turn["text"]) > 80 else new_turn["text"],
                )

            # Step 3: Check quiz
            if self.state["human_silent_turns"] >= 5:
                await self._step_quiz()

                if self.state["is_paused"]:
                    # Wait for human or timeout
                    quiz_turn = self.state["transcript"][-1]
                    await self._publish_quiz(quiz_turn["text"], quiz_turn["speaker_key"] or self.state["agents"][0])

                    answered = await self._wait_for_human_or_timeout(30)

                    if not answered:
                        # Agent answers own question
                        await self._agent_answers_quiz(quiz_turn["text"])

                    self.state["human_silent_turns"] = 0
                    self.state["is_paused"] = False

        self._running = False
        logger.info("Debate ended after %d turns", self.state["turn_count"])
        return self.state["transcript"]

    async def _step_route(self) -> None:
        """Route to next speaker using Groq fast model."""
        from backend.agents.orchestrator import route_turn
        self.state = await route_turn(self.state)

    async def _step_generate(self) -> None:
        """Generate utterance for active speaker."""
        from backend.agents.orchestrator import generate_turn
        self.state = await generate_turn(self.state)

    async def _step_quiz(self) -> None:
        """Detect and generate quiz if needed."""
        from backend.agents.orchestrator import detect_quiz
        self.state = await detect_quiz(self.state)

    async def _wait_for_human_or_timeout(self, timeout: float) -> bool:
        """Wait for human speech event or timeout. Returns True if human spoke."""
        self._human_event.clear()
        try:
            await asyncio.wait_for(self._human_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            logger.info("Quiz timeout — no human response in %ds", timeout)
            return False

    async def _agent_answers_quiz(self, question: str) -> None:
        """Agent answers their own quiz question when human doesn't respond."""
        client = _groq_client()
        speaker_key = self.state["active_speaker"] or self.state["agents"][0]
        persona = PERSONAS[speaker_key]

        try:
            response = await client.chat.completions.create(
                model=GROQ_GENERATION_MODEL,
                max_tokens=200,
                temperature=0.7,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"You are {persona['name']}, {persona['role']}. "
                            "The student didn't answer, so briefly answer your own question "
                            "in 2-3 sentences, then say you'll come back to this later."
                        ),
                    },
                    {"role": "user", "content": f"Answer this question: {question}"},
                ],
            )
            text = (response.choices[0].message.content or "Let me answer that myself...").strip()
        except Exception:
            text = "No worries, I'll come back to this. Let's continue."

        turn = {
            "speaker_type": "agent",
            "speaker_key": speaker_key,
            "speaker_name": persona["name"],
            "speaker_role": persona["role"],
            "text": text,
            "turn_number": self.state["turn_count"],
            "is_quiz_event": False,
        }
        self.state["transcript"].append(turn)
        self.state["turn_count"] += 1
        await self._publish_turn(turn)

    # ------------------------------------------------------------------
    # External control
    # ------------------------------------------------------------------

    def pause_debate(self) -> None:
        """Pause the debate (human is speaking)."""
        self._paused = True

    def resume_debate(self) -> None:
        """Resume after human finishes speaking."""
        self._paused = False
        self.state["human_silent_turns"] = 0
        self._human_event.set()

    def add_human_turn(self, text: str) -> None:
        """Record a human utterance in the transcript."""
        turn = {
            "speaker_type": "human",
            "speaker_key": "human",
            "speaker_name": "Student",
            "speaker_role": "Engineer",
            "text": text,
            "turn_number": self.state["turn_count"],
            "is_quiz_event": False,
        }
        self.state["transcript"].append(turn)
        self.state["turn_count"] += 1
        self.state["human_silent_turns"] = 0
        self._human_event.set()

    def stop(self) -> None:
        """Stop the debate loop."""
        self._running = False
        self._human_event.set()  # Unblock any wait
