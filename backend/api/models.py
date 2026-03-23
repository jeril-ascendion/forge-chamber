from datetime import datetime

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: str
    version: str


# ---------------------------------------------------------------------------
# Engineer
# ---------------------------------------------------------------------------


class EngineerSetupRequest(BaseModel):
    name: str
    role_track: str
    skill_level: str = "mid"


class EngineerProfileResponse(BaseModel):
    id: str
    name: str
    role_track: str
    skill_level: str
    total_xp: int
    total_sessions: int


class EngineerUpdateRequest(BaseModel):
    name: str | None = None
    role_track: str | None = None
    skill_level: str | None = None


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------


class SessionStartRequest(BaseModel):
    topic: str
    agents: list[str]
    user_role: str
    room_id: str | None = None


class SessionStartResponse(BaseModel):
    livekit_url: str
    livekit_token: str
    room_name: str
    session_id: str


class TurnSchema(BaseModel):
    speaker_type: str
    speaker_key: str | None = None
    speaker_name: str | None = None
    text: str
    turn_number: int
    is_quiz_event: bool = False


class SessionEndRequest(BaseModel):
    transcript: list[TurnSchema]


class SessionEndResponse(BaseModel):
    debrief: dict | None = None
    scores: dict[str, float]
    xp_earned: int
    xp_breakdown: dict | None = None
    new_badges: list[str] = []


class SessionDetailResponse(BaseModel):
    id: str
    room_id: str
    engineer_id: str
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: int | None
    xp_earned: int
    transcript: str | None
    debrief: str | None
    technical_depth_score: float | None
    communication_score: float | None
    debate_resilience_score: float | None
    ai_native_score: float | None


class SessionSummaryResponse(BaseModel):
    id: str
    started_at: datetime
    ended_at: datetime | None
    xp_earned: int
    topic: str | None = None


# ---------------------------------------------------------------------------
# RAG
# ---------------------------------------------------------------------------


class IngestUrlRequest(BaseModel):
    url: str


class IngestResponse(BaseModel):
    status: str
    chunks: int
    title: str


class RagSourceResponse(BaseModel):
    id: str
    label: str
    chunks: int
    ingested_at: str


class DeleteSourceResponse(BaseModel):
    status: str


# ---------------------------------------------------------------------------
# Progress
# ---------------------------------------------------------------------------


class SkillScoresResponse(BaseModel):
    technical_depth: float
    communication: float
    debate_resilience: float
    ai_native: float


class SessionProgressItem(BaseModel):
    session_id: str = ""
    date: str
    topic: str | None
    duration_seconds: int | None = None
    xp: int
    scores: dict[str, float | None]


class BadgeResponse(BaseModel):
    key: str
    label: str
    description: str
    icon: str
    earned_at: str


class ProgressSummaryResponse(BaseModel):
    skills: SkillScoresResponse
    total_xp: int
    total_sessions: int
    current_streak: int
    badges: list[BadgeResponse]
