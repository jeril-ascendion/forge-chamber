"""
Forge Chamber — LangGraph Debate Orchestrator

Manages turn-taking, utterance generation, and quiz detection
in a multi-agent engineering debate.
"""

import asyncio
import json
import logging
import os
import random
from typing import TypedDict

import openai
from langgraph.graph import END, StateGraph

from backend.agents.personas import PERSONAS, format_system_prompt

logger = logging.getLogger(__name__)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_ROUTING_MODEL = "llama-3.1-8b-instant"
GROQ_GENERATION_MODEL = "llama-3.3-70b-versatile"


def _groq_client() -> openai.AsyncOpenAI:
    import httpx

    return openai.AsyncOpenAI(
        base_url=GROQ_BASE_URL,
        api_key=os.environ.get("GROQ_API_KEY", ""),
        http_client=httpx.AsyncClient(verify=False),
    )


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------


class DebateState(TypedDict):
    topic: str
    agents: list[str]
    transcript: list[dict]
    turn_count: int
    active_speaker: str | None
    human_silent_turns: int
    is_paused: bool
    rag_context: str
    session_id: str
    current_seed: str
    max_turns: int
    data_dir: str


def initial_state(
    topic: str,
    agents: list[str],
    session_id: str,
    rag_context: str = "",
    max_turns: int = 20,
    data_dir: str = "./data",
) -> DebateState:
    return DebateState(
        topic=topic,
        agents=agents,
        transcript=[],
        turn_count=0,
        active_speaker=None,
        human_silent_turns=0,
        is_paused=False,
        rag_context=rag_context,
        session_id=session_id,
        current_seed="",
        max_turns=max_turns,
        data_dir=data_dir,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _format_transcript_last_n(transcript: list[dict], n: int = 8) -> str:
    """Format the last N turns as readable dialogue."""
    recent = transcript[-n:] if len(transcript) > n else transcript
    lines = []
    for t in recent:
        name = t.get("speaker_name", t.get("speaker_key", "Unknown"))
        role = t.get("speaker_role", "")
        text = t.get("text", "")
        if role:
            lines.append(f"{name} ({role}): {text}")
        else:
            lines.append(f"{name}: {text}")
    return "\n".join(lines) if lines else "(no turns yet)"


def _build_orchestrator_system(agents_desc: str, last_speaker: str, topic: str) -> str:
    return (
        "You manage turn-taking in an engineering debate panel.\n"
        'Respond ONLY with valid JSON, no other text, no markdown:\n'
        '{"next_speaker": "agent_key", "seed": "one sentence prompt for that agent to react to", "tension_target": "agent_key_or_null"}\n'
        "\n"
        f"Available agents: {agents_desc}\n"
        f"Last speaker: {last_speaker}\n"
        "\n"
        "Rules:\n"
        "- Never pick the same agent as last speaker\n"
        "- If an agent was named or challenged in the last utterance, they should respond next\n"
        "- After 3+ turns of agreement, increase tension by picking the agent most likely to disagree\n"
        f"- Keep the debate on topic: {topic}\n"
        "- The seed should provoke a specific, concrete reaction — not a generic prompt"
    )


async def route_turn(state: DebateState) -> DebateState:
    """Pick the next speaker using Groq fast model."""
    client = _groq_client()
    last_speaker = state["transcript"][-1]["speaker_key"] if state["transcript"] else None
    available = [a for a in state["agents"] if a != last_speaker]

    if not available:
        available = state["agents"]

    system = _build_orchestrator_system(
        agents_desc=", ".join(f'{a} ({PERSONAS[a]["name"]}, {PERSONAS[a]["role"]})' for a in state["agents"]),
        last_speaker=last_speaker or "none",
        topic=state["topic"],
    )

    transcript_text = _format_transcript_last_n(state["transcript"], 6)

    try:
        response = await client.chat.completions.create(
            model=GROQ_ROUTING_MODEL,
            max_tokens=150,
            temperature=0.7,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": f"Recent debate:\n{transcript_text}\n\nPick the next speaker."},
            ],
        )
        raw = response.choices[0].message.content or ""
        # Strip markdown code fences if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        decision = json.loads(raw)
        next_speaker = decision.get("next_speaker", "")
        if next_speaker in available:
            state["active_speaker"] = next_speaker
            state["current_seed"] = decision.get("seed", "")
        else:
            # Fallback: pick from available
            state["active_speaker"] = random.choice(available)
            state["current_seed"] = ""
    except Exception as exc:
        logger.warning("route_turn JSON parse failed: %s — using round-robin", exc)
        state["active_speaker"] = available[state["turn_count"] % len(available)]
        state["current_seed"] = ""

    return state


