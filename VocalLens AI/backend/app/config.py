"""
VocalLens AI - Configuration Module
Deterministic parameters, weights, thresholds, and filler lists.
"""

import os
from pathlib import Path

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend"
DATASET_DIR = BASE_DIR / "dataset"
STORAGE_DIR = BASE_DIR / "storage" / "audio"
BASELINE_PATH = DATASET_DIR / "baseline.json"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'storage' / 'vocallens.db'}")

# Ensure storage directories exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
DATASET_DIR.mkdir(parents=True, exist_ok=True)
(DATASET_DIR / "ideal").mkdir(parents=True, exist_ok=True)
(DATASET_DIR / "flawed").mkdir(parents=True, exist_ok=True)

# Server Config
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000").split(",")]

# Whisper ASR Config
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "small")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

# Gemini API Config (Optional - Fallback to templates)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Dimension Weights (Total = 100)
DIMENSION_WEIGHTS = {
    "clarity": 15.0,
    "fluency": 15.0,
    "pace": 15.0,
    "pauses": 15.0,
    "fillers": 15.0,
    "pronunciation": 10.0,
    "confidence": 10.0,
    "vocabulary": 5.0,
}

# Score Bands
SCORE_BANDS = {
    "Excellent": (85.0, 100.0),
    "Good": (70.0, 84.99),
    "Needs work": (50.0, 69.99),
    "Weak": (0.0, 49.99),
}

# Filler Words (English & Hinglish)
FILLER_WORDS = [
    "um", "uh", "er", "ah", "like", "you know", "basically", 
    "actually", "sort of", "kind of", "matlab", "toh", "yaani", "accha"
]

# Hedge Words (Affect Confidence)
HEDGE_WORDS = [
    "maybe", "sort of", "kind of", "i guess", "i suppose", 
    "possibly", "probably", "perhaps", "i think maybe", "somewhat"
]

# Temporal Flaw Thresholds
PAUSE_MEDIUM_THRESHOLD = 1.2    # seconds
PAUSE_HIGH_THRESHOLD = 2.0      # seconds
SLIDING_WINDOW_SEC = 10.0       # seconds for rate calculations
WPM_TOO_FAST = 170.0            # WPM
WPM_TOO_SLOW = 100.0            # WPM
MUMBLE_PROB_THRESHOLD = 0.45    # Word confidence threshold
MUMBLE_CONSECUTIVE_WORDS = 3    # Number of consecutive low-prob words
MONOTONE_WINDOW_SEC = 8.0       # seconds
MONOTONE_PITCH_STD_THRESHOLD = 14.0 # Hz standard deviation below which voice sounds flat
LOW_CONFIDENCE_WORD_THRESHOLD = 0.50 # Word prob for pronunciation flaw

# Ideal Pace Range
IDEAL_WPM_MIN = 130.0
IDEAL_WPM_MAX = 155.0

# Metric Directionalities (Higher is better True/False)
# True = higher raw value is closer to ideal (e.g., clarity, vocab ratio)
# False = lower raw value is closer to ideal (e.g., filler rate, pause ratio)
METRIC_DIRECTIONS = {
    "clarity": True,         # Higher mean confidence is better
    "fluency": True,         # Higher fluency index (lower disfluency) is better
    "pace": True,            # Closer to ideal WPM (normalized pace consistency) is better
    "pauses": False,         # Lower pause ratio / count is better
    "fillers": False,        # Lower filler rate is better
    "pronunciation": True,   # Higher share of well-pronounced words is better
    "confidence": True,      # Higher confidence composite is better
    "vocabulary": True,      # Higher unique-word ratio & length composite is better
}
