@echo off
echo Starting Listing Genie...

:: Start backend in new window
start "Backend" cmd /k "cd /d %~dp0 && venv\Scripts\activate && uvicorn app.main:app --reload"

:: Wait a moment for backend to start
timeout /t 2 /nobreak > nul

:: Start frontend in new window
start "Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Both servers starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Close this window anytime - servers will keep running in their own windows.