async def generate_turn(state: DebateState) -> DebateState:
    """Generate an utterance for the active speaker using Groq quality model."""
    client = _groq_client()
    speaker_key = state["active_speaker"]
    if not speaker_key:
        return state

    persona = PERSONAS[speaker_key]
    transcript_text = _format_transcript_last_n(state["transcript"], 8)

    # Retrieve RAG context for this turn (non-blocking — falls back to empty)
    rag_context = state["rag_context"]
    if state.get("data_dir"):
        try:
            from backend.rag.retriever import retrieve_for_agent_turn

            last_texts = [t["text"] for t in state["transcript"][-2:] if t.get("text")]
            retrieved = retrieve_for_agent_turn(last_texts, state["data_dir"])
            if retrieved:
                rag_context = retrieved
        except Exception as exc:
            logger.warning("RAG retrieval failed for turn %d: %s", state["turn_count"], exc)

    system_prompt = format_system_prompt(
        agent_key=speaker_key,
        topic=state["topic"],
        rag_context=rag_context,
        transcript=transcript_text,
    )

    user_content = state["current_seed"] or f"Continue the debate on: {state['topic']}"
    if state["turn_count"] == 0:
        user_content = (
            f"You are opening the debate on: {state['topic']}. "
            "State your position or concern in 2-3 sentences. End with a question."
        )

    try:
        response = await client.chat.completions.create(
            model=GROQ_GENERATION_MODEL,
            max_tokens=200,
            temperature=0.8,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        text = response.choices[0].message.content or "(no response)"
    except Exception as exc:
        logger.error("generate_turn failed for %s: %s", speaker_key, exc)
        text = f"I'll defer to the next speaker on this point."

    turn = {
        "speaker_type": "agent",
        "speaker_key": speaker_key,
        "speaker_name": persona["name"],
        "speaker_role": persona["role"],
        "text": text.strip(),
        "turn_number": state["turn_count"],
        "is_quiz_event": False,
    }
    state["transcript"].append(turn)
    state["turn_count"] += 1
    state["human_silent_turns"] += 1

    return state


async def detect_quiz(state: DebateState) -> DebateState:
    """Check if student has been silent too long; generate quiz if needed."""
    if state["human_silent_turns"] < 5:
        return state

    # Generate a quiz question
    client = _groq_client()
    transcript_text = _format_transcript_last_n(state["transcript"], 6)

    try:
        response = await client.chat.completions.create(
            model=GROQ_ROUTING_MODEL,
            max_tokens=100,
            temperature=0.6,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Given this engineering debate context, write one direct question "
                        "to ask the student engineer. One sentence only. Be specific and "
                        "related to what was just discussed."
                    ),
                },
                {"role": "user", "content": transcript_text},
            ],
        )
        question = (response.choices[0].message.content or "What do you think about this approach?").strip()
    except Exception:
        question = "What's your take on the approach we've been discussing?"

    # Add quiz event to transcript
    quiz_turn = {
        "speaker_type": "system",
        "speaker_key": state["active_speaker"],
        "speaker_name": PERSONAS[state["active_speaker"] or state["agents"][0]]["name"],
        "speaker_role": "quiz",
        "text": question,
        "turn_number": state["turn_count"],
        "is_quiz_event": True,
    }
    state["transcript"].append(quiz_turn)
    state["is_paused"] = True

    return state


async def wait_for_human(state: DebateState) -> DebateState:
    """Wait for human to speak or timeout after 30 seconds."""
    # In the actual runtime, the debate_engine sets an asyncio.Event
    # that gets triggered when the human speaks. Here we just mark
    # the state as waiting. The debate_engine handles the actual wait.
    return state


async def resume_debate(state: DebateState) -> DebateState:
    """Resume after human interaction."""
    state["human_silent_turns"] = 0
    state["is_paused"] = False
    return state


# ---------------------------------------------------------------------------
# Routing logic
# ---------------------------------------------------------------------------


def _should_quiz(state: DebateState) -> str:
    """Conditional edge: quiz if human silent 5+ turns."""
    if state["is_paused"]:
        return "wait_for_human"
    return "continue"


def _should_stop(state: DebateState) -> str:
    """Check if debate should end."""
    if state["turn_count"] >= state["max_turns"]:
        return "end"
    return "route_turn"


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------


def build_debate_graph() -> StateGraph:
    """Build and compile the LangGraph debate orchestration graph."""
    graph = StateGraph(DebateState)

    graph.add_node("route_turn", route_turn)
    graph.add_node("generate_turn", generate_turn)
    graph.add_node("detect_quiz", detect_quiz)
    graph.add_node("wait_for_human", wait_for_human)
    graph.add_node("resume_debate", resume_debate)

    graph.add_edge("route_turn", "generate_turn")
    graph.add_conditional_edges(
        "generate_turn",
        lambda s: "end" if s["turn_count"] >= s["max_turns"] else "detect_quiz",
        {"end": END, "detect_quiz": "detect_quiz"},
    )
    graph.add_conditional_edges(
        "detect_quiz",
        _should_quiz,
        {"wait_for_human": "wait_for_human", "continue": "route_turn"},
    )
    graph.add_edge("wait_for_human", "resume_debate")
    graph.add_edge("resume_debate", "route_turn")

    graph.set_entry_point("route_turn")

    return graph.compile()


debate_graph = build_debate_graph()
