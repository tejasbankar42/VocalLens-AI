"""
VocalLens AI - Database Models
SQLAlchemy ORM models for users, sessions, dimension_scores, and flaw_events.
"""

from datetime import datetime, timezone
import json
import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(128), default="Default User")
    email = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    sessions = relationship("SessionModel", back_populates="user", cascade="all, delete-orphan")


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), ForeignKey("users.id"), default="default_user", nullable=False)
    filename = Column(String(256), nullable=False)
    audio_path = Column(String(512), nullable=False)
    language = Column(String(32), default="en")
    
    # High-level Metrics
    duration = Column(Float, default=0.0)
    wpm = Column(Float, default=0.0)
    pause_count = Column(Integer, default=0)
    filler_count = Column(Integer, default=0)
    overall_score = Column(Float, default=0.0)
    band = Column(String(32), default="Needs work")
    
    # Complex Fields Stored as JSON strings
    transcript_text = Column(Text, default="")
    transcript_words_json = Column(Text, default="[]")
    strengths_json = Column(Text, default="[]")
    weaknesses_json = Column(Text, default="[]")
    feedback_tips_json = Column(Text, default="[]")
    raw_metrics_json = Column(Text, default="{}")
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="sessions")
    dimension_scores = relationship("DimensionScore", back_populates="session", cascade="all, delete-orphan")
    flaw_events = relationship("FlawEvent", back_populates="session", cascade="all, delete-orphan")

    @property
    def transcript_words(self):
        try:
            return json.loads(self.transcript_words_json or "[]")
        except Exception:
            return []

    @transcript_words.setter
    def transcript_words(self, val):
        self.transcript_words_json = json.dumps(val)

    @property
    def strengths(self):
        try:
            return json.loads(self.strengths_json or "[]")
        except Exception:
            return []

    @strengths.setter
    def strengths(self, val):
        self.strengths_json = json.dumps(val)

    @property
    def weaknesses(self):
        try:
            return json.loads(self.weaknesses_json or "[]")
        except Exception:
            return []

    @weaknesses.setter
    def weaknesses(self, val):
        self.weaknesses_json = json.dumps(val)

    @property
    def feedback_tips(self):
        try:
            return json.loads(self.feedback_tips_json or "[]")
        except Exception:
            return []

    @feedback_tips.setter
    def feedback_tips(self, val):
        self.feedback_tips_json = json.dumps(val)

    @property
    def raw_metrics(self):
        try:
            return json.loads(self.raw_metrics_json or "{}")
        except Exception:
            return {}

    @raw_metrics.setter
    def raw_metrics(self, val):
        self.raw_metrics_json = json.dumps(val)


class DimensionScore(Base):
    __tablename__ = "dimension_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("sessions.id"), nullable=False)
    dimension = Column(String(64), nullable=False)
    score = Column(Float, nullable=False)
    raw_value = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)

    session = relationship("SessionModel", back_populates="dimension_scores")


class FlawEvent(Base):
    __tablename__ = "flaw_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("sessions.id"), nullable=False)
    flaw_type = Column(String(64), nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    severity = Column(String(32), nullable=False)
    evidence = Column(Text, nullable=False)
    tip = Column(Text, nullable=False)

    session = relationship("SessionModel", back_populates="flaw_events")
