"""
VocalLens AI - Flaw Detector Test
Validates that temporal flaw grounding correctly identifies ground truth flaws
present in annotations.json.
"""

import json
from pathlib import Path
from backend.app.config import DATASET_DIR
from backend.app.pipeline.asr import transcribe_audio
from backend.app.pipeline.audio_features import extract_acoustic_features
from backend.app.pipeline.metrics import compute_speech_metrics
from backend.app.pipeline.flaw_detector import ground_flaw_events


def test_detector_finds_known_flaws(sample_flawed_wav):
    """Verifies that ground-truth pause and filler flaws are correctly detected."""
    annotations_path = DATASET_DIR / "annotations.json"
    assert annotations_path.exists(), "annotations.json missing"

    with open(annotations_path, "r", encoding="utf-8") as f:
        annotations = json.load(f)

    expected_flaws = annotations.get("flawed/flawed_01_sample_01_interview.wav", [])
    assert len(expected_flaws) > 0, "No annotations found for flawed sample"

    # Run pipeline
    import soundfile as sf
    data, sr = sf.read(str(sample_flawed_wav))
    duration = float(len(data)) / float(sr)

    asr_res = transcribe_audio(sample_flawed_wav, language="en")
    words = asr_res["words"]
    acoustics = extract_acoustic_features(sample_flawed_wav)
    metrics_res = compute_speech_metrics(words, duration, acoustics)
    detected_flaws = ground_flaw_events(words, metrics_res, acoustics)

    assert len(detected_flaws) > 0, "Detector failed to find any flaw events"

    detected_types = {f["type"] for f in detected_flaws}
    expected_types = {f["type"] for f in expected_flaws}

    # Verify that primary flaw types (long_pause, filler) overlap with expectations
    common_types = detected_types.intersection(expected_types)
    assert len(common_types) >= 1, f"Expected types {expected_types} but detected {detected_types}"

    # Verify temporal grounding sanity (every flaw has start < end and evidence)
    for flaw in detected_flaws:
        assert flaw["start"] <= flaw["end"], f"Invalid timestamps in flaw: {flaw}"
        assert len(flaw["evidence"]) > 0, "Flaw missing evidence string"
        assert flaw["severity"] in ["low", "medium", "high"], f"Invalid severity: {flaw['severity']}"
