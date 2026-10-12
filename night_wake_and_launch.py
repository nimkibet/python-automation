"""
Night Scheduler & Auto-Launcher for Loggy3 + Final Bot
======================================================
Workflow:
1. When launched, checks the current time.
   - If it is NOT 3:00 AM:
     - Configures Windows to enable ACPI RTC wake timers (on both AC and battery).
     - Sets a hardware waitable wake timer to wake the computer up at exactly 03:00 AM.
     - Puts the laptop into Sleep mode (Standby S3).
   - If the computer was already ON (or was kept awake / woke up early), it waits until 03:00 AM.
2. At 03:00 AM:
   - Wakes up the display, acquires interactive desktop session, and restores execution state.
   - Launches Loggy3 using the Start Menu route (Win key -> type 'loggy3' -> Enter).
   - Waits 60 seconds (1 minute) for Loggy3 to fully load and initialize.
   - Maximizes Loggy3 window and brings it forcefully to the foreground.
   - Clicks the bottom-left action button (using relative layout coordinates:
     left padding ~0.75%, bottom padding ~1.4%, centered within the bottom bar).
   - Minimizes Loggy3.
   - Launches 'final.bat' (Idle Shorts Bot) in a new console window.
"""

import ctypes
from ctypes import wintypes
import datetime
import os
import subprocess
import sys
import time

# Win32 API handles
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
powrprof = ctypes.windll.powrprof

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FINAL_BAT = os.path.join(BASE_DIR, "final.bat")
START_FINAL_BAT = os.path.join(BASE_DIR, "start_final.bat")

# Window ShowWindow Constants
SW_HIDE = 0
SW_NORMAL = 1
SW_SHOWMINIMIZED = 2
SW_MAXIMIZE = 3
SW_SHOWNOACTIVATE = 4
SW_SHOW = 5
SW_MINIMIZE = 6
SW_RESTORE = 9

# Mouse Events
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

# Thread Execution State flags
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

def log(msg):
    timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
    print(f"{timestamp} {msg}", flush=True)

def bind_to_interactive_desktop():
    """Binds the current thread to the active user's interactive desktop."""
    GENERIC_ALL = 0x10000000
    desk = user32.OpenInputDesktop(0, False, GENERIC_ALL)
    if desk:
        user32.SetThreadDesktop(desk)
        user32.CloseDesktop(desk)
        return True
    return False

