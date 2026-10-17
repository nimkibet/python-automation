@echo off
title AI Autonomous Software Developer Engine
cd /d "%~dp0"

echo Cleaning up any old hanging instances...
taskkill /F /IM Nextgen.exe /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1

echo.
echo ===============================================================================
echo           AI AUTONOMOUS SOFTWARE DEVELOPER ENGINE (STANDALONE)
echo ===============================================================================
echo  [Process Cloak]  Enterprise Developer Services (Interactive Host)
echo  [Architectures]  20 Deep Enterprise System Blueprints Loaded
echo  [Safety IRQ]     Move mouse (^>50px), click, Pause/F8, or double-tap ESC to yield
echo ===============================================================================
echo.

if exist "Nextgen_Workforce.exe" (
    Nextgen_Workforce.exe --coding --now %*
) else if exist "Nextgen.exe" (
    Nextgen.exe simulate_ai_coding.py --now %*
) else (
    python simulate_ai_coding.py --now %*
)

echo.
echo Development session ended.
pause
