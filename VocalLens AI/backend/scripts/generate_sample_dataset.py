"""
VocalLens AI - Synthetic Contrastive Dataset Generator
Generates paired ideal and flawed audio samples with ground truth temporal annotations,
manifest.csv, and realistic flaw injection (long pauses, fillers, repetitions).
"""

import json
import csv
from pathlib import Path
import numpy as np
import soundfile as sf
import pyttsx3
import librosa
from backend.app.config import DATASET_DIR

IDEAL_DIR = DATASET_DIR / "ideal"
FLAWED_DIR = DATASET_DIR / "flawed"
MANIFEST_PATH = DATASET_DIR / "manifest.csv"
ANNOTATIONS_PATH = DATASET_DIR / "annotations.json"

# Curated Paired Scripts
SAMPLE_PAIRS = [
    {
        "id": "sample_01_interview",
        "title": "Software Engineering Interview Introduction",
        "ideal_segments": [
            "Good morning. I am excited to share my experience building scalable distributed cloud architectures.",
            "Over the past four years, I have architected resilient microservices and optimized high-throughput database pipelines.",
            "My focus has consistently centered on writing maintainable code and mentoring junior engineers.",
            "I look forward to discussing how my technical background aligns with your engineering initiatives."
        ],
        "flawed_segments": [
            ("Good morning, um, I am", "filler", "um"),
            ("like basically trying to share my experience with", "filler", "like"),
            ("SILENCE_2.2", "long_pause", "2.2 s hesitation"),
            ("distributed systems. And uh, over the past years,", "filler", "uh"),
            ("we we built several microservices.", "repetition", "we we"),
            ("SILENCE_1.8", "long_pause", "1.8 s silence"),
            ("You know, sort of optimizing databases, basically.", "filler", "you know")
        ]
    },
    {
        "id": "sample_02_pitch",
        "title": "AI Product Demonstration Pitch",
        "ideal_segments": [
            "Welcome everyone. Today we are launching VocalLens AI, a breakthrough in automated communication coaching.",
            "Our platform accurately tracks speech pacing, vocal clarity, and disfluency in real time.",
            "By contrasting your speech with verified exemplars, we deliver personalized actionable recommendations.",
            "This empowers every speaker to communicate with precision, confidence, and lasting authority."
        ],
        "flawed_segments": [
            ("So uh, welcome everyone. Today, um,", "filler", "uh"),
            ("our product is like basically revolutionary.", "filler", "basically"),
            ("SILENCE_2.5", "long_pause", "2.5 s pause"),
            ("It measures how you speak, and uh, like,", "filler", "like"),
            ("because because it gives you scores,", "repetition", "because because"),
            ("SILENCE_1.9", "long_pause", "1.9 s pause"),
            ("matlab it helps you improve your confidence, you know.", "filler", "matlab")
        ]
    },
    {
        "id": "sample_03_leadership",
        "title": "Executive Project Milestone Review",
        "ideal_segments": [
            "Good afternoon leadership team. I am pleased to report that our core milestones are fully on schedule.",
            "We have successfully completed system integration testing with zero critical blockers remaining.",
            "Our cross-functional teams have demonstrated exceptional execution, velocity, and discipline.",
            "Next week we commence deployment into our primary staging environments."
        ],
        "flawed_segments": [
            ("Uh, good afternoon everyone. Um,", "filler", "um"),
            ("SILENCE_2.1", "long_pause", "2.1 s hesitation"),
            ("basically our project status is, like,", "filler", "like"),
            ("mostly mostly on schedule.", "repetition", "mostly mostly"),
            ("SILENCE_1.7", "long_pause", "1.7 s pause"),
            ("And uh, we are trying to fix some blockers, sort of.", "filler", "uh")
        ]
    },
    {
        "id": "sample_04_support",
        "title": "Customer Solution & Technical Support",
        "ideal_segments": [
            "Thank you for contacting our technical support team. I have thoroughly investigated your account issue.",
            "We have identified the root cause in the authentication handshake and deployed an immediate configuration patch.",
            "Your service is now fully restored and functioning with nominal latency across all regions.",
            "Please let me know if you would like me to walk through the preventative safeguards we implemented."
        ],
        "flawed_segments": [
            ("Um, thank you for reaching out. Like,", "filler", "like"),
            ("SILENCE_2.3", "long_pause", "2.3 s dead pause"),
            ("we checked your account and, uh, basically,", "filler", "basically"),
            ("there was a bug. I I found the issue,", "repetition", "I I"),
            ("SILENCE_1.8", "long_pause", "1.8 s silence"),
            ("and uh, it should work now, toh you can try logging in.", "filler", "toh")
        ]
    },
    {
        "id": "sample_05_research",
        "title": "Scientific Data & Analysis Presentation",
        "ideal_segments": [
            "Our latest empirical research demonstrates a statistically significant improvement across speech evaluation benchmarks.",
            "We analyzed over ten thousand speech segments using contrastive acoustic feature embeddings.",
            "The experimental results confirm that temporal grounding substantially enhances feedback interpretability.",
            "These findings establish a reproducible baseline for future intelligent communication diagnostics."
        ],
        "flawed_segments": [
            ("Uh, so our research shows, like,", "filler", "like"),
            ("SILENCE_2.4", "long_pause", "2.4 s pause"),
            ("um, basically significant results.", "filler", "um"),
            ("We we tested thousands of audio clips,", "repetition", "we we"),
            ("SILENCE_2.0", "long_pause", "2.0 s pause"),
            ("and uh, the system works pretty well, you know.", "filler", "you know")
        ]
    }
]