def press_key(vk):
    """Simulates a physical key press and release."""
    user32.keybd_event(vk, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(vk, 0, 0x0002, 0)

def enable_windows_wake_timers():
    """Ensures Windows Power Scheme allows RTC wake timers on both AC (plugged-in) and DC (battery)."""
    try:
        log("Configuring Windows Power Scheme to allow wake timers...")
        subprocess.run(["powercfg", "/SETACVALUEINDEX", "SCHEME_CURRENT", "SUB_SLEEP", "RTCWAKE", "1"], capture_output=True)
        subprocess.run(["powercfg", "/SETDCVALUEINDEX", "SCHEME_CURRENT", "SUB_SLEEP", "RTCWAKE", "1"], capture_output=True)
        subprocess.run(["powercfg", "/SETACTIVE", "SCHEME_CURRENT"], capture_output=True)
        log("Wake timers enabled on AC and Battery.")
    except Exception as e:
        log(f"Warning: Could not configure powercfg: {e}")

def get_seconds_until_3am():
    """
    Returns seconds remaining until the next 03:00:00 AM.
    If current time is already between 03:00 and 03:05 AM, returns 0.
    """
    now = datetime.datetime.now()
    if now.hour == 3 and now.minute <= 5:
        return 0

    if now.hour < 3:
        target = now.replace(hour=3, minute=0, second=0, microsecond=0)
    else:
        target = (now + datetime.timedelta(days=1)).replace(hour=3, minute=0, second=0, microsecond=0)

    diff = (target - now).total_seconds()
    return max(0, diff)

def set_wake_timer_and_sleep(seconds_to_wait):
    """
    Sets a hardware RTC wake timer with fResume=True and puts Windows to sleep.
    """
    target_dt = datetime.datetime.now() + datetime.timedelta(seconds=seconds_to_wait)
    log(f"Setting hardware ACPI wake timer for: {target_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Time remaining until 03:00 AM: {int(seconds_to_wait // 3600)}h {int((seconds_to_wait % 3600) // 60)}m {int(seconds_to_wait % 60)}s")

    hTimer = kernel32.CreateWaitableTimerW(None, True, "Loggy3_3AM_WakeTimer")
    if not hTimer:
        log(f"Error: Failed to create waitable timer (Err={kernel32.GetLastError()}). Sleeping via time.sleep.")
        time.sleep(seconds_to_wait)
        return

    due_time = ctypes.c_longlong(-int(seconds_to_wait * 10_000_000))
    success = kernel32.SetWaitableTimer(hTimer, ctypes.byref(due_time), 0, None, None, True)
    if not success:
        log(f"Error: SetWaitableTimer failed (Err={kernel32.GetLastError()}). Falling back to time.sleep.")
        time.sleep(seconds_to_wait)
        kernel32.CloseHandle(hTimer)
        return

    log("Hardware wake timer registered successfully with Windows ACPI.")
    log("Putting laptop into Sleep mode now... Goodnight! (Will wake up at 03:00 AM)")
    time.sleep(1.5)

    powrprof.SetSuspendState(False, False, False)

    log("Waiting for 03:00 AM signal (whether asleep or awake)...")
    kernel32.WaitForSingleObject(hTimer, 0xFFFFFFFF)

    kernel32.CancelWaitableTimer(hTimer)
    kernel32.CloseHandle(hTimer)
    log("Wake timer triggered! 03:00 AM reached.")

def wake_system_display():
    """Wakes the screen and prevents Windows from going back to sleep."""
    log("Keeping display and system awake...")
    bind_to_interactive_desktop()
    kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
    
    # Nudge mouse slightly to wake the monitor backlight
    user32.mouse_event(0x0001, 1, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0001, -1, 0, 0, 0)
    time.sleep(1.0)

def open_loggy_via_start():
    """Opens Loggy3 using the Start Menu route (Win key -> type loggy3 -> Enter)."""
    bind_to_interactive_desktop()
    log("Opening Start menu...")
    press_key(0x5B) # Win key
    time.sleep(1.2)

    log("Typing 'loggy3'...")
    for ch in "loggy3":
        vk = user32.VkKeyScanW(ord(ch)) & 0xFF
        press_key(vk)
        time.sleep(0.08)

    time.sleep(0.6)
    log("Pressing Enter to launch/focus Loggy3...")
    press_key(0x0D) # Enter key
    time.sleep(3.0)

def find_loggy_window():
    """Finds the main window handle (HWND) for Loggy3."""
    bind_to_interactive_desktop()
    found_hwnd = [None]
    
    def cb(hwnd, _):
        if user32.IsWindow(hwnd):
            l = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(l + 1)
            user32.GetWindowTextW(hwnd, buf, l + 1)
            cls_buf = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, cls_buf, 256)
            
            if buf.value == "Loggy3" and "Tauri" in cls_buf.value:
                found_hwnd[0] = hwnd
                return False
            elif "loggy3" in buf.value.lower() and "recorder" not in buf.value.lower():
                found_hwnd[0] = hwnd
                return False
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return found_hwnd[0]

def focus_and_maximize_window(hwnd):
    """Restores, maximizes, and brings the target window to the foreground."""
    bind_to_interactive_desktop()
    log("Restoring and maximizing Loggy3 window...")
    user32.ShowWindow(hwnd, SW_RESTORE)
    time.sleep(0.5)
    user32.ShowWindow(hwnd, SW_MAXIMIZE)
    time.sleep(1.0)

    fg_hwnd = user32.GetForegroundWindow()
    if fg_hwnd != hwnd:
        fg_tid = user32.GetWindowThreadProcessId(fg_hwnd, None)
        target_tid = user32.GetWindowThreadProcessId(hwnd, None)
        if fg_tid and target_tid and fg_tid != target_tid:
            user32.AttachThreadInput(target_tid, fg_tid, True)
            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)
            user32.AttachThreadInput(target_tid, fg_tid, False)
        else:
            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)
    time.sleep(1.0)

