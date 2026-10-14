@echo off
title AI Complaint Management System (Full Python Streamlit Edition)
echo =====================================================================
echo   AI-Powered Customer Complaint Management System (Full Python)
echo =====================================================================
echo.
echo Launching Streamlit Application...
echo.

py -3.10 -m streamlit run app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Trying python launcher...
    python -m streamlit run app.py
)

pause
