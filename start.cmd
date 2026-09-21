@echo off
setlocal
cd /d "%~dp0"

title CineStills AI Studio

if not exist ".venv\Scripts\python.exe" (
    echo CineStills has not been set up yet.
    echo Starting first-time setup...
    echo.
    call setup.cmd
    exit /b %errorlevel%
)

".venv\Scripts\python.exe" -c "import PySide6, requests, PIL, rembg" >nul 2>&1
if errorlevel 1 (
    echo CineStills components have changed.
    echo Updating the local environment...
    echo.
    call setup.cmd
    exit /b %errorlevel%
)

".venv\Scripts\python.exe" main.py

if errorlevel 1 (
    echo.
    echo CineStills closed with an error.
    pause
)