def click_loggy_button(hwnd):
    """
    Clicks the bottom-left action button in Loggy3 based on user specifications:
    - Left padding: 0.5% - 1%
    - Bottom padding: 1% - 1.5%
    - Width: ~6%, Height: ~3.5%
    """
    bind_to_interactive_desktop()
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    
    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)
    
    left = max(0, rect.left)
    top = max(0, rect.top)
    width = min(screen_w, rect.right - left)
    height = min(screen_h, rect.bottom - top)

    click_x = left + int(width * 0.055)
    click_y = top + int(height * 0.967)

    log(f"Screen resolution: {screen_w}x{screen_h}. Target button coordinate: ({click_x}, {click_y})")

    # Optional color check via PIL
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab(bbox=(click_x - 5, click_y - 5, click_x + 5, click_y + 5))
        r, g, b = img.getpixel((5, 5))[:3]
        log(f"Detected pixel color at target button: R={r}, G={g}, B={b}")
        if r > 160 and g < 90 and b < 90:
            log("Notice: Red button detected (Loggy3 is already recording).")
            log("Loggy3 is currently recording. Keeping session active.")
            return
    except Exception as e:
        log(f"Color check note: {e}")

    log(f"Clicking Loggy3 button at ({click_x}, {click_y})...")
    user32.SetCursorPos(click_x, click_y)
    time.sleep(0.3)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.12)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(1.0)
    log("Button clicked successfully.")

def minimize_window(hwnd):
    """Minimizes the specified window."""
    bind_to_interactive_desktop()
    log("Minimizing Loggy3 window...")
    user32.ShowWindow(hwnd, SW_MINIMIZE)
    time.sleep(1.5)
    log("Loggy3 minimized.")

def launch_final_bot():
    """Starts final.bat in a separate console window."""
    bat_to_run = FINAL_BAT if os.path.exists(FINAL_BAT) else START_FINAL_BAT
    log(f"Starting secondary automation script: {bat_to_run}")

    if not os.path.exists(bat_to_run):
        log(f"Error: Could not locate batch file at {bat_to_run}!")
        return False

    working_dir = os.path.dirname(bat_to_run)
    subprocess.Popen(
        ["cmd.exe", "/c", os.path.basename(bat_to_run)],
        cwd=working_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    log("Final bot batch process launched successfully!")
    return True

def execute_3am_payload():
    """Executes the entire 3:00 AM sequence."""
    log("==================================================")
    log("Executing 3:00 AM Scheduled Task Sequence")
    log("==================================================")

    # 1. Wake display
    wake_system_display()

    # 2. Launch Loggy3 via Start Menu route
    log("Launching/Focusing Loggy3 via Start Menu route...")
    open_loggy_via_start()

    # 3. Wait 60 seconds (1 minute minimum) for Loggy3 to fully load as requested
    log("Waiting 60 seconds (1 minute minimum) for Loggy3 to fully load and initialize...")
    for remaining in range(60, 0, -5):
        log(f"Loading Loggy3... {remaining}s remaining")
        time.sleep(5)
    log("1 minute load time elapsed! Now detecting Loggy3 window...")

    # 4. Find window
    hwnd = None
    for attempt in range(15):
        hwnd = find_loggy_window()
        if hwnd:
            log(f"Found Loggy3 window: HWND={hwnd}")
            break
        time.sleep(1.0)

    # 5. Maximize, click button, and minimize
    if hwnd:
        focus_and_maximize_window(hwnd)
        time.sleep(2.0)

        click_loggy_button(hwnd)
        time.sleep(2.0)

        minimize_window(hwnd)
        time.sleep(1.5)
    else:
        log("Warning: Could not locate Loggy3 main window HWND after launch.")

    # 6. Start other script (final.bat)
    launch_final_bot()

    log("==================================================")
    log("Night automation sequence completed successfully!")
    log("==================================================")

def main():
    log("Night Wake & Auto-Launch Service Started.")
    bind_to_interactive_desktop()
    enable_windows_wake_timers()

    sec_until_3am = get_seconds_until_3am()

    if sec_until_3am > 0:
        log("Current time is NOT 3:00 AM.")
        set_wake_timer_and_sleep(sec_until_3am)
    else:
        log("Current time is 3:00 AM! Executing immediately without sleep.")

    execute_3am_payload()

if __name__ == "__main__":
    main()
