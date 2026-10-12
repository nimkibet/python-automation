@echo off
title 3:00 AM Night Scheduler - Loggy3 + Final Bot
echo =======================================================
echo   3:00 AM Night Scheduler & Auto-Launcher
echo =======================================================
echo.
echo Checking permissions and starting Python scheduler...
cd /d "%~dp0"
python night_wake_and_launch.py
pause
