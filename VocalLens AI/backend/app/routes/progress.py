"""
VocalLens AI - Progress Analytics API Route
Endpoint: GET /api/progress
Computes longitudinal analytics across recorded sessions, tracking score improvements,
dimension trends, and identifying the most improved skill area.
"""

from typing import Dict, List, Any
import numpy as np
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db import get_db
from backend.app.models import SessionModel, DimensionScore
from backend.app.schemas import ProgressResponse, SessionListItem
from backend.app.config import DIMENSION_WEIGHTS

router = APIRouter(prefix="/api/progress", tags=["Progress"])


@router.get("", response_model=ProgressResponse)
def get_user_progress(user_id: str = "default_user", db: Session = Depends(get_db)):
    """Calculates overall progress, score trajectories, and dimension growth."""
    sessions = (
        db.query(SessionModel)
        .filter(SessionModel.user_id == user_id)
        .order_by(SessionModel.created_at.asc())
        .all()
    )

    if not sessions:
        return ProgressResponse(
            total_sessions=0,
            average_score=0.0,
            highest_score=0.0,
            most_improved_dimension="None",
            improvement_delta=0.0,
            score_history=[],
            dimension_trends={d: [] for d in DIMENSION_WEIGHTS},
            recent_sessions=[]
        )

    scores = [s.overall_score for s in sessions]
    avg_score = round(float(np.mean(scores)), 1)
    highest_score = round(float(np.max(scores)), 1)

    # Score timeline for charts
    score_history = [
        {
            "id": s.id,
            "date": s.created_at.strftime("%b %d, %H:%M"),
            "timestamp": s.created_at.isoformat(),
            "score": s.overall_score,
            "band": s.band,
            "wpm": s.wpm,
            "fillers": s.filler_count,
            "pauses": s.pause_count,
            "filename": s.filename,
        }
        for s in sessions
    ]

    # Dimension trends across sessions
    dim_records = (
        db.query(DimensionScore)
        .join(SessionModel)
        .filter(SessionModel.user_id == user_id)
        .order_by(SessionModel.created_at.asc())
        .all()
    )

    dim_series: Dict[str, List[Dict[str, Any]]] = {d: [] for d in DIMENSION_WEIGHTS}
    for dr in dim_records:
        if dr.dimension in dim_series:
            dim_series[dr.dimension].append({
                "session_id": dr.session_id,
                "score": dr.score,
            })

    # Calculate most improved dimension (difference between first session and last session)
    most_improved = "clarity"
    max_delta = -999.0

    if len(sessions) >= 2:
        first_s_id = sessions[0].id
        last_s_id = sessions[-1].id

        first_scores = {
            d.dimension: d.score 
            for d in db.query(DimensionScore).filter(DimensionScore.session_id == first_s_id).all()
        }
        last_scores = {
            d.dimension: d.score 
            for d in db.query(DimensionScore).filter(DimensionScore.session_id == last_s_id).all()
        }

        for dim in DIMENSION_WEIGHTS:
            if dim in first_scores and dim in last_scores:
                delta = last_scores[dim] - first_scores[dim]
                if delta > max_delta:
                    max_delta = delta
                    most_improved = dim

        improvement_delta = round(max(0.0, max_delta), 1)
    else:
        improvement_delta = 0.0

    # Recent sessions (newest first)
    recent_sessions = [
        SessionListItem(
            id=s.id,
            filename=s.filename,
            duration=s.duration,
            overall_score=s.overall_score,
            band=s.band,
            wpm=s.wpm,
            filler_count=s.filler_count,
            pause_count=s.pause_count,
            created_at=s.created_at.isoformat()
        )
        for s in reversed(sessions)
    ]

    return ProgressResponse(
        total_sessions=len(sessions),
        average_score=avg_score,
        highest_score=highest_score,
        most_improved_dimension=most_improved,
        improvement_delta=improvement_delta,
        score_history=score_history,
        dimension_trends=dim_series,
        recent_sessions=recent_sessions[:10]
    )
