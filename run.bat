@echo off
title AI Complaint Management System Bootstrapper
echo ===================================================
echo   AI-Powered Customer Complaint Management System
echo ===================================================
echo.
echo [1/2] Launching Python FastAPI Backend...
start "FastAPI Backend" cmd /k "cd backend && python run.py"

echo [2/2] Launching Vite React Frontend...
start "Vite React Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ===================================================
echo   System running!
echo   Backend:  http://localhost:8000/docs
echo   Frontend: http://localhost:5173/
echo ===================================================
echo Press any key to exit this bootstrapper (services will remain running).
pause > nul
