@echo off
title Nextgen Autonomous Workforce - Interception Ring-0 Driver Setup
cd /d "%~dp0"

echo ===============================================================================
echo      NEXTGEN AUTONOMOUS WORKFORCE - RING-0 DRIVER AUTO-INSTALLER
echo ===============================================================================
echo This utility installs the Interception Ring-0 Kernel Filter Driver on your PC.
echo.
echo Requirements:
echo   1. Windows Administrator privileges (UAC prompt will appear)
echo   2. One system reboot after installation
echo ===============================================================================
echo.

REM Try bundled installer first, then Nextgen_Workforce.exe --install-driver
if exist "%~dp0installer\install-interception.exe" (
    echo [*] Running bundled driver installer with Administrator elevation...
    powershell -Command "Start-Process '%~dp0installer\install-interception.exe' -ArgumentList '/install' -Verb RunAs -Wait"
    goto :check_result
)

if exist "%~dp0Nextgen_Workforce.exe" (
    echo [*] Running driver installation via Nextgen_Workforce runtime...
    powershell -Command "Start-Process '%~dp0Nextgen_Workforce.exe' -ArgumentList '--install-driver' -Verb RunAs -Wait"
    goto :check_result
)

if exist "%~dp0Interception\Interception\command line installer\install-interception.exe" (
    echo [*] Running repository driver installer with Administrator elevation...
    powershell -Command "Start-Process '%~dp0Interception\Interception\command line installer\install-interception.exe' -ArgumentList '/install' -Verb RunAs -Wait"
    goto :check_result
)

echo [ERROR] No Interception driver installer found!
pause
exit /b 1

:check_result
echo.
echo ===============================================================================
echo [SUCCESS] Interception Ring-0 Driver setup dispatched.
echo.
echo IMPORTANT: You MUST restart your PC for the kernel filter to take effect.
echo After rebooting, run Nextgen_Workforce.exe or start_workday.bat.
echo ===============================================================================
echo.
set /p REBOOT="Would you like to restart your PC right now? [Y/N] (Default: N): "
if /i "%REBOOT%"=="Y" (
    shutdown /r /t 5 /c "Nextgen Workforce: Restarting to activate Ring-0 Filter Driver"
)
exit /b 0
