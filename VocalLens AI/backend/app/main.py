"""
VocalLens AI - Main FastAPI Application
Contrastive Speech Analytics & Temporal Flaw Grounding Platform.
"""

from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from backend.app.config import (
    CORS_ORIGINS, STORAGE_DIR, DATASET_DIR, BASELINE_PATH,
    WHISPER_MODEL_SIZE, DIMENSION_WEIGHTS, SCORE_BANDS
)
from backend.app.db import engine, Base, get_db
from backend.app.models import SessionModel
from backend.app.schemas import HealthResponse, BaselineResponse
from backend.app.routes import analyze, sessions, progress
from backend.app.pipeline.scorer import load_baseline
from backend.scripts.seed_demo import seed_database

# Create SQLite tables on startup
Base.metadata.create_all(bind=engine)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure database has initial demo sessions if empty."""
    from backend.app.db import SessionLocal
    db = SessionLocal()
    try:
        count = db.query(SessionModel).count()
        if count == 0:
            print("Database is empty. Automatically seeding demo sessions for judges...")
            seed_database()
    except Exception as e:
        print(f"Startup check warning: {e}")
    finally:
        db.close()
    yield

app = FastAPI(
    title="VocalLens AI",
    description="Contrastive Speech Analytics & Temporal Flaw Grounding Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount audio storage directory for browser WaveSurfer playback
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(STORAGE_DIR)), name="audio")

# Mount dataset directory for sample playback
DATASET_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/dataset_audio", StaticFiles(directory=str(DATASET_DIR)), name="dataset_audio")

# Register API Routers
app.include_router(analyze.router)
app.include_router(sessions.router)
app.include_router(progress.router)


@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """System health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        whisper_model=f"faster-whisper-{WHISPER_MODEL_SIZE}",
        database="connected",
        baseline_loaded=BASELINE_PATH.exists()
    )


@app.get("/api/baseline", tags=["System"])
def get_baseline_distributions():
    """Returns the contrastive baseline distributions and dimension weights."""
    baseline = load_baseline()
    return baseline


@app.get("/api/demo-session", tags=["Demo"])
def get_demo_session(type: str = "flagship", db: Session = Depends(get_db)):
    """Convenience endpoint returning pre-analyzed demo sessions for judges."""
    session_id = "demo-session-flagship" if type != "flawed" else "demo-session-flawed"
    return sessions.get_session_detail(session_id, db)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main.py:app", host="127.0.0.1", port=8000, reload=True)
