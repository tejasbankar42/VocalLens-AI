"""
VocalLens AI - Speech Analysis API Route
Endpoint: POST /api/analyze
Coordinates preprocessing, ASR transcription, acoustic extraction, metrics calculation,
contrastive scoring, flaw grounding, and feedback synthesis.
"""

from datetime import datetime, timezone
import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.config import STORAGE_DIR
from backend.app.db import get_db
from backend.app.models import SessionModel, DimensionScore, FlawEvent
from backend.app.schemas import ReportResponse, FlawEventSchema, FeedbackTip, WordItem, DimensionScoreSchema
from backend.app.pipeline.preprocess import preprocess_audio, AudioPreprocessingError
from backend.app.pipeline.asr import transcribe_audio
from backend.app.pipeline.audio_features import extract_acoustic_features
from backend.app.pipeline.metrics import compute_speech_metrics
from backend.app.pipeline.scorer import score_session
from backend.app.pipeline.flaw_detector import ground_flaw_events
from backend.app.pipeline.feedback import generate_feedback_tips, polish_feedback_with_gemini

router = APIRouter(prefix="/api", tags=["Analysis"])


@router.post("/analyze", response_model=ReportResponse)
async def analyze_speech(
    file: UploadFile = File(...),
    language: str = Form("en"),
    user_id: str = Form("default_user"),
    db: Session = Depends(get_db)
):
    """
    Analyzes an uploaded speech recording end-to-end and returns the full contrastive evaluation.
    """
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No audio file uploaded.")

    # Generate a unique session ID and filename
    session_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix or ".wav"
    raw_saved_path = STORAGE_DIR / f"{session_id}_raw{file_ext}"

    # 1. Save uploaded file to storage
    try:
        with open(raw_saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save incoming audio file: {e}"
        )

    # 2. Audio Preprocessing & Duration Validation (> 5.0 seconds)
    try:
        clean_wav_path, duration_sec, sr = preprocess_audio(
            raw_saved_path, 
            STORAGE_DIR, 
            min_duration=5.0
        )
    except AudioPreprocessingError as err:
        if raw_saved_path.exists():
            raw_saved_path.unlink()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
    except Exception as err:
        if raw_saved_path.exists():
            raw_saved_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Audio format is invalid or could not be decoded: {err}"
        )

    # 3. ASR Transcription with Word-level Timestamps
    try:
        asr_result = transcribe_audio(clean_wav_path, language=language)
        words = asr_result.get("words", [])
        transcript_text = asr_result.get("text", "")
        detected_language = asr_result.get("language", language)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech-to-text pipeline failure: {err}"
        )

    # Check if any speech words were detected
    if not words:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No intelligible speech detected in the audio file. Please speak clearly into the microphone."
        )

    # 4. Acoustic Prosody & Energy Extraction
    try:
        acoustics = extract_acoustic_features(clean_wav_path)
    except Exception as err:
        acoustics = {
            "mean_pitch_hz": 120.0,
            "std_pitch_hz": 18.0,
            "energy_stability": 0.75,
            "monotone_regions": []
        }

    # 5. Core Metric Computations
    metrics_result = compute_speech_metrics(words, duration_sec, acoustics)
    raw_metrics = metrics_result["raw_metrics"]
    summary = metrics_result["summary"]

    # 6. Contrastive Scoring (Deterministic Rubric vs Baseline)
    score_result = score_session(raw_metrics)
    overall_score = score_result["overall_score"]
    band = score_result["band"]
    dimension_scores = score_result["dimension_scores"]
    dimension_details = score_result["dimension_details"]
    strengths = score_result["strengths"]
    weaknesses = score_result["weaknesses"]

    # 7. Temporal Flaw Grounding
    flaw_events = ground_flaw_events(words, metrics_result, acoustics)

    # 8. Feedback Synthesis (Offline templates + optional Gemini polish)
    feedback_tips = generate_feedback_tips(dimension_scores, flaw_events, strengths, weaknesses)
    feedback_tips = polish_feedback_with_gemini(feedback_tips, overall_score, band)

    # 9. Persist into Database
    audio_rel_url = f"/audio/{clean_wav_path.name}"
    db_session = SessionModel(
        id=session_id,
        user_id=user_id,
        filename=file.filename,
        audio_path=audio_rel_url,
        language=detected_language,
        duration=round(duration_sec, 2),
        wpm=summary["overall_wpm"],
        pause_count=summary["pause_count"],
        filler_count=summary["filler_count"],
        overall_score=overall_score,
        band=band,
        transcript_text=transcript_text,
        transcript_words=words,
        strengths=strengths,
        weaknesses=weaknesses,
        feedback_tips=feedback_tips,
        raw_metrics=raw_metrics,
        created_at=datetime.now(timezone.utc)
    )
    db.add(db_session)

    # Persist Dimension Scores
    for detail in dimension_details:
        ds = DimensionScore(
            session_id=session_id,
            dimension=detail["dimension"],
            score=detail["score"],
            raw_value=detail["raw_value"],
            weight=detail["weight"]
        )
        db.add(ds)

    # Persist Flaw Events
    for flaw in flaw_events:
        fe = FlawEvent(
            session_id=session_id,
            flaw_type=flaw["type"],
            start_time=flaw["start"],
            end_time=flaw["end"],
            severity=flaw["severity"],
            evidence=flaw["evidence"],
            tip=flaw["tip"]
        )
        db.add(fe)

    db.commit()

    # 10. Construct API Response
    return ReportResponse(
        session_id=session_id,
        filename=file.filename,
        duration=round(duration_sec, 2),
        language=detected_language,
        overall_score=overall_score,
        band=band,
        dimension_scores=dimension_scores,
        dimension_details=[DimensionScoreSchema(**d) for d in dimension_details],
        strengths=strengths,
        weaknesses=weaknesses,
        wpm=summary["overall_wpm"],
        pause_count=summary["pause_count"],
        filler_count=summary["filler_count"],
        flaw_events=[FlawEventSchema(**f) for f in flaw_events],
        transcript_text=transcript_text,
        transcript_words=[WordItem(**w) for w in words],
        feedback_tips=[FeedbackTip(**t) for t in feedback_tips],
        raw_metrics=raw_metrics,
        created_at=db_session.created_at.isoformat()
    )
