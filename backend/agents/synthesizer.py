"""
Forge Chamber — Session Synthesizer

Generates structured debrief and calculates XP from a debate transcript.
"""

import json
import logging
import os

import openai

logger = logging.getLogger(__name__)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.3-70b-versatile"

DEBRIEF_SYSTEM = """You are the Forge Chamber session analyst. Analyze this engineering debate transcript and produce a structured debrief for the learning engineer.

Respond ONLY with valid JSON, no markdown, no preamble, no trailing text:
{
  "key_insights": ["insight 1", "insight 2", "insight 3"],
  "strong_moments": [
    {"turn": 0, "observation": "description of what the student did well"}
  ],
  "knowledge_gaps": [
    {"topic": "specific topic", "suggested_study": "what to study"}
  ],
  "scores": {
    "technical_depth": 3.0,
    "communication": 3.0,
    "debate_resilience": 3.0,
    "ai_native": 3.0
  },
  "overall_comment": "One paragraph honest assessment of this session."
}

Scoring rubric:
1.0 = Did not engage with this dimension
2.0 = Attempted but showed significant gaps
3.0 = Competent — handled most challenges adequately
4.0 = Strong — clear understanding, well-articulated under pressure
5.0 = Exceptional — nuanced, accurate, held position with evidence

Be honest and specific. Reference actual turns from the transcript.
If the student did not speak at all, scores should reflect that (1.0-2.0 range)."""


def _groq_client() -> openai.AsyncOpenAI:
    import httpx

    return openai.AsyncOpenAI(
        base_url=GROQ_BASE_URL,
        api_key=os.environ.get("GROQ_API_KEY", ""),
        http_client=httpx.AsyncClient(verify=False),
    )


def _format_transcript_for_debrief(transcript: list[dict]) -> str:
    """Format full transcript for debrief analysis."""
    lines = []
    for t in transcript:
        speaker = t.get("speaker_name", "Unknown")
        stype = t.get("speaker_type", "agent")
        text = t.get("text", "")
        turn_num = t.get("turn_number", 0)

        prefix = f"[Turn {turn_num}]"
        if stype == "human":
            lines.append(f"{prefix} STUDENT: {text}")
        elif t.get("is_quiz_event"):
            lines.append(f"{prefix} QUIZ ({speaker}): {text}")
        else:
            role = t.get("speaker_role", "")
            lines.append(f"{prefix} {speaker} ({role}): {text}")

    return "\n".join(lines)


async def synthesize_session(transcript: list[dict]) -> dict:
    """Analyze a debate transcript and produce a structured debrief.

    Returns a dict with: key_insights, strong_moments, knowledge_gaps,
    scores, overall_comment.
    """
    client = _groq_client()
    transcript_text = _format_transcript_for_debrief(transcript)

    for attempt in range(2):
        try:
            response = await client.chat.completions.create(
                model=GROQ_MODEL,
                max_tokens=800,
                temperature=0.4,
                messages=[
                    {"role": "system", "content": DEBRIEF_SYSTEM},
                    {"role": "user", "content": f"Analyze this transcript:\n\n{transcript_text}"},
                ],
            )
            raw = (response.choices[0].message.content or "").strip()

            # Strip markdown fences if present
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

            debrief = json.loads(raw)

            # Validate required keys
            assert "scores" in debrief
            assert "key_insights" in debrief

            # Clamp scores to 1.0-5.0
            for key in ["technical_depth", "communication", "debate_resilience", "ai_native"]:
                if key in debrief["scores"]:
                    debrief["scores"][key] = max(1.0, min(5.0, float(debrief["scores"][key])))

            return debrief

        except (json.JSONDecodeError, AssertionError, KeyError) as exc:
            logger.warning("Debrief parse attempt %d failed: %s", attempt + 1, exc)
            if attempt == 0:
                continue

    # Fallback debrief
    logger.error("Debrief synthesis failed after 2 attempts, returning fallback")
    return {
        "key_insights": ["Session completed. Debrief generation encountered an error."],
        "strong_moments": [],
        "knowledge_gaps": [],
        "scores": {
            "technical_depth": 2.0,
            "communication": 2.0,
            "debate_resilience": 2.0,
            "ai_native": 2.0,
        },
        "overall_comment": "Unable to generate detailed analysis. Please review the transcript manually.",
    }


def calculate_xp(
    scores: dict[str, float],
    transcript: list[dict],
    duration_seconds: int = 0,
    streak: int = 0,
) -> dict:
    """Calculate XP earned from a session.

    Returns dict with: total, base, participation_bonus, quiz_bonus,
    duration_bonus, streak_bonus, breakdown.
    """
    base = 50

    # Participation bonus: +10 per human turn, max 100
    human_turns = sum(1 for t in transcript if t.get("speaker_type") == "human")
    participation_bonus = min(human_turns * 10, 100)

    # Quiz bonus: +25 per answered quiz (human spoke after quiz event)
    quiz_bonus = 0
    for i, t in enumerate(transcript):
        if t.get("is_quiz_event"):
            # Check if next turn is human
            if i + 1 < len(transcript) and transcript[i + 1].get("speaker_type") == "human":
                quiz_bonus += 25

    # Duration bonus: +1 per minute, max 30
    duration_bonus = min(duration_seconds // 60, 30)

    # Streak bonus: +10 per consecutive session, max 50
    streak_bonus = min(streak * 10, 50)

    # Score bonus: average score * 20
    avg_score = sum(scores.values()) / max(len(scores), 1)
    score_bonus = int(avg_score * 20)

    total = base + participation_bonus + quiz_bonus + duration_bonus + streak_bonus + score_bonus

    return {
        "total": total,
        "base": base,
        "participation_bonus": participation_bonus,
        "quiz_bonus": quiz_bonus,
        "duration_bonus": duration_bonus,
        "streak_bonus": streak_bonus,
        "score_bonus": score_bonus,
        "breakdown": (
            f"Base: {base} + Participation: {participation_bonus} + "
            f"Quiz: {quiz_bonus} + Duration: {duration_bonus} + "
            f"Streak: {streak_bonus} + Score: {score_bonus} = {total}"
        ),
    }
