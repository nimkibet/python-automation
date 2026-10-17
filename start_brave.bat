@echo off
title AI Autonomous Web Exploration - Brave Browser
cd /d "%~dp0"

echo Cleaning up any old hanging instances...
taskkill /F /IM Nextgen.exe /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1

echo.
echo ===============================================================================
echo        AI AUTONOMOUS WEB EXPLORATION ENGINE - BRAVE BROWSER
echo ===============================================================================
echo  [Target Browser] Brave Browser (Strictly Maximized)
echo  [Curated Vault]  220+ Curated Enterprise ^& Tech URLs
echo  [Safety IRQ]     Move mouse (^>25px), click, Pause/F8, or double-tap ESC to yield
echo ===============================================================================
echo.

if exist "..\Nextgen_Workforce.exe" (
    ..\Nextgen_Workforce.exe --brave --now %*
) else if exist "Nextgen_Workforce.exe" (
    Nextgen_Workforce.exe --brave --now %*
) else if exist "..\Nextgen.exe" (
    ..\Nextgen.exe main_brave.py %*
) else if exist "Nextgen.exe" (
    Nextgen.exe main_brave.py %*
) else (
    python main_brave.py %*
)

echo.
echo Web exploration session ended.
pause
