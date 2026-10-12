import ctypes
import threading
import time
from pynput import keyboard
from core import state
from core.logger import log
from core.input_driver import emergency_cleanup

# ============================================================
# WINDOWS IDLE DETECTION STRUCTS
# ============================================================
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]

def get_idle_time_ms():
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
        return ctypes.windll.kernel32.GetTickCount() - lii.dwTime
    return 0

def _get_last_input_tick():
    """Return Windows tick count of the last keyboard or mouse input event."""
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
    return lii.dwTime

# ============================================================
# DAEMON
# ============================================================
_last_input_tick = ctypes.windll.kernel32.GetTickCount()
_ignore_until = 0.0

def set_ignore_until(t):
    global _ignore_until
    _ignore_until = t

def mouse_killswitch_daemon():
    """
    Fires instantly when Windows registers any keyboard or mouse event from
    the human — regardless of cursor position or bot cursor activity.
    """
    global _last_input_tick
    _last_input_tick = _get_last_input_tick()

    while True:
        time.sleep(0.04)

        if not state.automation_active.is_set() or state.is_stopped():
            _last_input_tick = _get_last_input_tick()
            continue

        tick = _get_last_input_tick()
        if tick != _last_input_tick:
            if state.injecting_key.locked() or time.time() < _ignore_until:
                # This was a bot-injected input, just update the known tick and ignore
                _last_input_tick = tick
            else:
                log('Human input detected. Yielding control.')
                state.request_stop()
                try:
                    emergency_cleanup()
                except Exception:
                    pass
                _last_input_tick = tick

# ============================================================
# ESC HANDOFF
# ============================================================
_last_esc_time = 0.0
_esc_tap_count = 0

def _on_press(key):
    global _last_esc_time, _esc_tap_count
    if key == keyboard.Key.esc:
        if state.injecting_key.locked():
            return
        if state.automation_active.is_set():
            now = time.monotonic()
            if now - _last_esc_time <= 0.8:
                _esc_tap_count += 1
            else:
                _esc_tap_count = 1
            _last_esc_time = now
            if _esc_tap_count >= 2:
                _esc_tap_count = 0
                log('Double-ESC: yielding control to human...')
                try:
                    emergency_cleanup()
                except Exception:
                    pass
                state.request_stop()

def start_daemons():
    listener = keyboard.Listener(on_press=_on_press)
    listener.daemon = True
    listener.start()
    threading.Thread(target=mouse_killswitch_daemon, daemon=True).start()
