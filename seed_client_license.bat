@echo off
title Nextgen Autonomous Workforce - Client License Seeder
color 0A
cd /d "%~dp0"

if exist "%~dp0seed_license.ps1" (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0seed_license.ps1" %*
) else (
    echo [ERROR] seed_license.ps1 not found in current directory!
    echo Please ensure seed_license.ps1 is in the same folder as this script.
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Seeder exited with error code %ERRORLEVEL%.
)

echo.
pause