def render_tts(text: str, temp_wav_path: Path, rate: int = 150):
    """Renders text to a temporary WAV file using pyttsx3."""
    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.save_to_file(text, str(temp_wav_path))
    engine.runAndWait()


def build_ideal_audio(pair: dict, output_path: Path) -> float:
    """Generates an ideal audio clip with balanced pacing and natural short breath pauses."""
    target_sr = 16000
    all_audio = []
    
    # 0.4s initial quiet padding
    all_audio.append(np.zeros(int(0.4 * target_sr), dtype=np.float32))

    temp_file = output_path.parent / f"temp_{output_path.stem}.wav"

    for seg in pair["ideal_segments"]:
        render_tts(seg, temp_file, rate=155)
        data, sr = sf.read(str(temp_file))
        if sr != target_sr:
            data = librosa.resample(data.astype(np.float32), orig_sr=sr, target_sr=target_sr)
        if data.ndim > 1:
            data = data.mean(axis=1)
        all_audio.append(data.astype(np.float32))
        
        # Natural conversational breathing pause between sentences (0.45s)
        natural_pause = np.zeros(int(0.45 * target_sr), dtype=np.float32)
        all_audio.append(natural_pause)

    if temp_file.exists():
        temp_file.unlink()

    final_audio = np.concatenate(all_audio)
    # Normalize peak amplitude
    max_amp = np.max(np.abs(final_audio))
    if max_amp > 0:
        final_audio = final_audio / max_amp * 0.90

    sf.write(str(output_path), final_audio, target_sr, subtype="PCM_16")
    return float(len(final_audio)) / target_sr


