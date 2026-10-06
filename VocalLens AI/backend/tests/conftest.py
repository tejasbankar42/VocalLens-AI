"""
VocalLens AI - Pytest Configuration and Shared Fixtures
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import DATASET_DIR, STORAGE_DIR

@pytest.fixture(scope="session")
def api_client():
    """Provides a FastAPI test client instance."""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="session")
def sample_ideal_wav():
    """Path to a verified ideal audio sample."""
    wav_path = DATASET_DIR / "ideal" / "ideal_01_sample_01_interview.wav"
    assert wav_path.exists(), f"Sample ideal audio not found at {wav_path}"
    return wav_path

@pytest.fixture(scope="session")
def sample_flawed_wav():
    """Path to a verified flawed audio sample."""
    wav_path = DATASET_DIR / "flawed" / "flawed_01_sample_01_interview.wav"
    assert wav_path.exists(), f"Sample flawed audio not found at {wav_path}"
    return wav_path
