import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Engineer(Base):
    __tablename__ = "engineers"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    role_track: Mapped[str] = mapped_column(String, nullable=False)
    skill_level: Mapped[str] = mapped_column(String, default="mid")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    total_sessions: Mapped[int] = mapped_column(Integer, default=0)


class SkillScore(Base):
    __tablename__ = "skill_scores"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    engineer_id: Mapped[str] = mapped_column(
        String, ForeignKey("engineers.id"), nullable=False
    )
    domain: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    session_count: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    engineer_id: Mapped[str] = mapped_column(
        String, ForeignKey("engineers.id"), nullable=False
    )
    topic: Mapped[str] = mapped_column(String, nullable=False)
    agents: Mapped[str] = mapped_column(String, nullable=False)
    user_role: Mapped[str] = mapped_column(String, nullable=False)
    context_sources: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    room_id: Mapped[str] = mapped_column(
        String, ForeignKey("rooms.id"), nullable=False
    )
    engineer_id: Mapped[str] = mapped_column(
        String, ForeignKey("engineers.id"), nullable=False
    )
    started_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    ended_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    debrief: Mapped[str | None] = mapped_column(Text, nullable=True)
    technical_depth_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    communication_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    debate_resilience_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_native_score: Mapped[float | None] = mapped_column(Float, nullable=True)


class Turn(Base):
    __tablename__ = "turns"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String, ForeignKey("sessions.id"), nullable=False
    )
    speaker_type: Mapped[str] = mapped_column(String, nullable=False)
    speaker_key: Mapped[str | None] = mapped_column(String, nullable=True)
    speaker_name: Mapped[str | None] = mapped_column(String, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_quiz_event: Mapped[bool] = mapped_column(Boolean, default=False)
    quiz_answered: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    turn_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )
