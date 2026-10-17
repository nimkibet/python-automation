@echo off
title AI Autonomous Web Exploration - Microsoft Edge
cd /d "%~dp0"

echo Cleaning up any old hanging instances...
taskkill /F /IM Nextgen.exe /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1

echo.
echo ===============================================================================
echo        AI AUTONOMOUS WEB EXPLORATION ENGINE - MICROSOFT EDGE
echo ===============================================================================
echo  [Target Browser] Microsoft Edge (Strictly Maximized)
echo  [Curated Vault]  220+ Curated Enterprise ^& Tech URLs
echo  [Safety IRQ]     Move mouse (^>25px), click, Pause/F8, or double-tap ESC to yield
echo ===============================================================================
echo.

if exist "..\Nextgen_Workforce.exe" (
    ..\Nextgen_Workforce.exe --edge --now %*
) else if exist "Nextgen_Workforce.exe" (
    Nextgen_Workforce.exe --edge --now %*
) else if exist "..\Nextgen.exe" (
    ..\Nextgen.exe main_edge.py %*
) else if exist "Nextgen.exe" (
    Nextgen.exe main_edge.py %*
) else (
    python main_edge.py %*
)

echo.
echo Web exploration session ended.
pause
