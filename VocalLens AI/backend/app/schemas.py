"""
VocalLens AI - Pydantic Schemas
Data contracts for API requests, analysis responses, sessions, and progress.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class WordItem(BaseModel):
    word: str
    start: float
    end: float
    probability: float


class FlawEventSchema(BaseModel):
    type: str
    start: float
    end: float
    severity: str
    evidence: str
    tip: str


class DimensionScoreSchema(BaseModel):
    dimension: str
    score: float
    raw_value: float
    weight: float


class FeedbackTip(BaseModel):
    dimension: str
    title: str
    observation: str
    how_to_improve: str
    priority: str = "medium"


class ReportResponse(BaseModel):
    session_id: str
    filename: str
    duration: float
    language: str
    overall_score: float
    band: str
    dimension_scores: Dict[str, float]
    dimension_details: List[DimensionScoreSchema]
    strengths: List[str]
    weaknesses: List[str]
    wpm: float
    pause_count: int
    filler_count: int
    flaw_events: List[FlawEventSchema]
    transcript_text: str
    transcript_words: List[WordItem]
    feedback_tips: List[FeedbackTip]
    raw_metrics: Dict[str, float]
    created_at: str


class SessionListItem(BaseModel):
    id: str
    filename: str
    duration: float
    overall_score: float
    band: str
    wpm: float
    filler_count: int
    pause_count: int
    created_at: str


class SessionDetailResponse(ReportResponse):
    pass


class ProgressResponse(BaseModel):
    total_sessions: int
    average_score: float
    highest_score: float
    most_improved_dimension: str
    improvement_delta: float
    score_history: List[Dict[str, Any]]
    dimension_trends: Dict[str, List[Dict[str, Any]]]
    recent_sessions: List[SessionListItem]


class BaselineMetricStats(BaseModel):
    mean: float
    std: float
    min: float
    max: float


class BaselineResponse(BaseModel):
    ideal: Dict[str, BaselineMetricStats]
    flawed: Dict[str, BaselineMetricStats]
    weights: Dict[str, float]
    bands: Dict[str, List[float]]
    sample_count: Dict[str, int]


class HealthResponse(BaseModel):
    status: str
    version: str
    whisper_model: str
    database: str
    baseline_loaded: bool
