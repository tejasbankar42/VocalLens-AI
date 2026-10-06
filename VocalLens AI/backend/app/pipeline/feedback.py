"""
VocalLens AI - Actionable Feedback Engine
Generates deterministic, rubric-based feedback cards ('what to improve' and 'how')
with optional Gemini API enhancement fallback.
"""

from typing import List, Dict, Any, Optional
import httpx
from backend.app.config import GEMINI_API_KEY


# Comprehensive Rule-Based Templates for all 8 speech dimensions
RULE_BASED_TEMPLATES = {
    "pauses": {
        "weak": {
            "title": "Master Strategic Micro-Pauses",
            "observation": "Frequent long silences (> 1.2s) interrupt your cadence and weaken listener retention.",
            "how_to_improve": "Replace abrupt dead silences with controlled 0.5s breaths at natural punctuation points. Outline your thoughts with transition signposts (e.g., 'First', 'Additionally', 'In conclusion') so you know where you're heading next.",
            "priority": "high"
        },
        "good": {
            "title": "Maintain Crisp Transitions",
            "observation": "Your pause frequency is reasonable, with occasional hesitations before complex words.",
            "how_to_improve": "Practice pausing intentionally for 1 full second right after delivering a key statistic or core insight to let it sink in.",
            "priority": "medium"
        }
    },
    "fillers": {
        "weak": {
            "title": "Eliminate Verbal Crutches",
            "observation": "Fillers such as 'um', 'uh', 'like', and 'basically' dilute your message authority.",
            "how_to_improve": "Use the 'Pause-and-Breathe' drill: whenever you feel the impulse to say 'um' or 'like', close your lips and take a silent nose inhale before resuming.",
            "priority": "high"
        },
        "good": {
            "title": "Refine Filler Discipline",
            "observation": "Minimal filler usage, keeping your speech relatively crisp and professional.",
            "how_to_improve": "Record yourself speaking on an unfamiliar topic for 60 seconds without a single filler word to achieve complete mastery.",
            "priority": "low"
        }
    },
    "pace": {
        "weak": {
            "title": "Stabilize Your Delivery Cadence",
            "observation": "Your speaking speed fluctuates outside the optimal 130–155 WPM conversational target.",
            "how_to_improve": "Tap your finger at 140 BPM to anchor a rhythmic cadence. Avoid accelerating when excited; emphasize key words by slowing down rather than speeding up.",
            "priority": "high"
        },
        "good": {
            "title": "Pacing Variety for Impact",
            "observation": "Good overall speed that is comfortable for listeners to follow.",
            "how_to_improve": "Experiment with dynamic pacing: slow down to 110 WPM on critical takeaways and return to 140 WPM for narrative explanations.",
            "priority": "low"
        }
    },
    "clarity": {
        "weak": {
            "title": "Crisp Articulation & Projection",
            "observation": "Acoustic and transcription confidence dipped on sentence endings and fast transitions.",
            "how_to_improve": "Practice the 'Cork Exercise': hold a wine cork or pen between your front teeth and read a paragraph aloud for 2 minutes, then speak naturally. Your enunciation will instantly sharpen.",
            "priority": "high"
        },
        "good": {
            "title": "Crystal Clear Voice Enunciation",
            "observation": "High clarity across syllables with virtually no dropped consonants.",
            "how_to_improve": "Ensure your mic distance remains consistent (approx 15 cm) to preserve clean vocal timbre in varied room acoustics.",
            "priority": "low"
        }
    },
    "fluency": {
        "weak": {
            "title": "Smooth Flow & Eliminate Restarts",
            "observation": "Immediate word repetitions and sentence restarts create a halting listening experience.",
            "how_to_improve": "When you stumble on a phrase, commit forward rather than repeating the word. Complete the sentence before clarifying, which conveys higher poise.",
            "priority": "high"
        },
        "good": {
            "title": "Fluid Sentence Continuity",
            "observation": "Strong conversational momentum with minimal restarts.",
            "how_to_improve": "Work on complex sentence structures using subordinating conjunctions ('Although', 'Whereas') without breaking vocal rhythm.",
            "priority": "low"
        }
    },
    "pronunciation": {
        "weak": {
            "title": "Sharp Syllable Emphasis",
            "observation": "Certain word transitions had low acoustic clarity or blended syllables.",
            "how_to_improve": "Over-enunciate the terminal consonants (e.g., 't', 'd', 'k', 'p') at the ends of multi-syllable words.",
            "priority": "medium"
        },
        "good": {
            "title": "Accurate Phonetic Execution",
            "observation": "Accurate pronunciation across both technical and everyday vocabulary.",
            "how_to_improve": "Broaden your repertoire with domain-specific terminology relevant to your interview or presentation field.",
            "priority": "low"
        }
    },
    "confidence": {
        "weak": {
            "title": "Vocal Variety & Assertive Phrasing",
            "observation": "A flatter pitch contour or hedging phrases ('I guess', 'maybe') reduce perceived confidence.",
            "how_to_improve": "Use downward inflection on final statements rather than upward questioning pitch ('uptalk'). Cut hedge phrases in favor of direct assertions: change 'I think maybe we should' to 'Our best approach is'.",
            "priority": "high"
        },
        "good": {
            "title": "Commanding Vocal Presence",
            "observation": "Energetic pitch modulation and steady vocal support throughout your speech.",
            "how_to_improve": "Practice projecting from the diaphragm to sustain full tonal resonance during longer speeches.",
            "priority": "low"
        }
    },
    "vocabulary": {
        "weak": {
            "title": "Expand Lexical Variety",
            "observation": "Repetition of common words lowers your lexical variety score.",
            "how_to_improve": "Swap repeated basic adjectives ('good', 'big', 'hard') for vivid descriptors ('robust', 'substantial', 'formidable'). Keep an active word journal.",
            "priority": "medium"
        },
        "good": {
            "title": "Rich Vocabulary Repertoire",
            "observation": "Commendable diversity of words with strong precision and length.",
            "how_to_improve": "Tailor vocabulary density to your audience: blend sophisticated concepts with simple analogies for maximum persuasive power.",
            "priority": "low"
        }
    }
}


