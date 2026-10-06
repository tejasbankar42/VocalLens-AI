#!/usr/bin/env bash
set -e

echo "==================================================="
echo "          VocalLens AI - Starting Platform"
echo "          Speak. Measure. Improve."
echo "==================================================="

echo ""
echo "[1/3] Initializing demo data..."
python3 -m backend.scripts.seed_demo

echo ""
echo "[2/3] Starting Backend Server on http://127.0.0.1:8000 ..."
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

echo ""
echo "[3/3] Starting Frontend Dev Server on http://localhost:5173 ..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "==================================================="
echo "VocalLens AI is now running!"
echo "Access the Web Application at: http://localhost:5173"
echo "Backend API Docs at:           http://127.0.0.1:8000/docs"
echo "Press Ctrl+C to terminate both servers."
echo "==================================================="

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
