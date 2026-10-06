"""
VocalLens AI - API Schema and Endpoint Integration Tests
Validates status codes, contract payloads, and report serialization.
"""

from pathlib import Path


def test_health_check_endpoint(api_client):
    """GET /api/health must return healthy status and whisper info."""
    response = api_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "whisper_model" in data
    assert data["database"] == "connected"


def test_baseline_endpoint(api_client):
    """GET /api/baseline must return ideal and flawed metric stats."""
    response = api_client.get("/api/baseline")
    assert response.status_code == 200
    data = response.json()
    assert "ideal" in data
    assert "flawed" in data
    assert "clarity" in data["ideal"]
    assert "fillers" in data["flawed"]
    assert "weights" in data


def test_sessions_list_endpoint(api_client):
    """GET /api/sessions returns a list of sessions."""
    response = api_client.get("/api/sessions")
    assert response.status_code == 200
    sessions = response.json()
    assert isinstance(sessions, list)
    assert len(sessions) > 0
    item = sessions[0]
    for key in ["id", "filename", "overall_score", "band", "wpm", "created_at"]:
        assert key in item


def test_session_detail_schema(api_client):
    """GET /api/sessions/{id} returns the comprehensive report schema."""
    response = api_client.get("/api/sessions/demo-session-flagship")
    assert response.status_code == 200
    data = response.json()
    
    # Validate required ReportResponse fields
    required_keys = [
        "session_id", "filename", "duration", "language", "overall_score", "band",
        "dimension_scores", "dimension_details", "strengths", "weaknesses",
        "wpm", "pause_count", "filler_count", "flaw_events", "transcript_text",
        "transcript_words", "feedback_tips", "raw_metrics", "created_at"
    ]
    for k in required_keys:
        assert k in data, f"Missing key in ReportResponse: {k}"

    assert len(data["dimension_details"]) == 8
    assert isinstance(data["flaw_events"], list)
    assert isinstance(data["transcript_words"], list)
    assert isinstance(data["feedback_tips"], list)


def test_progress_endpoint_schema(api_client):
    """GET /api/progress returns overall stats and historical trajectories."""
    response = api_client.get("/api/progress")
    assert response.status_code == 200
    data = response.json()

    for k in ["total_sessions", "average_score", "highest_score", "most_improved_dimension", "score_history", "dimension_trends"]:
        assert k in data
    assert data["total_sessions"] >= 1
    assert isinstance(data["score_history"], list)


def test_analyze_endpoint_upload(api_client, sample_ideal_wav):
    """POST /api/analyze accepts audio file and returns complete report."""
    with open(sample_ideal_wav, "rb") as f:
        response = api_client.post(
            "/api/analyze",
            files={"file": ("test_interview.wav", f, "audio/wav")},
            data={"language": "en"}
        )

    assert response.status_code == 200, f"Analyze failed: {response.text}"
    report = response.json()
    assert report["overall_score"] > 0
    assert report["band"] in ["Excellent", "Good", "Needs work", "Weak"]
    assert len(report["dimension_scores"]) == 8
    assert len(report["transcript_words"]) > 0
