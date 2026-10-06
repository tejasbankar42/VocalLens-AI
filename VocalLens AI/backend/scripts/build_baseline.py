"""
VocalLens AI - Baseline Calibration Engine
Reads dataset/manifest.csv, runs the pipeline on all clips, calculates metric distributions,
saves dataset/baseline.json, and prints a validation table.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
import pandas as pd

from backend.app.config import (
    DATASET_DIR, BASELINE_PATH, DIMENSION_WEIGHTS, SCORE_BANDS, STORAGE_DIR
)
from backend.app.pipeline.preprocess import preprocess_audio
from backend.app.pipeline.asr import transcribe_audio
from backend.app.pipeline.audio_features import extract_acoustic_features
from backend.app.pipeline.metrics import compute_speech_metrics
from backend.app.pipeline.scorer import score_session


def build_baseline():
    manifest_path = DATASET_DIR / "manifest.csv"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found at {manifest_path}. Run generate_sample_dataset.py first.")

    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        records = list(reader)

    print(f"Loaded {len(records)} audio records from {manifest_path}")

    ideal_metrics_list: List[Dict[str, float]] = []
    flawed_metrics_list: List[Dict[str, float]] = []
    clip_results: List[Dict[str, Any]] = []

    temp_proc_dir = STORAGE_DIR / "temp_baseline"
    temp_proc_dir.mkdir(parents=True, exist_ok=True)

    for i, row in enumerate(records, start=1):
        rel_path = row["filename"]
        category = row["category"]
        audio_file = DATASET_DIR / rel_path

        if not audio_file.exists():
            print(f"  [!] Missing file: {audio_file}, skipping.")
            continue

        print(f"[{i}/{len(records)}] Processing {category.upper()}: {rel_path}...")
        
        # 1. Preprocess
        clean_wav, dur, sr = preprocess_audio(audio_file, temp_proc_dir, min_duration=3.0)

        # 2. ASR Transcription
        asr_res = transcribe_audio(clean_wav, language="en")
        words = asr_res.get("words", [])

        # 3. Acoustic features
        acoustics = extract_acoustic_features(clean_wav)

        # 4. Speech metrics
        metrics_res = compute_speech_metrics(words, dur, acoustics)
        raw_m = metrics_res["raw_metrics"]

        if category == "ideal":
            ideal_metrics_list.append(raw_m)
        else:
            flawed_metrics_list.append(raw_m)

        clip_results.append({
            "filename": rel_path,
            "category": category,
            "duration": dur,
            "raw_metrics": raw_m,
            "clean_wav": clean_wav
        })

    # Clean up temp processing files
    import shutil
    shutil.rmtree(temp_proc_dir, ignore_errors=True)

    # Compute baseline distribution statistics
    dims = list(DIMENSION_WEIGHTS.keys())
    ideal_df = pd.DataFrame(ideal_metrics_list)
    flawed_df = pd.DataFrame(flawed_metrics_list)

    baseline_data: Dict[str, Any] = {
        "ideal": {},
        "flawed": {},
        "weights": DIMENSION_WEIGHTS,
        "bands": SCORE_BANDS,
        "sample_count": {
            "ideal": len(ideal_metrics_list),
            "flawed": len(flawed_metrics_list)
        }
    }

    for dim in dims:
        if dim in ideal_df.columns:
            baseline_data["ideal"][dim] = {
                "mean": round(float(ideal_df[dim].mean()), 4),
                "std": round(max(float(ideal_df[dim].std(ddof=0)), 0.001), 4),
                "min": round(float(ideal_df[dim].min()), 4),
                "max": round(float(ideal_df[dim].max()), 4),
            }
        if dim in flawed_df.columns:
            baseline_data["flawed"][dim] = {
                "mean": round(float(flawed_df[dim].mean()), 4),
                "std": round(max(float(flawed_df[dim].std(ddof=0)), 0.001), 4),
                "min": round(float(flawed_df[dim].min()), 4),
                "max": round(float(flawed_df[dim].max()), 4),
            }

    # Save to dataset/baseline.json
    with open(BASELINE_PATH, "w", encoding="utf-8") as f:
        json.dump(baseline_data, f, indent=2)
    print(f"\nSuccessfully wrote baseline distributions to {BASELINE_PATH}\n")

    # Evaluate all clips against the new baseline and display validation table
    print("=" * 80)
    print("CONTRASTIVE VALIDATION TABLE: IDEAL VS. FLAWED SPEECH SAMPLES")
    print("=" * 80)
    print(f"{'Filename':<32} | {'Category':<8} | {'Score':<6} | {'Band':<12} | {'WPM':<5} | {'Fillers':<7}")
    print("-" * 80)

    ideal_scores = []
    flawed_scores = []

    for item in clip_results:
        eval_res = score_session(item["raw_metrics"])
        score = eval_res["overall_score"]
        band = eval_res["band"]
        cat = item["category"]

        if cat == "ideal":
            ideal_scores.append(score)
        else:
            flawed_scores.append(score)

        print(f"{item['filename']:<32} | {cat:<8} | {score:<6.1f} | {band:<12} | {item['raw_metrics'].get('pace', 0.0):<5.2f} | {item['raw_metrics'].get('fillers', 0.0):<7.2f}")

    print("-" * 80)
    avg_ideal = np.mean(ideal_scores) if ideal_scores else 0.0
    avg_flawed = np.mean(flawed_scores) if flawed_scores else 0.0
    separation = avg_ideal - avg_flawed

    print(f"AVERAGE IDEAL SCORE:  {avg_ideal:.1f}/100")
    print(f"AVERAGE FLAWED SCORE: {avg_flawed:.1f}/100")
    print(f"SCORE SEPARATION:     +{separation:.1f} points (Ideal > Flawed)")
    print("=" * 80)

    return baseline_data


if __name__ == "__main__":
    build_baseline()
