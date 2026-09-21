@echo off
setlocal
cd /d "%~dp0"

title CineStills AI Studio - Setup

echo.
echo ==========================================
echo   CineStills AI Studio - First-time Setup
echo ==========================================
echo.

set "PYTHON_CMD="

where py >nul 2>&1
if %errorlevel%==0 (
    py -3.12 --version >nul 2>&1
    if %errorlevel%==0 set "PYTHON_CMD=py -3.12"
)

if not defined PYTHON_CMD (
    where python >nul 2>&1
    if %errorlevel%==0 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
    echo ERROR: Python was not found on this computer.
    echo Install Python 3.12 or later, then run setup.cmd again.
    echo.
    pause
    exit /b 1
)

echo Using Python:
%PYTHON_CMD% --version
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating the CineStills environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto :failed
) else (
    echo [1/3] CineStills environment already exists.
)

echo [2/3] Installing required components...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :failed

".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :failed

echo [3/3] Starting CineStills AI Studio...
echo.
".venv\Scripts\python.exe" main.py

exit /b 0

:failed
echo.
echo Setup could not be completed.
echo Review the error above, then run setup.cmd again.
echo.
pause
exit /b 1
