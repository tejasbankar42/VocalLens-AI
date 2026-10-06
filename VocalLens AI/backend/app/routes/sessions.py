"""
VocalLens AI - Sessions API Routes
Endpoints:
- GET /api/sessions
- GET /api/sessions/{id}
- DELETE /api/sessions/{id}
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db import get_db
from backend.app.models import SessionModel, DimensionScore, FlawEvent
from backend.app.schemas import SessionListItem, ReportResponse, DimensionScoreSchema, FlawEventSchema, WordItem, FeedbackTip

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.get("", response_model=List[SessionListItem])
def list_sessions(user_id: str = "default_user", db: Session = Depends(get_db)):
    """Retrieves all sessions recorded by the user, newest first."""
    sessions = (
        db.query(SessionModel)
        .filter(SessionModel.user_id == user_id)
        .order_by(SessionModel.created_at.desc())
        .all()
    )
    return [
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
        for s in sessions
    ]


@router.get("/{session_id}", response_model=ReportResponse)
def get_session_detail(session_id: str, db: Session = Depends(get_db)):
    """Retrieves comprehensive report data for a specific session."""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found."
        )

    # Fetch dimension scores
    dim_scores = db.query(DimensionScore).filter(DimensionScore.session_id == session_id).all()
    dimension_scores_dict = {d.dimension: d.score for d in dim_scores}
    dimension_details = [
        DimensionScoreSchema(
            dimension=d.dimension,
            score=d.score,
            raw_value=d.raw_value,
            weight=d.weight
        )
        for d in dim_scores
    ]

    # Fetch flaw events
    flaws = db.query(FlawEvent).filter(FlawEvent.session_id == session_id).order_by(FlawEvent.start_time.asc()).all()
    flaw_schemas = [
        FlawEventSchema(
            type=f.flaw_type,
            start=f.start_time,
            end=f.end_time,
            severity=f.severity,
            evidence=f.evidence,
            tip=f.tip
        )
        for f in flaws
    ]

    return ReportResponse(
        session_id=session.id,
        filename=session.filename,
        duration=session.duration,
        language=session.language,
        overall_score=session.overall_score,
        band=session.band,
        dimension_scores=dimension_scores_dict,
        dimension_details=dimension_details,
        strengths=session.strengths,
        weaknesses=session.weaknesses,
        wpm=session.wpm,
        pause_count=session.pause_count,
        filler_count=session.filler_count,
        flaw_events=flaw_schemas,
        transcript_text=session.transcript_text,
        transcript_words=[WordItem(**w) for w in session.transcript_words],
        feedback_tips=[FeedbackTip(**t) for t in session.feedback_tips],
        raw_metrics=session.raw_metrics,
        created_at=session.created_at.isoformat()
    )


@router.delete("/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Deletes a session and its associated records."""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found."
        )

    db.delete(session)
    db.commit()
    return {"message": f"Session '{session_id}' successfully deleted."}
