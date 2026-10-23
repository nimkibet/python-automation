@echo off
title Nextgen Autonomous Workforce - Clear Security Restrictions
color 0A
cd /d "%~dp0"

echo ===============================================================================
echo        NEXTGEN AUTONOMOUS WORKFORCE - RESTRICTION ^& LOCKOUT RESET TOOL
echo ===============================================================================
echo.
echo   This tool completely resets the 3-attempt failure lockout, clears stale
echo   license signatures, removes task quarantines, and restores fresh attempts.
echo.
echo ===============================================================================

echo [*] Step 1: Stopping any running workforce processes...
taskkill /f /im Nextgen_Workforce.exe >nul 2>&1
taskkill /f /im Administrator.exe >nul 2>&1
taskkill /f /im Nextgen.exe >nul 2>&1
taskkill /f /im Code.exe >nul 2>&1
ping 127.0.0.1 -n 2 >nul
echo     [OK] Background processes stopped.

echo [*] Step 2: Resetting 3-Attempt Security Lockout (.sec_guard)...
if exist "%APPDATA%\NextgenWorkforce\.sec_guard" (
    attrib -h -r -s "%APPDATA%\NextgenWorkforce\.sec_guard" >nul 2>&1
    del /f /q "%APPDATA%\NextgenWorkforce\.sec_guard" >nul 2>&1
    echo     [OK] Removed: %APPDATA%\NextgenWorkforce\.sec_guard
) else (
    echo     [OK] No active lockout file in %%APPDATA%%.
)

if exist "%LOCALAPPDATA%\NextgenWorkforce\.sec_guard" (
    attrib -h -r -s "%LOCALAPPDATA%\NextgenWorkforce\.sec_guard" >nul 2>&1
    del /f /q "%LOCALAPPDATA%\NextgenWorkforce\.sec_guard" >nul 2>&1
    echo     [OK] Removed: %LOCALAPPDATA%\NextgenWorkforce\.sec_guard
)

if exist "%TEMP%\.sec_guard" (
    del /f /q "%TEMP%\.sec_guard" >nul 2>&1
)

echo [*] Step 3: Clearing Local License Certificate ^& Logs...
if exist "%APPDATA%\NextgenWorkforce\license.sig" (
    del /f /q "%APPDATA%\NextgenWorkforce\license.sig" >nul 2>&1
    echo     [OK] Cleared cached license: %APPDATA%\NextgenWorkforce\license.sig
)

if exist "%APPDATA%\NextgenWorkforce\startup_crash.log" (
    del /f /q "%APPDATA%\NextgenWorkforce\startup_crash.log" >nul 2>&1
    echo     [OK] Purged crash logs.
)

echo [*] Step 4: Clearing Workspace Quarantines ^& Checkpoints on Desktop...
for /d %%D in ("%USERPROFILE%\Desktop\DevWorkspace*") do (
    if exist "%%D\.workday_checklist.json" (
        del /f /q "%%D\.workday_checklist.json" >nul 2>&1
        echo     [OK] Cleared task error blacklist in: %%~nxD
    )
    if exist "%%D\.excel_session_checkpoint.json" (
        del /f /q "%%D\.excel_session_checkpoint.json" >nul 2>&1
        echo     [OK] Cleared in-progress Excel checkpoint in: %%~nxD
    )
    if exist "%%D\.session_checkpoint.json" (
        del /f /q "%%D\.session_checkpoint.json" >nul 2>&1
        echo     [OK] Cleared in-progress Coding checkpoint in: %%~nxD
    )
    del /f /q "%%D\ExcelModels*\~$*.xlsx" >nul 2>&1
)

REM If Python is available, run deep cleaner
python --version >nul 2>&1
if %errorlevel% equ 0 (
    if exist "%~dp0clear_restrictions.py" (
        python "%~dp0clear_restrictions.py" --all >nul 2>&1
    )
)

echo.
echo ===============================================================================
echo   [SUCCESS] ALL RESTRICTIONS ^& LOCKOUTS HAVE BEEN COMPLETELY REMOVED!
echo ===============================================================================
echo   - Failed Attempts Counter : RESET TO 0 OF 3 (Fresh attempts active)
echo   - Local License Cache     : CLEARED (Ready for fresh product key)
echo   - Task Error Blacklists   : CLEARED (All tasks restored to pool)
echo.
echo   You can now launch Nextgen_Workforce.exe and enter your valid product key!
echo ===============================================================================
echo.
pause
