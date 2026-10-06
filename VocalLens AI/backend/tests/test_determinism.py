"""
VocalLens AI - Determinism Test
Validates that the same audio input evaluated twice yields identical numerical scores.
"""

from pathlib import Path
from backend.app.pipeline.asr import transcribe_audio
from backend.app.pipeline.audio_features import extract_acoustic_features
from backend.app.pipeline.metrics import compute_speech_metrics
from backend.app.pipeline.scorer import score_session


def evaluate_clip(wav_path: Path):
    asr_res = transcribe_audio(wav_path, language="en")
    words = asr_res["words"]
    import soundfile as sf
    data, sr = sf.read(str(wav_path))
    duration = float(len(data)) / float(sr)
    acoustics = extract_acoustic_features(wav_path)
    metrics_res = compute_speech_metrics(words, duration, acoustics)
    score_res = score_session(metrics_res["raw_metrics"])
    return score_res


def test_scoring_determinism(sample_ideal_wav):
    """Evaluating the same audio clip twice must return exact identical scores."""
    result1 = evaluate_clip(sample_ideal_wav)
    result2 = evaluate_clip(sample_ideal_wav)

    assert result1["overall_score"] == result2["overall_score"], (
        f"Score mismatch: {result1['overall_score']} vs {result2['overall_score']}"
    )
    assert result1["band"] == result2["band"], (
        f"Band mismatch: {result1['band']} vs {result2['band']}"
    )

    for dim in result1["dimension_scores"]:
        s1 = result1["dimension_scores"][dim]
        s2 = result2["dimension_scores"][dim]
        assert s1 == s2, f"Dimension '{dim}' mismatch: {s1} vs {s2}"
