import time
import random
from core import state
from core.logger import log
from core.input_driver import hotkey, safe_press
from core.human_physics import human_typing
from core.window_manager import focus_window_by_title

def open_app_via_run(app_name):
    try:
        log(f"Verification: Pressing Start to open {app_name}")
        safe_press('win')
        time.sleep(random.uniform(0.85, 1.2))
        human_typing(app_name, wpm=random.randint(60, 95))
        time.sleep(random.uniform(0.3, 0.6))
        safe_press('enter')
        time.sleep(random.uniform(2.5, 4.5))
    except Exception as e:
        log(f"Error opening app via start menu: {e}")

def open_browser(browser_exe='brave', browser_title='Brave'):
    """Open a browser or focus it if already running."""
    if focus_window_by_title(browser_title):
        log(f"Verification Success: Browser '{browser_title}' already running. Focused.")
        return
        
    try:
        log(f"Verification: Browser not found. Launching '{browser_exe}' via Start menu.")
        safe_press('win')
        time.sleep(random.uniform(0.85, 1.2))
        human_typing(browser_exe, wpm=80)
        time.sleep(0.35)
        safe_press('enter')
        time.sleep(random.uniform(3.0, 5.5))
    except Exception as e:
        log(f"Error launching browser: {e}")

def _open_url(url):
    """Open a new tab, navigate to url. Returns False if stopped."""
    log(f"Opening URL: {url}")
    try:
        # Snap the browser to the front before typing to prevent wrong-window URL typing
        from core.window_manager import focus_window_by_title
        focus_window_by_title(['Firefox', 'Brave'])
        time.sleep(0.5)

        hotkey('ctrl', 't')
        time.sleep(random.uniform(0.35, 0.65))
        hotkey('ctrl', 'l')
        time.sleep(random.uniform(0.20, 0.40))
        human_typing(url, wpm=95)
        if state.is_stopped(): return False
        safe_press('enter')
        time.sleep(random.uniform(2.5, 4.5))
        return True
    except Exception as e:
        log(f"Error navigating to URL: {e}")
        return False
