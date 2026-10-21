@echo off
title Nextgen Autonomous Workforce - New PC Setup
cd /d "%~dp0"

echo ===============================================================================
echo        NEXTGEN AUTONOMOUS WORKFORCE ENGINE - AUTOMATED SYSTEM SETUP
echo ===============================================================================
echo This installer prepares any Windows 10/11 PC to run the Nextgen Workforce Suite.
echo.

REM 0. Check for Standalone Executable (Zero-Dependency Mode)
if exist "%~dp0Nextgen_Workforce.exe" (
    echo [FOUND] Standalone Nextgen Workforce Runtime (Single-File Binary).
    echo [INFO] Python runtime is embedded inside executable. No pip dependencies required!
    goto :setup_standalone_shortcuts
)

REM 1. Verify Python Installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not added to your system PATH.
    echo.
    echo Please follow these simple steps:
    echo   1. Download Python 3.12 (64-bit) from:
    echo      https://www.python.org/downloads/windows/
    echo   2. Run the installer and CRITICALLY check the box:
    echo      "[X] Add python.exe to PATH"
    echo   3. Once installed, re-run this setup_new_pc.bat script.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version') do echo [FOUND] Python Runtime: %%v

REM 2. Install Required Python Packages
echo.
echo [*] Installing required Python packages from requirements.txt...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some packages failed to install. Retrying direct installation...
    python -m pip install pywin32 pynput requests psutil Pillow interception-python openpyxl uiautomation
)

REM 3. Ensure Interception Library DLL and Ring-0 Driver are in place
if not exist "interception.dll" (
    if exist "Interception\Interception\library\x64\interception.dll" (
        copy /y "Interception\Interception\library\x64\interception.dll" "interception.dll" >nul
        echo [OK] Copied interception.dll to workspace.
    )
)
if exist "installer\install-interception.exe" (
    echo [*] Checking Interception Ring-0 Kernel Driver status...
    python -c "import sys; sys.path.insert(0, 'final_bot'); from core.driver_installer import is_interception_driver_installed; sys.exit(0 if is_interception_driver_installed() else 1)" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [*] Installing Interception Ring-0 Driver with Administrator privileges...
        powershell -Command "Start-Process '%~dp0installer\install-interception.exe' -ArgumentList '/install' -Verb RunAs -Wait"
        echo [NOTICE] Please restart your PC after driver installation.
    ) else (
        echo [OK] Ring-0 Interception Kernel Driver verified active.
    )
)

REM 4. Compile In-Process Nextgen.exe Host (Zero-bloat native launcher)
set CSC=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe
if exist "%CSC%" (
    echo.
    echo [*] Compiling native Nextgen.exe CLR host launcher...
    "%CSC%" /nologo /target:exe /platform:x64 /out:"%~dp0Nextgen.exe" "%~dp0Nextgen.cs" >nul 2>&1
    if exist "%~dp0Nextgen.exe" (
        echo [OK] Nextgen.exe built successfully.
    )
)

REM 5. Create Desktop Shortcut
echo.
echo [*] Creating Desktop Shortcut...
python -c "import win32com.client, os; w = win32com.client.Dispatch('WScript.Shell'); s = w.CreateShortcut(os.path.expandvars(r'%%USERPROFILE%%\Desktop\Nextgen Autonomous Workforce.lnk')); s.TargetPath = r'%~dp0Nextgen.exe'; s.WorkingDirectory = r'%~dp0'; s.Description = 'Nextgen Autonomous Workforce Suite'; s.Save(); print('[OK] Desktop shortcut created: Nextgen Autonomous Workforce.lnk')" >nul 2>&1

echo.
echo ===============================================================================
echo [SETUP COMPLETE] All dependencies configured successfully!
echo.
echo HOW TO LAUNCH:
echo   - Double-click the desktop shortcut: 'Nextgen Autonomous Workforce'
echo   - Or double-click: Nextgen_Workforce.exe
echo   - Or run: start_workday.bat
echo ===============================================================================
echo.
pause
exit /b 0

:setup_standalone_shortcuts
echo.
echo [*] Checking Ring-0 Hardware Filter Driver status...
"%~dp0Nextgen_Workforce.exe" --verify >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Ring-0 Interception Kernel Driver verified active.
) else (
    echo [!] Ring-0 Interception Driver not yet bound on this PC.
    echo [*] Launching 1-click Ring-0 Driver Installer with Administrator privileges...
    if exist "%~dp0installer\install-interception.exe" (
        powershell -Command "Start-Process '%~dp0installer\install-interception.exe' -ArgumentList '/install' -Verb RunAs -Wait"
    ) else (
        powershell -Command "Start-Process '%~dp0Nextgen_Workforce.exe' -ArgumentList '--install-driver' -Verb RunAs -Wait"
    )
    echo.
    echo [NOTICE] If you just installed the driver, please restart your PC before running automation.
)

echo.
echo [*] Creating Desktop Shortcut for Nextgen Workforce...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([System.IO.Path]::Combine([System.Environment]::GetFolderPath('Desktop'), 'Nextgen Autonomous Workforce.lnk')); $s.TargetPath = '%~dp0Nextgen_Workforce.exe'; $s.WorkingDirectory = '%~dp0'; $s.Description = 'Nextgen Autonomous Workforce Engine'; $s.Save()" >nul 2>&1
echo [OK] Desktop shortcut created: Nextgen Autonomous Workforce.lnk

echo.
echo ===============================================================================
echo [SETUP COMPLETE] Standalone Enterprise Workforce Ready!
echo.
echo HOW TO LAUNCH:
echo   - Double-click the desktop shortcut: 'Nextgen Autonomous Workforce'
echo   - Or double-click: Nextgen_Workforce.exe
echo   - Or run: start_workday.bat
echo ===============================================================================
echo.
pause
exit /b 0
