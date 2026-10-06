"""
VocalLens AI - Temporal Flaw Grounding Detector
Identifies precise timestamped flaw events across the audio timeline:
- long_pause
- filler
- too_fast
- too_slow
- repetition
- mumble (3+ low probability words in a row)
- monotone (8s+ flat pitch)
"""

from typing import List, Dict, Any
from backend.app.config import (
    MUMBLE_PROB_THRESHOLD, MUMBLE_CONSECUTIVE_WORDS
)


def detect_mumble_events(words: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detects 3 or more consecutive words with low ASR probability."""
    mumble_events: List[Dict[str, Any]] = []
    current_run: List[Dict[str, Any]] = []

    for w in words:
        if w["probability"] < MUMBLE_PROB_THRESHOLD:
            current_run.append(w)
        else:
            if len(current_run) >= MUMBLE_CONSECUTIVE_WORDS:
                start = current_run[0]["start"]
                end = current_run[-1]["end"]
                avg_prob = sum(x["probability"] for x in current_run) / len(current_run)
                words_str = " ".join(x["word"] for x in current_run)
                mumble_events.append({
                    "type": "mumble",
                    "start": round(start, 2),
                    "end": round(end, 2),
                    "severity": "high" if avg_prob < 0.35 or len(current_run) >= 4 else "medium",
                    "evidence": f"Unclear articulation on {len(current_run)} words: \"{words_str}\" (avg confidence {int(avg_prob * 100)}%).",
                    "tip": "Articulate consonants deliberately and open your mouth slightly wider to project clear sound."
                })
            current_run = []

    # Check terminal run
    if len(current_run) >= MUMBLE_CONSECUTIVE_WORDS:
        start = current_run[0]["start"]
        end = current_run[-1]["end"]
        avg_prob = sum(x["probability"] for x in current_run) / len(current_run)
        words_str = " ".join(x["word"] for x in current_run)
        mumble_events.append({
            "type": "mumble",
            "start": round(start, 2),
            "end": round(end, 2),
            "severity": "high" if avg_prob < 0.35 or len(current_run) >= 4 else "medium",
            "evidence": f"Unclear articulation on {len(current_run)} words: \"{words_str}\" (avg confidence {int(avg_prob * 100)}%).",
            "tip": "Articulate consonants deliberately and open your mouth slightly wider to project clear sound."
        })

    return mumble_events


def detect_monotone_events(acoustic_features: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Transforms acoustic monotone regions into temporal flaw events."""
    monotone_flaws: List[Dict[str, Any]] = []
    regions = acoustic_features.get("monotone_regions", [])

    for r in regions:
        start = r["start"]
        end = r["end"]
        duration = round(end - start, 1)
        pitch_std = r.get("pitch_std", 10.0)
        monotone_flaws.append({
            "type": "monotone",
            "start": start,
            "end": end,
            "severity": "high" if pitch_std < 8.0 else "medium",
            "evidence": f"Pitch deviation stayed flat (std {pitch_std:.1f} Hz) for {duration} seconds.",
            "tip": "Vary your pitch up and down to underline key verbs and ideas. Express vocal emotion."
        })

    return monotone_flaws


def ground_flaw_events(
    words: List[Dict[str, Any]],
    computed_metrics: Dict[str, Any],
    acoustic_features: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Aggregates and grounds all temporal flaw events across the speech recording,
    sorted by timestamp.
    """
    all_events: List[Dict[str, Any]] = []

    # 1. Pauses
    all_events.extend(computed_metrics.get("pause_events", []))

    # 2. Fillers
    all_events.extend(computed_metrics.get("filler_events", []))

    # 3. Repetitions
    all_events.extend(computed_metrics.get("repeat_events", []))

    # 4. Pace spikes & slumps
    all_events.extend(computed_metrics.get("speed_events", []))

    # 5. Mumble sequences
    mumble_events = detect_mumble_events(words)
    all_events.extend(mumble_events)

    # 6. Monotone intervals
    monotone_events = detect_monotone_events(acoustic_features)
    all_events.extend(monotone_events)

    # Sort strictly by start time
    all_events.sort(key=lambda x: (x["start"], x["end"]))

    return all_events
