@echo off
echo ========================================================
echo FINAL BOT - PLUG AND PLAY INSTALLER
echo ========================================================
echo.
echo Step 1/3: Installing Python Dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies. Ensure Python is installed and in PATH.
    pause
    exit /b %errorlevel%
)
echo Python dependencies installed successfully!
echo.

echo Step 2/3: Extracting Interception Driver...
powershell -Command "Expand-Archive -Force 'Interception.zip' 'Interception'"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to extract Interception.zip.
    pause
    exit /b %errorlevel%
)
echo Extracted successfully!
echo.

echo Step 3/3: Installing Interception Driver (Requires Admin Privileges)...
echo This will prompt you for Administrator permissions.
powershell -Command "Start-Process -FilePath 'Interception\command line installer\install-interception.exe' -ArgumentList '/install' -Verb RunAs -Wait"

echo.
echo ========================================================
echo INSTALLATION COMPLETE!
echo ========================================================
echo The Interception driver has been successfully installed.
echo HOWEVER, WINDOWS REQUIRES A RESTART FOR THE DRIVER TO LOAD.
echo.
echo Please save your work, and press any key to restart your computer now.
echo If you close this window, YOU MUST MANUALLY RESTART before using the bot.
pause
shutdown /r /t 5 /c "Restarting to finalize Interception Driver installation..."
