# Python Automation Suite

> **Undetectable Hardware-Level Windows Activity Emulation & Automated Night Scheduling**

A production-grade Python automation framework designed to simulate authentic human computer activity on Windows without triggering synthetic input detection flags. Includes a modular multi-task bot engine and an autonomous 3:00 AM Night Scheduler for application automation and power management.

---

## Table of Contents
- [Key Features](#key-features)
- [Project Directory Structure](#project-directory-structure)
- [Prerequisites & System Requirements](#prerequisites--system-requirements)
- [Step-by-Step Installation Guide](#step-by-step-installation-guide)
  - [Step 1: Install the Interception Driver](#step-1-install-the-interception-driver)
  - [Step 2: Install Python Dependencies](#step-2-install-python-dependencies)
- [How to Run the Automation](#how-to-run-the-automation)
  - [1. Running the Main Modular Automation Bot](#1-running-the-main-modular-automation-bot)
  - [2. Running the 3:00 AM Night Scheduler](#2-running-the-300-am-night-scheduler)
  - [3. Running Legacy Monolithic Scripts](#3-running-legacy-monolithic-scripts)
- [Core Architecture & Modules](#core-architecture--modules)
- [Configuration Guide](#configuration-guide)
- [Safety & Emergency Controls](#safety--emergency-controls)
- [License](#license)

---

## Key Features

1. **Kernel-Level Hardware Input Emulation**
   - Driven by the low-level **Interception** kernel driver (`interception-python`).
   - Bypasses standard Windows synthetic input detection (`LLMHF_INJECTED` and `SendInput` flags).
   - Indistinguishable from physical USB keyboard and mouse hardware events.

2. **Organic Human Physics Emulation**
   - **Mouse Dynamics:** Smooth Cubic Bezier trajectories with ease-in acceleration, ease-out deceleration, and micro-jitter. Eliminates linear robotic movements and abrupt high-speed stops.
   - **Typing Dynamics:** Non-linear typing flow simulating natural human thought patterns, variable bursts, typing fatigue, bigram acceleration, and QWERTY typo-correction simulation.
   - **Scroll Dynamics:** Chaotic burst scrolling with variable notch delays, hesitation pauses, and reading drift.

3. **Multi-Application Task Suite**
   - **Web Tasks:** YouTube Shorts browsing, Wikipedia reading with `Alt + Shift + X` shortcuts, Multi-Genre E-Commerce & Shopping browsing (Jumia, Alibaba, AliExpress, Amazon, eBay, Etsy, Target, etc.), Tech News reading (with smart `F5` reload optimization), Reddit browsing, GitHub Trending exploration, and Project Gutenberg novel reading.
   - **Desktop Tasks:** Notepad essay authoring, MS Paint freehand drawing, Command Prompt diagnostic commands, and VS Code programming sessions.

4. **Zero-Trust Safety & Emergency Yield**
   - **Instant Mouse Killswitch:** Background daemon detects physical human mouse input and instantly yields control without false trips.
   - **Double-Tap ESC Yield:** Instant graceful stop via quick double-tap of the `ESC` key.
   - **Window Focus Management:** Employs the `AttachThreadInput` Windows API bypass to safely bring windows to the front without taskbar flashing.

5. **3:00 AM Autonomous Night Scheduler (`night_wake_and_launch.py`)**
   - If launched before 3:00 AM, automatically configures Windows power settings to enable RTC wake timers (on both AC power and Battery) and puts the laptop into **Standby (S3) Sleep**.
   - Wakes the computer up at exactly **03:00 AM**, awakens the display backlight, launches **Loggy3** via the Windows Start search route, counts down a 60-second initialization period, maximizes the window, clicks the bottom-left action button, minimizes the window, and automatically chain-launches the main automation bot (`final.bat`).

---

## Project Directory Structure

```text
.
├── final_bot/                           # Main modular bot engine
│   ├── config/
│   │   └── settings.py                  # Core configuration (timeouts, URLs, essay topics, profiles)
│   ├── core/
│   │   ├── human_physics.py             # Cubic Bezier mouse easing, typing flow, scroll dynamics
│   │   ├── input_driver.py              # Low-level Interception driver wrapper & safe key/mouse APIs
│   │   ├── killswitch.py                # Human input detection, double-ESC handler, idle timer
│   │   ├── logger.py                    # Structured logging utility with timestamps
│   │   ├── state.py                     # Thread-safe cross-module state & stop event signaling
│   │   └── window_manager.py            # Window focusing (AttachThreadInput bypass) & window states
│   ├── docs/
│   │   └── agent_architecture.md        # Technical architecture documentation
│   ├── tasks/
│   │   ├── scheduler.py                 # Weighted task scheduler & break manager
│   │   ├── shared.py                    # Shared app launchers & browser navigation handlers
│   │   ├── system_tasks.py              # Notepad, MS Paint, CMD, VS Code, Task Manager tasks
│   │   └── web_tasks.py                 # YouTube Shorts, Wikipedia, News, Reddit, GitHub tasks
│   ├── install.bat                      # Automated dependency and driver installer for final_bot
│   ├── Interception.zip                 # Backup archive of Interception driver binaries
│   ├── main_chrome.py                   # Entry point configured for Google Chrome
│   ├── main_edge.py                     # Entry point configured for Microsoft Edge
│   ├── main_firefox.py                  # Entry point configured for Mozilla Firefox
│   ├── main_shorts.py                   # Primary entry point (configured for Brave Browser)
│   ├── README.txt                       # Quick reference text file
│   ├── requirements.txt                 # Python dependencies for final_bot
│   └── start_firefox.bat                # Batch launcher for Firefox bot
│
├── Interception/                        # Interception kernel-mode filter driver package
│   ├── Interception/
│   │   ├── command line installer/      # Installer executable directory
│   │   │   ├── install-interception.exe # Official driver installer binary
│   │   │   └── README.md                # Direct CLI installer instructions
│   │   ├── library/                     # C/C++ dynamic libraries and headers (x86 & x64)
│   │   ├── licenses/                    # Driver license terms
│   │   └── samples/                     # Driver diagnostic and sample utilities
│   └── README.md                        # Driver overview and setup instructions
│
├── final.bat                            # Primary one-click batch launcher (runs start_final.bat)
├── idle_firefox.py                      # Standalone monolithic legacy script (Firefox)
├── idle_shorts.py                       # Standalone monolithic legacy script (Brave)
├── install_dependencies.bat             # One-click pip installer for root requirements
├── night_wake_and_launch.py             # Autonomous 3:00 AM sleep/wake scheduler & Loggy3 launcher
├── requirements.txt                     # Unified Python dependencies for the repository
├── run_night_scheduler.bat              # Batch launcher for night_wake_and_launch.py
├── start_final.bat                      # Clean startup script for final_bot/main_shorts.py
├── start_idle_firefox.bat               # Batch launcher for idle_firefox.py
├── start_idle_shorts.bat                # Batch launcher for idle_shorts.py
└── .gitignore                           # Excludes bytecode, caches, and log files
```

---

## Prerequisites & System Requirements

- **Operating System:** Windows 10 or Windows 11 (64-bit recommended).
- **Python Version:** Python 3.10, 3.11, or 3.12 (ensure Python is added to system `PATH`).
- **Privileges:** Administrator privileges are required once to install the Interception kernel driver.
- **Target Browsers:** Brave Browser (default for `main_shorts.py`), Google Chrome, Microsoft Edge, or Mozilla Firefox.

---

## Step-by-Step Installation Guide

### Step 1: Install the Interception Driver

The Interception kernel driver must be installed once so that Windows binds the filter to keyboard and mouse hardware ports.

1. Open **Command Prompt as Administrator**:
   - Press the `Windows Key`, type `cmd`, right-click **Command Prompt**, and select **Run as administrator**.

2. Navigate to the installer directory:
   ```cmd
   cd /d "%USERPROFILE%\Desktop\money needed\Interception\Interception\command line installer"
   ```

3. Run the installer:
   ```cmd
   install-interception.exe /install
   ```

4. You will see:
   ```text
   Interception successfully installed. You must reboot for it to take effect.
   ```

5. **Restart your computer**:
   ```cmd
   shutdown /r /t 0
   ```

---

### Step 2: Install Python Dependencies

1. Open a regular Command Prompt or terminal in the repository root directory:
   ```cmd
   cd /d "%USERPROFILE%\Desktop\money needed"
   ```

2. Run the dependency installer:
   ```cmd
   pip install -r requirements.txt
   ```
   *(Or simply double-click `install_dependencies.bat`)*

3. Verify that the Interception driver connects to Python:
   ```cmd
   python -c "import interception; interception.auto_capture_devices(); print('Success!')"
   ```

---

## How to Run the Automation

### 1. Running the Main Modular Automation Bot

To run the full modular bot (configured by default for Brave Browser with all 11 task types):

* **Option A (Recommended):** Double-click **`final.bat`** (or **`start_final.bat`**).
* **Option B (Command Line):**
  ```cmd
  cd /d "%USERPROFILE%\Desktop\money needed\final_bot"
  python main_shorts.py
  ```

#### How it Behaves:
- The bot initializes the driver and starts monitoring for system inactivity (`IDLE_TIMEOUT` is set to 120 seconds by default in `config/settings.py`).
- Once you leave your computer idle for the configured timeout, automation begins automatically.
- Tasks are picked in weighted rotation (YouTube Shorts, Wikipedia, News, Reddit, GitHub, Notepad, Paint, CMD, VS Code).
- Between tasks, the bot takes realistic human-like breaks (4 to 5 minutes).

---

### 2. Running the 3:00 AM Night Scheduler

If you are stepping away for the night and want your laptop to sleep and wake up automatically at 3:00 AM:

* **Option A:** Double-click **`run_night_scheduler.bat`**.
* **Option B (Command Line):**
  ```cmd
  cd /d "%USERPROFILE%\Desktop\money needed"
  python night_wake_and_launch.py
  ```

#### Sequence of Events:
1. **Sleep Phase:** If launched before 3:00 AM, it calculates the exact time remaining, sets an ACPI hardware wake timer, enables wake timers on AC/battery, and puts Windows into Sleep mode.
2. **Wake Phase:** At exactly 03:00 AM, the hardware timer wakes the laptop and turns on the display.
3. **Loggy3 Launch:** Opens the Start menu, types `loggy3`, and presses Enter.
4. **Initialization Countdown:** Waits a full 60 seconds (1 minute minimum) with a console countdown to allow Loggy3 to load completely.
5. **Window Maximization & Focus:** Snaps Loggy3 to full screen in the foreground.
6. **Action Click:** Moves the mouse to the bottom-left action button (dynamic relative coordinates) and clicks it.
7. **Minimization:** Minimizes Loggy3 to the taskbar.
8. **Bot Launch:** Automatically launches `final.bat` in a new console window to begin your daily automation routine.

---

### 3. Running Legacy Monolithic Scripts

If you prefer to run the standalone single-file versions without the modular structure:
- **Brave Browser:** Double-click `start_idle_shorts.bat` (runs `idle_shorts.py`).
- **Firefox Browser:** Double-click `start_idle_firefox.bat` (runs `idle_firefox.py`).

---

## Core Architecture & Modules

| Module / File | Responsibility |
|---|---|
| `final_bot/main_shorts.py` | Primary entry point for Brave browser automation. Configures weights, desktop binding, and idle loop. |
| `final_bot/core/input_driver.py` | Low-level wrapper around `interception`. Exposes `safe_press`, `hotkey`, `safe_move_to`, `safe_scroll`. |
| `final_bot/core/human_physics.py` | Easing-based mouse curves (`_ease_in_out_cubic`), typing flow-speed modulator, and erratic scroll delays. |
| `final_bot/core/killswitch.py` | High-frequency mouse tick observer and keyboard hook for instant handoff back to the human. |
| `final_bot/core/window_manager.py` | `AttachThreadInput` foreground focus bypass and `maximize_active_window` verification. |
| `final_bot/tasks/scheduler.py` | Weighted random task selection, execution timeouts, break timers, and consecutive error protection. |
| `night_wake_and_launch.py` | Power management, ACPI RTC wake timer, Start menu app launcher, and automated button clicker. |

---

## Configuration Guide

All primary settings are located in **`final_bot/config/settings.py`**:

- **`IDLE_TIMEOUT`**: Number of seconds of inactivity before automation begins (default: `120`).
- **`TOTAL_RUNTIME`**: Maximum continuous runtime for an automation session (default: `36000` = 10 hours).
- **`SHORTS_URL`**: Target URL for YouTube Shorts.
- **`WIKI_URLS`**: Wikipedia URLs used for random article browsing.
- **`SHOPPING_AND_EXPLORE_URLS`**: 25+ diverse online shopping, e-commerce (Jumia, Alibaba, AliExpress, Amazon, eBay, Etsy), tech reviews, travel, culture, and guides.
- **`TECH_NEWS_URLS`**: List of technology news portals rotated by the bot.
- **`REDDIT_URLS`**: Subreddits visited during community browsing.
- **`GITHUB_URLS`**: GitHub trending repositories explored.
- **`NOVEL_URLS`**: Project Gutenberg full-text novel URLs.
- **`ESSAY_TOPICS`**: Realistic multi-paragraph essay templates typed into Notepad.
- **`SCROLL_PROFILES`**: Scroll notch ranges, pause intervals, backwards scroll probability, and distraction drifts for each content type (includes `shopping` profile).

---

## Safety & Emergency Controls

- **Double-Tap `ESC`:** Quickly tap the `ESC` key twice at any time during automation to immediately yield control back to you. The bot cleanly releases all held keys and mouse buttons.
- **Move the Mouse:** Any physical movement of the mouse or human keypress will trigger the killswitch daemon, immediately yielding control and cleaning up input state.
- **Closing the Window:** Closing the command prompt window will cleanly and immediately terminate the automation process.

---

## License

This project is licensed under the MIT License. Driver components are governed by their respective licenses in `Interception/Interception/licenses/`.
