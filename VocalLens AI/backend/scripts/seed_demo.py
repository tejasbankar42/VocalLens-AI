"""
VocalLens AI - Demo Seeder Script
Initializes the SQLite database with rich demo users, historical practice sessions,
flaw grounding events, dimension scores, and progress trends.
"""

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from backend.app.db import engine, SessionLocal, Base
from backend.app.models import User, SessionModel, DimensionScore, FlawEvent
from backend.app.config import STORAGE_DIR

# Sample flagship transcript with word timestamps
DEMO_WORDS_EXCELLENT = [
    {"word": "Good", "start": 0.35, "end": 0.62, "probability": 0.99},
    {"word": "morning.", "start": 0.65, "end": 1.05, "probability": 0.98},
    {"word": "I", "start": 1.20, "end": 1.32, "probability": 0.99},
    {"word": "am", "start": 1.34, "end": 1.48, "probability": 0.99},
    {"word": "excited", "start": 1.50, "end": 1.95, "probability": 0.98},
    {"word": "to", "start": 1.98, "end": 2.08, "probability": 0.99},
    {"word": "share", "start": 2.10, "end": 2.45, "probability": 0.97},
    {"word": "our", "start": 2.48, "end": 2.68, "probability": 0.98},
    {"word": "vision", "start": 2.70, "end": 3.12, "probability": 0.99},
    {"word": "for", "start": 3.15, "end": 3.28, "probability": 0.99},
    {"word": "scalable", "start": 3.30, "end": 3.82, "probability": 0.96},
    {"word": "artificial", "start": 3.85, "end": 4.38, "probability": 0.97},
    {"word": "intelligence", "start": 4.40, "end": 5.15, "probability": 0.98},
    {"word": "architectures.", "start": 5.18, "end": 6.05, "probability": 0.96},
    {"word": "Over", "start": 6.60, "end": 6.88, "probability": 0.99},
    {"word": "the", "start": 6.90, "end": 7.02, "probability": 0.99},
    {"word": "past", "start": 7.05, "end": 7.35, "probability": 0.98},
    {"word": "three", "start": 7.38, "end": 7.68, "probability": 0.98},
    {"word": "months,", "start": 7.70, "end": 8.18, "probability": 0.97},
    {"word": "our", "start": 8.50, "end": 8.70, "probability": 0.99},
    {"word": "engineering", "start": 8.72, "end": 9.38, "probability": 0.98},
    {"word": "team", "start": 9.40, "end": 9.68, "probability": 0.99},
    {"word": "has", "start": 9.70, "end": 9.85, "probability": 0.99},
    {"word": "reduced", "start": 9.88, "end": 10.35, "probability": 0.97},
    {"word": "inference", "start": 10.38, "end": 10.92, "probability": 0.98},
    {"word": "latency", "start": 10.95, "end": 11.45, "probability": 0.96},
    {"word": "by", "start": 11.48, "end": 11.62, "probability": 0.99},
    {"word": "forty", "start": 11.65, "end": 12.02, "probability": 0.98},
    {"word": "percent.", "start": 12.05, "end": 12.55, "probability": 0.99},
]

DEMO_WORDS_FLAWED = [
    {"word": "Um,", "start": 0.40, "end": 0.95, "probability": 0.92},
    {"word": "good", "start": 1.05, "end": 1.30, "probability": 0.96},
    {"word": "morning", "start": 1.32, "end": 1.70, "probability": 0.95},
    {"word": "everyone,", "start": 1.72, "end": 2.15, "probability": 0.91},
    {"word": "like", "start": 2.25, "end": 2.58, "probability": 0.94},
    {"word": "basically", "start": 2.60, "end": 3.18, "probability": 0.92},
    {"word": "I", "start": 5.40, "end": 5.55, "probability": 0.98},
    {"word": "wanted", "start": 5.58, "end": 5.92, "probability": 0.97},
    {"word": "to", "start": 5.95, "end": 6.05, "probability": 0.99},
    {"word": "talk", "start": 6.08, "end": 6.35, "probability": 0.98},
    {"word": "about", "start": 6.38, "end": 6.68, "probability": 0.98},
    {"word": "our", "start": 6.70, "end": 6.85, "probability": 0.98},
    {"word": "project.", "start": 6.88, "end": 7.35, "probability": 0.96},
    {"word": "And", "start": 7.50, "end": 7.68, "probability": 0.98},
    {"word": "uh,", "start": 7.70, "end": 8.15, "probability": 0.91},
    {"word": "we", "start": 8.30, "end": 8.48, "probability": 0.98},
    {"word": "we", "start": 8.50, "end": 8.68, "probability": 0.97},
    {"word": "built", "start": 8.70, "end": 9.02, "probability": 0.96},
    {"word": "some", "start": 9.05, "end": 9.25, "probability": 0.98},
    {"word": "stuff", "start": 9.28, "end": 9.60, "probability": 0.95},
    {"word": "that", "start": 11.80, "end": 12.02, "probability": 0.98},
    {"word": "works", "start": 12.05, "end": 12.40, "probability": 0.97},
    {"word": "well.", "start": 12.42, "end": 12.80, "probability": 0.98},
]