def generate_feedback_tips(
    dimension_scores: Dict[str, float],
    flaw_events: List[Dict[str, Any]],
    strengths: List[str],
    weaknesses: List[str]
) -> List[Dict[str, str]]:
    """
    Generates tailored feedback cards combining rule-based pedagogical templates
    and observed temporal flaws.
    """
    tips: List[Dict[str, str]] = []

    # Prioritize weaknesses first, then remaining dimensions
    ordered_dims = list(weaknesses) + [d for d in dimension_scores if d not in weaknesses]

    for dim in ordered_dims:
        score = dimension_scores.get(dim, 70.0)
        dim_templates = RULE_BASED_TEMPLATES.get(dim)
        if not dim_templates:
            continue

        template = dim_templates["weak"] if score < 75.0 else dim_templates["good"]
        
        # Check if there are specific flaw events for this dimension
        relevant_flaws = [f for f in flaw_events if f.get("type") in [dim, f"long_{dim}"] or (dim == "fillers" and f.get("type") == "filler")]
        
        observation = template["observation"]
        if relevant_flaws and score < 75.0:
            top_flaw = relevant_flaws[0]
            observation += f" (For example at {top_flaw['start']}s: {top_flaw['evidence']})"

        tips.append({
            "dimension": dim,
            "title": template["title"],
            "observation": observation,
            "how_to_improve": template["how_to_improve"],
            "priority": template["priority"]
        })

    # Return top 4-5 most impactful cards
    return tips[:5]


def polish_feedback_with_gemini(
    tips: List[Dict[str, str]], 
    overall_score: float, 
    band: str
) -> List[Dict[str, str]]:
    """
    Optional Gemini API enhancement (temperature 0).
    If key is not provided or network is unreachable, gracefully returns templates.
    """
    if not GEMINI_API_KEY:
        return tips

    prompt = f"""You are a master speech coach. Polish the following feedback tips for a speaker with score {overall_score}/100 ({band}).
Keep them ultra-actionable, empathetic, and concise. Maintain the exact same JSON format with keys: dimension, title, observation, how_to_improve, priority.

Input Tips:
{tips}
"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.0, "responseMimeType": "application/json"}
        }
        with httpx.Client(timeout=4.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                import json
                result = resp.json()
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                polished = json.loads(text)
                if isinstance(polished, list) and len(polished) > 0:
                    return polished
    except Exception:
        # Fallback seamlessly to offline templates
        pass

    return tips
