@echo off
echo ===================================================
echo           VocalLens AI - Starting Platform
echo           Speak. Measure. Improve.
echo ===================================================

echo.
echo [1/3] Checking Python dependencies and database...
python -m backend.scripts.seed_demo

echo.
echo [2/3] Starting Backend Server on http://127.0.0.1:8000 ...
start "VocalLens AI Backend" cmd /k "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

echo.
echo [3/3] Starting Frontend Dev Server on http://localhost:5173 ...
cd frontend
start "VocalLens AI Frontend" cmd /k "npm run dev"

echo.
echo ===================================================
echo VocalLens AI is now running!
echo Access the Web Application at: http://localhost:5173
echo Backend API Docs at:           http://127.0.0.1:8000/docs
echo ===================================================
pause
