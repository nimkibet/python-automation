@echo off
title AI Autonomous Reading Mode (Subtle Scroll Jiggler)
cd /d "%~dp0"

echo Cleaning up any old hanging instances...
taskkill /F /IM Nextgen.exe /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1

echo.
echo ===============================================================================
echo      AI AUTONOMOUS READING MODE - SUBTLE SCROLL JIGGLER ENGINE
echo ===============================================================================
echo  [Input Driver]   Interception Ring-0 Kernel Filter (0 injected flags)
echo  [Idle Trigger]   2 Minutes (120s) of unbroken human inactivity
echo  [Action]         Subtle micro-scroll down and exact 1:1 restoration up
echo  [Safety IRQ]     Move mouse (^>20px), click, Pause/F8, or double-tap ESC to yield
echo ===============================================================================
echo.

if exist "Nextgen_Workforce.exe" (
    Nextgen_Workforce.exe --reading %*
) else if exist "Nextgen.exe" (
    Nextgen.exe launcher.py --reading %*
) else (
    python run_reading_mode.py %*
)

echo.
echo Reading Mode session ended.
pause
