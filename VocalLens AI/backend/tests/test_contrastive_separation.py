"""
VocalLens AI - Contrastive Separation Test
Validates that ideal clips score significantly higher than flawed clips.
"""

from pathlib import Path
import csv
import soundfile as sf
import numpy as np

from backend.app.config import DATASET_DIR
from backend.app.pipeline.asr import transcribe_audio
from backend.app.pipeline.audio_features import extract_acoustic_features
from backend.app.pipeline.metrics import compute_speech_metrics
from backend.app.pipeline.scorer import score_session


def evaluate_audio_score(file_path: Path) -> float:
    data, sr = sf.read(str(file_path))
    duration = float(len(data)) / float(sr)
    asr_res = transcribe_audio(file_path, language="en")
    words = asr_res["words"]
    acoustics = extract_acoustic_features(file_path)
    metrics_res = compute_speech_metrics(words, duration, acoustics)
    score_res = score_session(metrics_res["raw_metrics"])
    return score_res["overall_score"]


def test_ideal_scores_higher_than_flawed():
    """Validates contrastive separation: Ideal mean score >> Flawed mean score."""
    manifest_path = DATASET_DIR / "manifest.csv"
    assert manifest_path.exists(), "manifest.csv missing"

    with open(manifest_path, "r", encoding="utf-8") as f:
        records = list(csv.DictReader(f))

    # Evaluate first 2 ideal and first 2 flawed clips for fast test turnaround
    ideal_scores = []
    flawed_scores = []

    for r in records[:4]:
        file_path = DATASET_DIR / r["filename"]
        score = evaluate_audio_score(file_path)
        if r["category"] == "ideal":
            ideal_scores.append(score)
        else:
            flawed_scores.append(score)

    assert len(ideal_scores) > 0 and len(flawed_scores) > 0
    mean_ideal = float(np.mean(ideal_scores))
    mean_flawed = float(np.mean(flawed_scores))

    print(f"\nTest Separation -> Ideal Mean: {mean_ideal:.1f}, Flawed Mean: {mean_flawed:.1f}")
    assert mean_ideal > mean_flawed, f"Ideal mean ({mean_ideal}) must exceed flawed mean ({mean_flawed})"
    assert (mean_ideal - mean_flawed) > 30.0, f"Separation margin ({mean_ideal - mean_flawed}) is under 30.0 points"