def build_flawed_audio(pair: dict, output_path: Path) -> tuple[float, list]:
    """
    Generates a flawed audio clip with synthesized filler phrases, long dead pauses,
    and repetitions, tracking precise ground-truth flaw timestamps.
    """
    target_sr = 16000
    all_audio = []
    annotations = []
    current_time = 0.3

    # Initial silence
    all_audio.append(np.zeros(int(0.3 * target_sr), dtype=np.float32))
    temp_file = output_path.parent / f"temp_{output_path.stem}.wav"

    for item in pair["flawed_segments"]:
        phrase_or_silence, flaw_type, detail = item

        if phrase_or_silence.startswith("SILENCE_"):
            silence_len = float(phrase_or_silence.split("_")[1])
            start_t = round(current_time, 2)
            end_t = round(current_time + silence_len, 2)
            
            silence_samples = np.zeros(int(silence_len * target_sr), dtype=np.float32)
            all_audio.append(silence_samples)
            current_time += silence_len

            annotations.append({
                "type": "long_pause",
                "start": start_t,
                "end": end_t,
                "severity": "high" if silence_len >= 2.0 else "medium",
                "evidence": f"{silence_len:.1f} s silence gap",
                "tip": "Reduce dead silences; keep pauses under 0.8s."
            })
        else:
            # Render spoken phrase (rate varies to simulate hesitation/rushing)
            rate = 135
            render_tts(phrase_or_silence, temp_file, rate=rate)
            data, sr = sf.read(str(temp_file))
            if sr != target_sr:
                data = librosa.resample(data.astype(np.float32), orig_sr=sr, target_sr=target_sr)
            if data.ndim > 1:
                data = data.mean(axis=1)

            seg_dur = float(len(data)) / target_sr
            start_t = round(current_time, 2)
            end_t = round(current_time + seg_dur, 2)

            all_audio.append(data.astype(np.float32))
            current_time += seg_dur

            # Record flaw annotation
            if flaw_type == "filler":
                annotations.append({
                    "type": "filler",
                    "start": start_t,
                    "end": min(end_t, start_t + 1.2),
                    "severity": "high" if detail in ["um", "uh", "matlab"] else "medium",
                    "evidence": f"Filler '{detail}' used.",
                    "tip": "Pause silently instead of verbalizing filler sounds."
                })
            elif flaw_type == "repetition":
                annotations.append({
                    "type": "repetition",
                    "start": start_t,
                    "end": end_t,
                    "severity": "medium",
                    "evidence": f"Word repetition '{detail}'.",
                    "tip": "Speak in measured phrases to avoid false-starts."
                })

            # Small 0.2s transition gap
            all_audio.append(np.zeros(int(0.2 * target_sr), dtype=np.float32))
            current_time += 0.2

    if temp_file.exists():
        temp_file.unlink()

    final_audio = np.concatenate(all_audio)
    max_amp = np.max(np.abs(final_audio))
    if max_amp > 0:
        final_audio = final_audio / max_amp * 0.90

    sf.write(str(output_path), final_audio, target_sr, subtype="PCM_16")
    total_dur = float(len(final_audio)) / target_sr
    return total_dur, annotations


def generate_dataset():
    """Generates the full contrastive sample dataset."""
    IDEAL_DIR.mkdir(parents=True, exist_ok=True)
    FLAWED_DIR.mkdir(parents=True, exist_ok=True)

    manifest_rows = []
    annotations_dict = {}

    print(f"Generating {len(SAMPLE_PAIRS)} contrastive speech pairs...")

    for i, pair in enumerate(SAMPLE_PAIRS, start=1):
        pair_id = pair["id"]
        
        # 1. Generate Ideal
        ideal_filename = f"ideal_{i:02d}_{pair_id}.wav"
        ideal_path = IDEAL_DIR / ideal_filename
        ideal_dur = build_ideal_audio(pair, ideal_path)
        manifest_rows.append({
            "filename": f"ideal/{ideal_filename}",
            "category": "ideal",
            "speaker_id": f"speaker_{i % 2 + 1}",
            "duration": round(ideal_dur, 2),
            "script_id": pair_id
        })
        print(f"  [+] Generated ideal clip: {ideal_filename} ({ideal_dur:.1f}s)")

        # 2. Generate Flawed
        flawed_filename = f"flawed_{i:02d}_{pair_id}.wav"
        flawed_path = FLAWED_DIR / flawed_filename
        flawed_dur, flaws = build_flawed_audio(pair, flawed_path)
        manifest_rows.append({
            "filename": f"flawed/{flawed_filename}",
            "category": "flawed",
            "speaker_id": f"speaker_{i % 2 + 1}",
            "duration": round(flawed_dur, 2),
            "script_id": pair_id
        })
        annotations_dict[f"flawed/{flawed_filename}"] = flaws
        print(f"  [+] Generated flawed clip: {flawed_filename} ({flawed_dur:.1f}s, {len(flaws)} flaws)")

    # Save manifest.csv
    with open(MANIFEST_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "category", "speaker_id", "duration", "script_id"])
        writer.writeheader()
        writer.writerows(manifest_rows)
    print(f"Saved manifest to {MANIFEST_PATH}")

    # Save annotations.json
    with open(ANNOTATIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(annotations_dict, f, indent=2)
    print(f"Saved annotations to {ANNOTATIONS_PATH}")


if __name__ == "__main__":
    generate_dataset()
