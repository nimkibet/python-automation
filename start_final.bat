@echo off
title Idle Shorts - Final Modular Version
echo Cleaning up any old background instances...
taskkill /F /IM python.exe /T >nul 2>&1
echo Deleting any hanging cache or log files...
del idle_automation.log >nul 2>&1

echo.
echo Starting Final Bot Architecture...
echo (Closing this black window will immediately stop the script completely)
echo.

cd /d "%~dp0final_bot"
python main_shorts.py

pause
