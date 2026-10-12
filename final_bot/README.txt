========================================================
FINAL BOT - INSTALLATION & DEPLOYMENT GUIDE (NEW PC)
========================================================

To run this bot on a completely different PC, you cannot simply copy the python scripts. The bot uses a kernel-level hardware driver (Interception) to completely bypass anti-bot and anti-cheat detections, and this driver must be physically installed on the new Windows machine.

INSTALLATION (PLUG & PLAY)
--------------------------------------------------------
1. Right-click `install.bat` and select "Run as Administrator" (or just double click it and accept the admin prompt).
2. The script will automatically install all Python dependencies.
3. The script will automatically extract and install the Interception Kernel Driver.
4. The script will prompt you to reboot your PC. YOU MUST REBOOT for the driver to load.


RUN THE BOT
--------------------------------------------------------
Once rebooted, open a command prompt in this `final_bot` folder and choose your browser entry point:

For Firefox:  python main_firefox.py
For Brave:    python main_shorts.py
For Chrome:   python main_chrome.py
For Edge:     python main_edge.py

The bot will automatically map your keyboard and mouse, wait for 120 seconds of idle time, and begin.
Double-tap ESC at any point to instantly yield control back to you.
