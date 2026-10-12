import ctypes
import time
import platform
from core import state
from core.input_driver import hotkey
from core.logger import log

def get_foreground_title():
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        if not length:
            return ''
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    except Exception as e:
        log(f"Verification Error: Failed to get foreground title - {e}")
        return ''

def is_window_zoomed(hwnd):
    return ctypes.windll.user32.IsZoomed(hwnd) != 0

def wait_for_window(fragments, timeout=12.0):
    """
    Verification Panel: Robustly waits for a window whose title matches ANY of the provided fragments.
    Returns True if successful, False if it timed out.
    """
    if isinstance(fragments, str):
        fragments = [fragments]
        
    log(f"Verification: Waiting for window matching {fragments}...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        if state.is_stopped(): return False
        
        current_title = get_foreground_title().lower()
        for frag in fragments:
            if frag.lower() in current_title:
                log(f"Verification Success: Found window '{current_title}'")
                return True
        time.sleep(0.5)
        
    log(f"Verification Failed: Timeout waiting for window {fragments}")
    return False

def focus_window_by_title(fragments):
    """
    Verification Panel: Attempts to find an existing window by title fragment and focus it.
    Uses AttachThreadInput to bypass Windows focus stealing restrictions.
    """
    if isinstance(fragments, str):
        fragments = [fragments]
        
    found = [False]
    def cb(hwnd, _):
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        current_title = buf.value.lower()
        
        for frag in fragments:
            if frag.lower() in current_title:
                user32 = ctypes.windll.user32
                foreground_hwnd = user32.GetForegroundWindow()
                
                if foreground_hwnd != hwnd:
                    foreground_thread = user32.GetWindowThreadProcessId(foreground_hwnd, None)
                    target_thread = user32.GetWindowThreadProcessId(hwnd, None)
                    
                    if foreground_thread and target_thread and (foreground_thread != target_thread):
                        user32.AttachThreadInput(target_thread, foreground_thread, True)
                        user32.BringWindowToTop(hwnd)
                        user32.ShowWindow(hwnd, 9) # SW_RESTORE
                        user32.SetForegroundWindow(hwnd)
                        user32.AttachThreadInput(target_thread, foreground_thread, False)
                    else:
                        user32.BringWindowToTop(hwnd)
                        user32.ShowWindow(hwnd, 9) # SW_RESTORE
                        user32.SetForegroundWindow(hwnd)
                else:
                    user32.ShowWindow(hwnd, 9) # SW_RESTORE
                
                found[0] = True
                return False # Stop enumerating
        return True
        
    Proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    ctypes.windll.user32.EnumWindows(Proc(cb), 0)
    
    if found[0]:
        time.sleep(0.6)
    return found[0]

def maximize_active_window(retries=3):
    """
    Verification Panel: Attempts to maximize the window and explicitly VERIFIES if it worked.
    Uses 'win + up' as requested by the user. If it fails, retries.
    """
    if platform.system() != 'Windows':
        return
        
    log("Verification: Attempting to maximize active window...")
    for attempt in range(retries):
        if state.is_stopped(): return
        
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            time.sleep(0.5)
            continue
            
        if is_window_zoomed(hwnd):
            log("Verification Success: Window is already maximized.")
            return True
            
        # The user requested start + up (win + up)
        hotkey('win', 'up')
        time.sleep(1.0)
        
        if is_window_zoomed(hwnd):
            log("Verification Success: Window successfully maximized via win+up.")
            return True
        else:
            log(f"Verification Retry {attempt+1}: Window failed to maximize, trying again.")
            
    log("Verification Failed: Could not maximize window after all retries.")
    return False


def close_app_safely():
    log("Closing application cleanly (Alt+F4)")
    hotkey('alt', 'f4')
    
def close_tab_safely():
    log("Closing tab cleanly (Ctrl+W)")
    hotkey('ctrl', 'w')
