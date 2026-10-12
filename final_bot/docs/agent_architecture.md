# Final Bot Architecture & Developer Guide

**ATTENTION ALL AGENTS:** 
You MUST read this file before modifying the codebase. 
You MUST update this file when you change the architecture, add new tasks, or fix major bugs.
Do NOT assume operations succeed; always use verification panels (e.g., check if a window actually exists before interacting with it).

## Directory Structure
The bot is split into modular components for stability, easy debugging, and strict error boundaries.

- **`main_shorts.py`**: Entry point for full system automation (Web + System tasks).
- **`main_firefox.py`**: Entry point for web-only automation.
- **`config/settings.py`**: All global variables, URLs (stripped of HTTPS), timings, scroll profiles.
- **`core/killswitch.py`**: `GetLastInputInfo` daemon to instantly halt automation on human input.
- **`core/input_driver.py`**: Low-level Interception driver wrappers. Every call is wrapped in a strict try/catch.
- **`core/human_physics.py`**: WindMouse algorithm, typing dynamics, active waits, and natural scrolling.
- **`core/window_manager.py`**: Strict window verification. Uses robust title matching and retry logic for UI actions.
- **`tasks/scheduler.py`**: The main execution loop. Handles task picking, task execution, and breaks.
- **`tasks/web_tasks.py`**: Browser-based tasks (Wiki, Reddit, Shorts, News, etc.). Fullscreen (`F11`) capability for Shorts.
- **`tasks/system_tasks.py`**: Desktop tasks (CMD, VSCode, Paint, Notepad, Task Manager).
- **`tasks/shared.py`**: Common application launchers (e.g. Start menu interaction) with error boundaries.

## Core Principles
1. **Never Assume, Always Verify (Verification Panels):** 
   If a task opens an app (e.g., `cmd`), it MUST verify the app window is actually foregrounded via `wait_for_window`. If title matching fails, it safely logs it or retries. All major steps output `Verification Success / Failed` to logs.
2. **Strict Try-Catch Boundaries:**
   Every input injection (`interception.move_to`, `.scroll`, `.write`) must be wrapped in `try-except` to prevent driver blips from crashing the entire 15-minute task.
3. **Instant Yield:**
   The human killswitch (`GetLastInputInfo`) is paramount. Any detected input must instantly set the `stop_automation_event`. All loops must check this event every step.

## Known Bugs & Fixes Log

| Date | Issue | Resolution |
| :--- | :--- | :--- |
| 2026-10-07 | Codebase too large, hard to debug. | Refactored into the `final_bot` modular structure across `core/` and `tasks/`. |
| 2026-10-07 | Bot tripped on its own mouse/scroll inputs. | `interception` driver inputs *do* update OS tick. Wrapped mouse and scroll methods inside `with state.injecting_key:` lock in `core/input_driver.py`. |
| 2026-10-07 | Killswitch race condition. | Added `_bump_grace()` to all `core/input_driver.py` functions to give a 0.15s window where OS tick updates don't trip the human daemon. |
| 2026-10-07 | `win + r` (Run dialog) gets stuck. | Updated `tasks/shared.py` to press the `win` key (Start menu) directly to search and launch apps. |
| 2026-10-07 | Window maximization issues (`start+up` user request). | In `core/window_manager.py`, `maximize_active_window` explicitly uses `win+up` in a retry loop. It queries `IsZoomed` to verify success, falling back on retries if the browser ignores it. |
| 2026-10-07 | Shorts video not fullscreen. | Added `set_full_screen()` (F11) into `web_tasks.py` specifically for `task_watch_shorts` so the video occupies the full monitor. |
| 2026-10-07 | Driver blips caused scrolling to crash tasks halfway through. | Added granular `try/except` around every Interception module call in `core/input_driver.py`. Handled `scroll` direction literals explicitly. |
| 2026-10-07 | Scrolling hit desktop instead of browser. | Forced explicit `human_mouse_move` to the center of the screen `(sw//2, sh//2)` prior to any scroll operation to ensure target focus. |
| 2026-10-07 | MS Paint task did not draw. | Paint title verification fails in Win11. Bypassed strict abort. Added center-canvas click to guarantee canvas focus, wrapped drawing loops in strict exceptions. |
| 2026-10-07 | URLs typing failed due to HTTPS / browser auto-format. | Stripped all URLs in `config/settings.py` so the bot types domains natively just like a human. |
