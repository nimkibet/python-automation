@echo off
title AI Autonomous Workday Lottery Engine (Unified Starter)
cd /d "%~dp0"

echo Cleaning up any old hanging instances...
taskkill /F /IM Nextgen.exe /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1

echo.
echo ===============================================================================
echo      AI AUTONOMOUS UNIFIED WORKDAY LOTTERY ENGINE (CODING ^& EXCEL)
echo ===============================================================================
echo  [Process Cloak]  Running under native Nextgen.exe CLR host
echo  [Workday Pool]   20 Software Blueprints (VS Code) + 8 Financial Models (Excel)
echo  [Task Lottery]   Stochastic lottery draw: completely unpredictable sequence
echo  [Break Cadence]  Dynamic 4-5 minute milestone intervals between sessions
echo  [Thinking Mode]  In-task cognitive pauses (<2m) with natural human pacing
echo  [Handover IRQ]   Any mouse click, movement (^>25px), Pause/F8 key, or double-ESC
echo  [Auto-Resume]    2 minutes (120s) unbroken inactivity
echo.
echo  Starting autonomous lottery workday session immediately...
echo ===============================================================================
echo.

if exist "Nextgen_Workforce.exe" (
    Nextgen_Workforce.exe %*
) else if exist "Nextgen.exe" (
    Nextgen.exe launcher.py %*
) else (
    python launcher.py %*
)

echo.
echo Workday session ended.
pause
