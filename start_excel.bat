@echo off
title AI Autonomous Excel Financial Analyst Engine
cd /d "%~dp0"

echo Cleaning up any old hanging instances...
taskkill /F /IM Nextgen.exe /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1

echo.
echo ===============================================================================
echo        AI AUTONOMOUS EXCEL FINANCIAL ANALYST ENGINE (STANDALONE)
echo ===============================================================================
echo  [Process Cloak]  Enterprise Developer Services (Interactive Host)
echo  [Workbooks]      8 Deep Financial ^& Operational Models Loaded
echo  [Safety IRQ]     Move mouse (^>50px), click, Pause/F8, or double-tap ESC to yield
echo ===============================================================================
echo.

if exist "Nextgen_Workforce.exe" (
    Nextgen_Workforce.exe --excel --now %*
) else if exist "Nextgen.exe" (
    Nextgen.exe simulate_excel_automation.py --now %*
) else (
    python simulate_excel_automation.py --now %*
)

echo.
echo Financial modeling session ended.
pause
