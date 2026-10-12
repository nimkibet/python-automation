@echo off
title Run Idle Shorts

echo Cleaning up any old background instances...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1

echo Deleting any hanging cache or log files...
del /f /q idle_shorts.log >nul 2>&1
del /f /s /q __pycache__ >nul 2>&1
del /f /q *.pyc >nul 2>&1

echo.
echo Starting Idle Shorts Version...
echo (Closing this black window will immediately stop the script completely)
python idle_shorts.py
pause