def seed_database():
    """Initializes tables and seeds users and sessions."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Create or retrieve Default User
        user = db.query(User).filter(User.id == "default_user").first()
        if not user:
            user = User(
                id="default_user",
                name="Alex Rivera",
                email="alex.rivera@example.com",
                created_at=datetime.now(timezone.utc) - timedelta(days=20)
            )
            db.add(user)
            db.commit()

        # Clear existing sessions for a clean deterministic state
        db.query(FlawEvent).delete()
        db.query(DimensionScore).delete()
        db.query(SessionModel).delete()
        db.commit()

        now = datetime.now(timezone.utc)

        # Session 1: Baseline struggle (14 days ago)
        s1 = SessionModel(
            id="demo-session-day1",
            user_id="default_user",
            filename="practice_day01_impromptu.wav",
            audio_path="storage/audio/demo_day01.wav",
            language="en",
            duration=42.5,
            wpm=108.0,
            pause_count=6,
            filler_count=9,
            overall_score=54.2,
            band="Needs work",
            transcript_text="Um, hello team, so basically like I wanted to give an update on the progress, but uh, we we faced some issues...",
            transcript_words=DEMO_WORDS_FLAWED,
            strengths=["pronunciation", "clarity"],
            weaknesses=["pauses", "fillers", "fluency"],
            feedback_tips=[
                {
                    "dimension": "pauses",
                    "title": "Master Strategic Micro-Pauses",
                    "observation": "6 dead silences (> 1.5s) fragmented your message flow.",
                    "how_to_improve": "Breathe gently at sentence breaks instead of pausing in the middle of phrases.",
                    "priority": "high"
                },
                {
                    "dimension": "fillers",
                    "title": "Eliminate Verbal Crutches",
                    "observation": "High density of 'um', 'like', and 'basically' weakened message clarity.",
                    "how_to_improve": "Practice silent pauses in place of filler vocalizations.",
                    "priority": "high"
                }
            ],
            raw_metrics={"clarity": 0.82, "fluency": 0.58, "pace": 0.62, "pauses": 0.22, "fillers": 12.7, "pronunciation": 0.85, "confidence": 0.55, "vocabulary": 0.58},
            created_at=now - timedelta(days=14)
        )
        db.add(s1)

        # Session 2: Early improvement (10 days ago)
        s2 = SessionModel(
            id="demo-session-day4",
            user_id="default_user",
            filename="interview_prep_take1.wav",
            audio_path="storage/audio/demo_day04.wav",
            language="en",
            duration=38.0,
            wpm=122.0,
            pause_count=4,
            filler_count=6,
            overall_score=64.8,
            band="Needs work",
            transcript_text="Good afternoon. In my previous role I managed backend development and uh, microservices pipelines...",
            transcript_words=DEMO_WORDS_FLAWED,
            strengths=["clarity", "vocabulary"],
            weaknesses=["fillers", "pauses"],
            feedback_tips=[
                {
                    "dimension": "fillers",
                    "title": "Reduce 'Uh' Hesitations",
                    "observation": "Filler rate reduced by 30%, but still present during topic shifts.",
                    "how_to_improve": "Anchor your thoughts before speaking each bullet point.",
                    "priority": "high"
                }
            ],
            raw_metrics={"clarity": 0.87, "fluency": 0.68, "pace": 0.74, "pauses": 0.16, "fillers": 9.4, "pronunciation": 0.89, "confidence": 0.64, "vocabulary": 0.66},
            created_at=now - timedelta(days=10)
        )
        db.add(s2)

        # Session 3: Crossing into Good (7 days ago)
        s3 = SessionModel(
            id="demo-session-day7",
            user_id="default_user",
            filename="system_architecture_pitch.wav",
            audio_path="storage/audio/demo_day07.wav",
            language="en",
            duration=45.2,
            wpm=134.0,
            pause_count=2,
            filler_count=3,
            overall_score=75.4,
            band="Good",
            transcript_text="Our platform leverages event-driven architecture to guarantee sub-millisecond response times across the cluster...",
            transcript_words=DEMO_WORDS_EXCELLENT,
            strengths=["pace", "clarity", "vocabulary"],
            weaknesses=["confidence"],
            feedback_tips=[
                {
                    "dimension": "confidence",
                    "title": "Elevate Vocal Pitch Modulation",
                    "observation": "Good steady pace; pitch variety could be broader to project excitement.",
                    "how_to_improve": "Emphasize key verbs and metrics with deliberate pitch inflections.",
                    "priority": "medium"
                }
            ],
            raw_metrics={"clarity": 0.91, "fluency": 0.81, "pace": 0.88, "pauses": 0.08, "fillers": 3.9, "pronunciation": 0.93, "confidence": 0.74, "vocabulary": 0.72},
            created_at=now - timedelta(days=7)
        )
        db.add(s3)

        # Session 4: Refined Delivery (3 days ago)
        s4 = SessionModel(
            id="demo-session-day11",
            user_id="default_user",
            filename="executive_summary_v2.wav",
            audio_path="storage/audio/demo_day11.wav",
            language="en",
            duration=36.0,
            wpm=141.0,
            pause_count=1,
            filler_count=2,
            overall_score=82.6,
            band="Good",
            transcript_text="I am pleased to present the Q3 engineering accomplishments. All deliverables met our reliability targets...",
            transcript_words=DEMO_WORDS_EXCELLENT,
            strengths=["pace", "pauses", "pronunciation", "clarity"],
            weaknesses=["fillers"],
            feedback_tips=[
                {
                    "dimension": "fillers",
                    "title": "Final Push for Zero Fillers",
                    "observation": "Only 2 minor filler words remain. Exceptional cadence.",
                    "how_to_improve": "Maintain complete stillness during natural pauses.",
                    "priority": "low"
                }
            ],
            raw_metrics={"clarity": 0.94, "fluency": 0.89, "pace": 0.94, "pauses": 0.05, "fillers": 3.3, "pronunciation": 0.95, "confidence": 0.82, "vocabulary": 0.76},
            created_at=now - timedelta(days=3)
        )
        db.add(s4)

        # Session 5: Flagship Excellent Session (Demo Primary)
        s5 = SessionModel(
            id="demo-session-flagship",
            user_id="default_user",
            filename="final_presentation_showcase.wav",
            audio_path="storage/audio/demo_flagship.wav",
            language="en",
            duration=35.4,
            wpm=144.0,
            pause_count=0,
            filler_count=0,
            overall_score=89.5,
            band="Excellent",
            transcript_text="Good morning. I am excited to share our vision for scalable artificial intelligence architectures. Over the past three months, our engineering team has reduced inference latency by forty percent.",
            transcript_words=DEMO_WORDS_EXCELLENT,
            strengths=["clarity", "fluency", "pace", "pauses", "fillers"],
            weaknesses=["vocabulary"],
            feedback_tips=[
                {
                    "dimension": "confidence",
                    "title": "Masterful Executive Presence",
                    "observation": "Strong vocal dynamics, crystal-clear projection, and outstanding rhythm.",
                    "how_to_improve": "Maintain this commanding tone when presenting to diverse executive stakeholders.",
                    "priority": "low"
                },
                {
                    "dimension": "vocabulary",
                    "title": "Rich Lexical Diversity",
                    "observation": "Precise domain-specific terminology delivered with confidence.",
                    "how_to_improve": "Continue to introduce vivid analogies to make technical depth accessible.",
                    "priority": "low"
                }
            ],
            raw_metrics={"clarity": 0.97, "fluency": 0.95, "pace": 0.96, "pauses": 0.02, "fillers": 0.0, "pronunciation": 0.98, "confidence": 0.90, "vocabulary": 0.81},
            created_at=now - timedelta(hours=2)
        )
        db.add(s5)

        # Flagship Flawed Session for judges to inspect flaw grounding
        s_flawed = SessionModel(
            id="demo-session-flawed",
            user_id="default_user",
            filename="flawed_sample_showcase.wav",
            audio_path="storage/audio/demo_flawed.wav",
            language="en",
            duration=31.2,
            wpm=98.0,
            pause_count=4,
            filler_count=5,
            overall_score=51.8,
            band="Needs work",
            transcript_text="Um, good morning everyone, like basically I wanted to talk about our project. And uh, we we built some stuff that works well.",
            transcript_words=DEMO_WORDS_FLAWED,
            strengths=["pronunciation"],
            weaknesses=["pauses", "fillers", "fluency", "confidence"],
            feedback_tips=[
                {
                    "dimension": "pauses",
                    "title": "Master Strategic Micro-Pauses",
                    "observation": "Awkward 2.2s dead silence between 'basically' and 'I' broke listener focus.",
                    "how_to_improve": "Keep transitions under 0.6 seconds; maintain eye contact and breathe calmly.",
                    "priority": "high"
                },
                {
                    "dimension": "fillers",
                    "title": "Eliminate Verbal Crutches",
                    "observation": "Multiple consecutive fillers ('like basically', 'uh') undermine speaker confidence.",
                    "how_to_improve": "Replace 'like basically' with a silent pause.",
                    "priority": "high"
                }
            ],
            raw_metrics={"clarity": 0.74, "fluency": 0.52, "pace": 0.55, "pauses": 0.28, "fillers": 9.6, "pronunciation": 0.78, "confidence": 0.48, "vocabulary": 0.54},
            created_at=now - timedelta(hours=4)
        )
        db.add(s_flawed)

        db.commit()

        # Seed Dimension Scores for flagship session
        dimensions_data_flagship = [
            ("clarity", 94.0, 0.97, 15.0),
            ("fluency", 92.0, 0.95, 15.0),
            ("pace", 95.0, 0.96, 15.0),
            ("pauses", 96.0, 0.02, 15.0),
            ("fillers", 100.0, 0.0, 15.0),
            ("pronunciation", 91.0, 0.98, 10.0),
            ("confidence", 87.0, 0.90, 10.0),
            ("vocabulary", 78.0, 0.81, 5.0),
        ]
        for dim, sc, raw, wt in dimensions_data_flagship:
            ds = DimensionScore(session_id="demo-session-flagship", dimension=dim, score=sc, raw_value=raw, weight=wt)
            db.add(ds)

        # Seed Flaw Events for flawed session to showcase WaveSurfer grounding
        flaws_data = [
            ("filler", 0.40, 0.95, "medium", "Filler word 'Um' used at the opening.", "Start speaking directly with your greeting."),
            ("filler", 2.25, 3.18, "high", "Clustered verbal crutches 'like basically'.", "Pause silently instead of stringing filler phrases."),
            ("long_pause", 3.20, 5.40, "high", "2.2 s hesitation gap between 'basically' and 'I'.", "Transition smoothly into your main idea."),
            ("filler", 7.70, 8.15, "medium", "Filler sound 'uh' verbalized.", "Breathe silently through your nose."),
            ("repetition", 8.30, 8.68, "medium", "Stumbled repetition 'we we'.", "Commit to the phrase without double-starting."),
            ("long_pause", 9.65, 11.75, "high", "2.1 s dead pause between 'stuff' and 'that'.", "Keep thought flow steady with connective words."),
        ]
        for ftype, st, en, sev, ev, tp in flaws_data:
            fe = FlawEvent(
                session_id="demo-session-flawed",
                flaw_type=ftype,
                start_time=st,
                end_time=en,
                severity=sev,
                evidence=ev,
                tip=tp
            )
            db.add(fe)

        # Also add Dimension Scores for flawed session
        dimensions_data_flawed = [
            ("clarity", 62.0, 0.74, 15.0),
            ("fluency", 48.0, 0.52, 15.0),
            ("pace", 52.0, 0.55, 15.0),
            ("pauses", 44.0, 0.28, 15.0),
            ("fillers", 41.0, 9.6, 15.0),
            ("pronunciation", 70.0, 0.78, 10.0),
            ("confidence", 50.0, 0.48, 10.0),
            ("vocabulary", 60.0, 0.54, 5.0),
        ]
        for dim, sc, raw, wt in dimensions_data_flawed:
            ds = DimensionScore(session_id="demo-session-flawed", dimension=dim, score=sc, raw_value=raw, weight=wt)
            db.add(ds)

        db.commit()
        print("Successfully seeded demo database with 6 progression sessions, dimensions, and flaw events!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
