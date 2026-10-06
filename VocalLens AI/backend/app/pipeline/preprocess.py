"""
VocalLens AI - Audio Preprocessing Pipeline
Standardizes input audio into 16kHz mono WAV, validates duration, and sanitizes format.
"""

from pathlib import Path
import shutil
import numpy as np
import soundfile as sf
import av

class AudioPreprocessingError(ValueError):
    """Custom exception for preprocessing errors."""
    pass


def load_audio_to_numpy(file_path: Path, target_sr: int = 16000) -> tuple[np.ndarray, float]:
    """
    Decodes audio from various formats (wav, mp3, m4a, webm, ogg, flac) using PyAV,
    resamples to target_sr, converts to mono, and returns (audio_array, duration_seconds).
    """
    try:
        container = av.open(str(file_path))
    except Exception as e:
        raise AudioPreprocessingError(f"Unsupported or corrupted audio file: {e}")

    audio_stream = next((s for s in container.streams if s.type == "audio"), None)
    if audio_stream is None:
        raise AudioPreprocessingError("No audio stream found in the uploaded file.")

    resampler = av.AudioResampler(
        format="s16",
        layout="mono",
        rate=target_sr
    )

    frames = []
    for frame in container.decode(audio_stream):
        resampled_frames = resampler.resample(frame)
        for r_frame in resampled_frames:
            array = r_frame.to_ndarray()
            frames.append(array.flatten())

    if not frames:
        raise AudioPreprocessingError("Audio stream is empty.")

    audio_data = np.concatenate(frames).astype(np.float32) / 32768.0
    duration = float(len(audio_data)) / float(target_sr)

    return audio_data, duration


def preprocess_audio(input_path: Path, output_dir: Path, min_duration: float = 5.0) -> tuple[Path, float, int]:
    """
    Processes an incoming audio file:
    - Validates presence and non-emptiness
    - Decodes and converts to 16kHz Mono WAV
    - Validates minimum duration (> min_duration seconds)
    - Returns (normalized_wav_path, duration_seconds, sample_rate)
    """
    if not input_path.exists():
        raise AudioPreprocessingError(f"Input file does not exist: {input_path}")

    target_sr = 16000
    audio_data, duration = load_audio_to_numpy(input_path, target_sr=target_sr)

    if duration < min_duration:
        raise AudioPreprocessingError(
            f"Audio duration is {duration:.1f}s. VocalLens requires at least {min_duration:.1f} seconds of speech for accurate contrastive analysis."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    clean_wav_path = output_dir / f"processed_{input_path.stem}.wav"
    sf.write(str(clean_wav_path), audio_data, target_sr, subtype="PCM_16")

    return clean_wav_path, duration, target_sr
