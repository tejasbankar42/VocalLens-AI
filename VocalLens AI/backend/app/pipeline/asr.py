"""
VocalLens AI - Automatic Speech Recognition Pipeline
Uses faster-whisper (small, int8) with word-level timestamps and probability extraction.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from faster_whisper import WhisperModel
from backend.app.config import WHISPER_MODEL_SIZE, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE

_whisper_instance: Optional[WhisperModel] = None


def get_whisper_model() -> WhisperModel:
    """Singleton getter for WhisperModel."""
    global _whisper_instance
    if _whisper_instance is None:
        _whisper_instance = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
            download_root=None,
        )
    return _whisper_instance


def transcribe_audio(
    wav_path: Path, 
    language: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transcribes audio with word-level timestamps and confidence scores.
    Returns:
    {
        "text": full transcript text,
        "language": detected or specified language,
        "words": [
            {"word": "Hello", "start": 0.12, "end": 0.45, "probability": 0.98},
            ...
        ],
        "segments": [...]
    }
    """
    model = get_whisper_model()
    
    # Handle language mapping: 'hinglish' uses 'en' or auto with Hindi context
    lang_param = language
    if language in ["hinglish", "en-in", "hi-en"]:
        lang_param = None  # Whisper handles mixed-code better in auto or standard mode

    # Read audio with soundfile to avoid PyAV metadata_errors keyword issue in newer av versions
    import soundfile as sf
    import numpy as np
    audio_data, sr = sf.read(str(wav_path))
    if audio_data.ndim > 1:
        audio_data = audio_data.mean(axis=1)
    audio_data = audio_data.astype(np.float32)

    segments, info = model.transcribe(
        audio_data,
        word_timestamps=True,
        language=lang_param,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )

    words_list: List[Dict[str, Any]] = []
    text_segments: List[str] = []
    raw_segments: List[Dict[str, Any]] = []

    for seg in segments:
        text_segments.append(seg.text.strip())
        raw_segments.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip(),
            "avg_logprob": seg.avg_logprob,
        })
        if seg.words:
            for w in seg.words:
                cleaned_word = w.word.strip()
                if cleaned_word:
                    words_list.append({
                        "word": cleaned_word,
                        "start": round(w.start, 2),
                        "end": round(w.end, 2),
                        "probability": round(float(w.probability), 3),
                    })

    full_text = " ".join(text_segments).strip()

    return {
        "text": full_text,
        "language": info.language if info else (language or "en"),
        "language_probability": round(info.language_probability, 3) if info else 1.0,
        "words": words_list,
        "segments": raw_segments,
    }
