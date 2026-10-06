"""
VocalLens AI - Deterministic Contrastive Scorer
Calculates reproducible scores for 8 speech dimensions by contrasting with
ideal and flawed speech baseline distributions.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from backend.app.config import (
    BASELINE_PATH, DIMENSION_WEIGHTS, SCORE_BANDS
)

# Robust fallback baseline priors if baseline.json has not been built yet
DEFAULT_BASELINE = {
    "ideal": {
        "clarity": {"mean": 0.94, "std": 0.04},
        "fluency": {"mean": 0.92, "std": 0.05},
        "pace": {"mean": 0.95, "std": 0.04},
        "pauses": {"mean": 0.04, "std": 0.03},
        "fillers": {"mean": 0.40, "std": 0.30},
        "pronunciation": {"mean": 0.96, "std": 0.03},
        "confidence": {"mean": 0.88, "std": 0.05},
        "vocabulary": {"mean": 0.78, "std": 0.06},
    },
    "flawed": {
        "clarity": {"mean": 0.68, "std": 0.08},
        "fluency": {"mean": 0.52, "std": 0.10},
        "pace": {"mean": 0.48, "std": 0.12},
        "pauses": {"mean": 0.28, "std": 0.08},
        "fillers": {"mean": 6.80, "std": 2.10},
        "pronunciation": {"mean": 0.70, "std": 0.09},
        "confidence": {"mean": 0.46, "std": 0.10},
        "vocabulary": {"mean": 0.48, "std": 0.08},
    }
}


def load_baseline() -> Dict[str, Any]:
    """Loads baseline parameters from dataset/baseline.json or falls back to defaults."""
    if BASELINE_PATH.exists():
        try:
            with open(BASELINE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "ideal" in data and "flawed" in data:
                    return data
        except Exception:
            pass
    return DEFAULT_BASELINE


def calculate_dimension_score(x: float, ideal_mean: float, flawed_mean: float) -> float:
    """
    Deterministic contrastive scoring formula:
    score = clip((x - flawed_mean) / (ideal_mean - flawed_mean), 0, 1) * 100
    Works identically for both positive metrics (ideal > flawed) and
    inverted penalty metrics (ideal < flawed).
    """
    denom = ideal_mean - flawed_mean
    if abs(denom) < 1e-6:
        return 50.0

    raw_ratio = (x - flawed_mean) / denom
    clipped = max(0.0, min(1.0, raw_ratio))
    return round(clipped * 100.0, 1)


def score_session(raw_metrics: Dict[str, float]) -> Dict[str, Any]:
    """
    Computes contrastive scores, overall weighted score, score band,
    strengths, and weaknesses.
    """
    baseline = load_baseline()
    ideal_stats = baseline.get("ideal", DEFAULT_BASELINE["ideal"])
    flawed_stats = baseline.get("flawed", DEFAULT_BASELINE["flawed"])

    dimension_scores: Dict[str, float] = {}
    dimension_details: List[Dict[str, Any]] = []

    total_weighted_score = 0.0
    total_weights = 0.0

    for dim, weight in DIMENSION_WEIGHTS.items():
        raw_val = raw_metrics.get(dim, 0.5)
        ideal_mean = ideal_stats.get(dim, {}).get("mean", 1.0)
        flawed_mean = flawed_stats.get(dim, {}).get("mean", 0.0)

        dim_score = calculate_dimension_score(raw_val, ideal_mean, flawed_mean)
        dimension_scores[dim] = dim_score
        
        dimension_details.append({
            "dimension": dim,
            "score": dim_score,
            "raw_value": raw_val,
            "weight": weight
        })

        total_weighted_score += (dim_score * weight)
        total_weights += weight

    overall_score = round(total_weighted_score / max(total_weights, 1.0), 1)

    # Determine Score Band
    assigned_band = "Weak"
    for band_name, (low, high) in SCORE_BANDS.items():
        if low <= overall_score <= high:
            assigned_band = band_name
            break
        if overall_score >= 100.0:
            assigned_band = "Excellent"
            break

    # Rank strengths and weaknesses
    ranked = sorted(dimension_scores.items(), key=lambda item: item[1], reverse=True)
    strengths = [dim for dim, s in ranked[:3] if s >= 60.0]
    if not strengths and ranked:
        strengths = [ranked[0][0]]

    weaknesses = [dim for dim, s in ranked[-3:] if s < 80.0]
    if not weaknesses and ranked:
        weaknesses = [ranked[-1][0]]
    # Ensure no duplicate overlap if few dimensions
    weaknesses = [w for w in weaknesses if w not in strengths]

    return {
        "overall_score": overall_score,
        "band": assigned_band,
        "dimension_scores": dimension_scores,
        "dimension_details": dimension_details,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "baseline_comparison": {
            dim: {
                "user": dimension_scores[dim],
                "user_raw": raw_metrics.get(dim, 0.0),
                "ideal_mean": ideal_stats.get(dim, {}).get("mean", 0.0),
                "flawed_mean": flawed_stats.get(dim, {}).get("mean", 0.0),
            }
            for dim in DIMENSION_WEIGHTS
        }
    }
