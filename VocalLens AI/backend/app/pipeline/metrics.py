"""
VocalLens AI - Speech Metrics Computation Engine
Computes raw measurements for:
Pace, Pauses, Fillers, Fluency, Clarity, Pronunciation, Confidence, and Vocabulary.
"""

import re
from typing import List, Dict, Any, Tuple
import numpy as np
from backend.app.config import (
    FILLER_WORDS, HEDGE_WORDS, PAUSE_MEDIUM_THRESHOLD, PAUSE_HIGH_THRESHOLD,
    SLIDING_WINDOW_SEC, WPM_TOO_FAST, WPM_TOO_SLOW,
    LOW_CONFIDENCE_WORD_THRESHOLD, IDEAL_WPM_MIN, IDEAL_WPM_MAX
)


def clean_text_token(word: str) -> str:
    """Removes punctuation and lowercases a token."""
    return re.sub(r"[^\w\s]", "", word).strip().lower()


def compute_speech_metrics(
    words: List[Dict[str, Any]],
    duration_sec: float,
    acoustic_features: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes all 8 dimensions with detailed temporal statistics.
    Returns:
    {
        "raw_metrics": { ... 8 dimension raw values ... },
        "pause_events": [...],
        "filler_events": [...],
        "repeat_events": [...],
        "speed_events": [...],
        "sliding_wpm_profile": [...],
        "summary": {...}
    }
    """
    safe_duration = max(duration_sec, 0.5)
    clean_tokens = [clean_text_token(w["word"]) for w in words]
    total_words = len([t for t in clean_tokens if t])

    # -------------------------------------------------------------
    # 1. PACE: Overall WPM & 10s Sliding Window Profile
    # -------------------------------------------------------------
    overall_wpm = (total_words / safe_duration) * 60.0

    sliding_wpm_profile: List[Dict[str, float]] = []
    speed_flaw_events: List[Dict[str, Any]] = []
    
    # 10s window sliding every 2 seconds
    window_step = 2.0
    num_windows = int(max(0, safe_duration - SLIDING_WINDOW_SEC) / window_step) + 1
    
    for i in range(num_windows):
        w_start = i * window_step
        w_end = w_start + SLIDING_WINDOW_SEC
        # Count words falling in this window
        window_words = [
            w for w in words 
            if w_start <= w["start"] < w_end
        ]
        w_count = len(window_words)
        w_wpm = (w_count / SLIDING_WINDOW_SEC) * 60.0
        sliding_wpm_profile.append({
            "start": round(w_start, 2),
            "end": round(w_end, 2),
            "wpm": round(w_wpm, 1),
            "word_count": w_count
        })

        if w_wpm > WPM_TOO_FAST and w_count >= 5:
            speed_flaw_events.append({
                "type": "too_fast",
                "start": round(w_start, 2),
                "end": round(w_end, 2),
                "severity": "high" if w_wpm > 190 else "medium",
                "evidence": f"Pace spiked to {round(w_wpm)} WPM across a 10s window ({w_count} words).",
                "tip": "Ease back your pace. Aim for 130–150 WPM so your audience can comfortably absorb your points."
            })
        elif w_wpm < WPM_TOO_SLOW and w_count > 0:
            speed_flaw_events.append({
                "type": "too_slow",
                "start": round(w_start, 2),
                "end": round(w_end, 2),
                "severity": "high" if w_wpm < 70 else "medium",
                "evidence": f"Pace dropped to {round(w_wpm)} WPM across a 10s window ({w_count} words).",
                "tip": "Maintain momentum between phrases to keep your listener actively engaged."
            })

    # Pace consistency score: penalize deviation from ideal range [130, 155]
    if overall_wpm < IDEAL_WPM_MIN:
        pace_index = max(0.0, 1.0 - ((IDEAL_WPM_MIN - overall_wpm) / 70.0))
    elif overall_wpm > IDEAL_WPM_MAX:
        pace_index = max(0.0, 1.0 - ((overall_wpm - IDEAL_WPM_MAX) / 80.0))
    else:
        pace_index = 1.0

    # -------------------------------------------------------------
    # 2. PAUSES: Inter-word gaps > 1.2s (> 2.0s is high severity)
    # -------------------------------------------------------------
    pause_events: List[Dict[str, Any]] = []
    total_pause_duration = 0.0

    for i in range(len(words) - 1):
        prev_word = words[i]
        next_word = words[i + 1]
        gap = round(next_word["start"] - prev_word["end"], 2)

        if gap >= PAUSE_MEDIUM_THRESHOLD:
            severity = "high" if gap >= PAUSE_HIGH_THRESHOLD else "medium"
            total_pause_duration += gap
            pause_events.append({
                "type": "long_pause",
                "start": round(prev_word["end"], 2),
                "end": round(next_word["start"], 2),
                "severity": severity,
                "evidence": f"{gap:.1f} s silence between '{prev_word['word']}' and '{next_word['word']}'",
                "tip": "Replace long dead pauses with smooth transitions or deliberate 0.5s punctuation breaths."
            })

    pause_count = len(pause_events)
    pause_ratio = min(1.0, total_pause_duration / safe_duration)

    # -------------------------------------------------------------
    # 3. FILLERS: English & Hinglish Filler Words
    # -------------------------------------------------------------
    filler_events: List[Dict[str, Any]] = []
    filler_tokens_set = set(FILLER_WORDS)
    
    # Check single tokens and 2-word n-grams
    i = 0
    while i < len(words):
        w = words[i]
        token = clean_text_token(w["word"])
        
        # Check two-word phrases like 'you know', 'sort of', 'kind of'
        matched_phrase = False
        if i + 1 < len(words):
            next_w = words[i + 1]
            two_word = f"{token} {clean_text_token(next_w['word'])}"
            if two_word in filler_tokens_set:
                filler_events.append({
                    "type": "filler",
                    "start": w["start"],
                    "end": next_w["end"],
                    "severity": "medium",
                    "evidence": f"Filler phrase '{two_word}' detected.",
                    "tip": "Pause silently instead of using verbal crutches like 'you know' or 'sort of'."
                })
                i += 2
                matched_phrase = True
                continue

        if token in filler_tokens_set:
            severity = "high" if token in ["um", "uh", "matlab"] else "medium"
            filler_events.append({
                "type": "filler",
                "start": w["start"],
                "end": w["end"],
                "severity": severity,
                "evidence": f"Filler sound '{token}' spoken.",
                "tip": "Breathe gently and pause silently in place of saying filler words."
            })

        i += 1

    filler_count = len(filler_events)
    filler_rate_per_min = (filler_count / safe_duration) * 60.0

    # -------------------------------------------------------------
    # 4. FLUENCY: Repeats, Restarts & Disfluency
    # -------------------------------------------------------------
    repeat_events: List[Dict[str, Any]] = []
    repeat_count = 0

    for i in range(len(words) - 1):
        w1 = clean_text_token(words[i]["word"])
        w2 = clean_text_token(words[i + 1]["word"])
        if w1 and w2 and w1 == w2 and len(w1) > 1:
            repeat_count += 1
            repeat_events.append({
                "type": "repetition",
                "start": words[i]["start"],
                "end": words[i + 1]["end"],
                "severity": "medium",
                "evidence": f"Immediate repetition of '{words[i]['word']} {words[i+1]['word']}'.",
                "tip": "Speak in deliberate phrases to eliminate word stutter and accidental double-starts."
            })

    # Restarts / false starts penalty
    restart_count = 0
    for w in words:
        if w["word"].endswith("-") or w["word"].endswith("—"):
            restart_count += 1

    disfluency_score = (repeat_count * 0.08) + (restart_count * 0.05) + (pause_ratio * 0.5)
    fluency_index = max(0.0, min(1.0, 1.0 - disfluency_score))

    # -------------------------------------------------------------
    # 5. CLARITY: Mean ASR Confidence
    # -------------------------------------------------------------
    if words:
        mean_confidence = float(np.mean([w["probability"] for w in words]))
    else:
        mean_confidence = 0.5

    # -------------------------------------------------------------
    # 6. PRONUNCIATION: Share of Low-Confidence Words (< 0.5)
    # -------------------------------------------------------------
    low_prob_words = [w for w in words if w["probability"] < LOW_CONFIDENCE_WORD_THRESHOLD]
    low_prob_share = len(low_prob_words) / max(total_words, 1)
    pronunciation_index = max(0.0, 1.0 - low_prob_share)

    # -------------------------------------------------------------
    # 7. CONFIDENCE: Pitch Dynamics, RMS Stability, Hedge Words
    # -------------------------------------------------------------
    pitch_std = acoustic_features.get("std_pitch_hz", 20.0)
    energy_stability = acoustic_features.get("energy_stability", 0.7)
    
    # Detect Hedge Words
    hedge_count = 0
    for token in clean_tokens:
        if token in HEDGE_WORDS:
            hedge_count += 1
            
    # Pitch dynamic factor (healthy variation is 15-45 Hz)
    pitch_factor = min(1.0, max(0.2, pitch_std / 30.0))
    hedge_penalty = min(0.4, (hedge_count / max(total_words, 1)) * 4.0)
    confidence_index = max(0.0, min(1.0, (0.45 * pitch_factor) + (0.45 * energy_stability) - hedge_penalty + 0.1))

    # -------------------------------------------------------------
    # 8. VOCABULARY: Unique-Word Ratio (TTR) & Average Word Length
    # -------------------------------------------------------------
    meaningful_tokens = [t for t in clean_tokens if len(t) > 2 and t not in filler_tokens_set]
    if meaningful_tokens:
        unique_tokens = set(meaningful_tokens)
        ttr = len(unique_tokens) / len(meaningful_tokens)
        avg_word_len = sum(len(t) for t in meaningful_tokens) / len(meaningful_tokens)
    else:
        ttr = 0.5
        avg_word_len = 4.5

    # Normalized vocab composite
    vocab_index = max(0.0, min(1.0, (0.6 * ttr) + (0.4 * min(avg_word_len / 6.5, 1.0))))

    # Raw metrics dictionary
    raw_metrics = {
        "clarity": round(mean_confidence, 4),
        "fluency": round(fluency_index, 4),
        "pace": round(pace_index, 4),
        "pauses": round(pause_ratio, 4),
        "fillers": round(filler_rate_per_min, 3),
        "pronunciation": round(pronunciation_index, 4),
        "confidence": round(confidence_index, 4),
        "vocabulary": round(vocab_index, 4),
    }

    # Summary measurements for display
    summary = {
        "duration_sec": round(safe_duration, 2),
        "total_words": total_words,
        "overall_wpm": round(overall_wpm, 1),
        "pause_count": pause_count,
        "total_pause_duration": round(total_pause_duration, 2),
        "filler_count": filler_count,
        "filler_rate_per_min": round(filler_rate_per_min, 2),
        "repeat_count": repeat_count,
        "mean_confidence": round(mean_confidence, 3),
        "low_prob_word_count": len(low_prob_words),
        "pitch_mean_hz": acoustic_features.get("mean_pitch_hz", 120.0),
        "pitch_std_hz": pitch_std,
        "ttr": round(ttr, 3),
        "avg_word_len": round(avg_word_len, 2),
    }

    return {
        "raw_metrics": raw_metrics,
        "summary": summary,
        "pause_events": pause_events,
        "filler_events": filler_events,
        "repeat_events": repeat_events,
        "speed_events": speed_flaw_events,
        "sliding_wpm_profile": sliding_wpm_profile,
    }
