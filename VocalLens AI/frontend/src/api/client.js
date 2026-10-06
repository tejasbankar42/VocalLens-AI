/**
 * VocalLens AI - Frontend API Client
 * Wraps backend FastAPI routes with structured error handling.
 */

const API_BASE = ''; // Relies on Vite proxy to backend port 8000

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function fetchBaseline() {
  const res = await fetch(`${API_BASE}/api/baseline`);
  if (!res.ok) throw new Error('Failed to fetch baseline distributions');
  return res.json();
}

export async function analyzeAudio(audioBlobOrFile, language = 'en') {
  const formData = new FormData();
  formData.append('file', audioBlobOrFile, audioBlobOrFile.name || 'speech_sample.wav');
  formData.append('language', language);
  formData.append('user_id', 'default_user');

  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Analysis failed' }));
    throw new Error(errorData.detail || `Server error (${res.status})`);
  }

  return res.json();
}

export async function fetchSessions() {
  const res = await fetch(`${API_BASE}/api/sessions`);
  if (!res.ok) throw new Error('Failed to fetch sessions');
  return res.json();
}

export async function fetchSessionDetail(sessionId) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}`);
  if (!res.ok) throw new Error(`Session ${sessionId} not found`);
  return res.json();
}

export async function fetchProgress() {
  const res = await fetch(`${API_BASE}/api/progress`);
  if (!res.ok) throw new Error('Failed to fetch progress analytics');
  return res.json();
}

export async function fetchDemoSession(type = 'flagship') {
  const res = await fetch(`${API_BASE}/api/demo-session?type=${type}`);
  if (!res.ok) throw new Error('Failed to load demo session');
  return res.json();
}

export async function deleteSession(sessionId) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete session');
  return res.json();
}
