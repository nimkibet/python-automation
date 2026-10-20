@echo off
title Nextgen Workforce - Reading Mode Scroll Jiggler
cd /d "%~dp0"
echo ===============================================================================
echo       NEXTGEN AUTONOMOUS WORKFORCE - READING MODE SCROLL JIGGLER
echo ===============================================================================
echo  Provider : Interception Ring-0 Kernel Filter Driver
echo  Trigger  : 2 Minutes (120s) of unbroken human inactivity
echo  Action   : Subtle micro-scroll down and exact restoration up (0px cursor drift)
echo  Safety   : Physical mouse movement or keyboard input yields immediately
echo ===============================================================================
echo.
python run_reading_mode.py %*
pause
