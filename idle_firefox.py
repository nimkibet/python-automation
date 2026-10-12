import time
import random
import threading
import platform
import math
import ctypes
from pynput import keyboard

# ============================================================
# CONFIGURATION
# ============================================================
IDLE_TIMEOUT  = 30         # 30 seconds idle before automation starts
TOTAL_RUNTIME = 10 * 3600  # max runtime (10 hours)
LOG_FILE      = 'idle_firefox.log'

# ---- Site Pools ----
SHORTS_URL = 'https://www.youtube.com/shorts'

WIKI_URLS = [
    'https://en.wikipedia.org/wiki/Special:Random',
    'https://en.wikipedia.org/wiki/Special:Random',   # weighted higher
    'https://en.wikipedia.org/wiki/Special:Random',
    'https://simple.wikipedia.org/wiki/Special:Random',
]

TECH_NEWS_URLS = [
    'https://news.ycombinator.com/',
    'https://arstechnica.com/',
    'https://www.theverge.com/',
    'https://www.wired.com/',
    'https://techcrunch.com/',
    'https://www.engadget.com/',
    'https://www.bbc.com/news/technology',
    'https://www.technologyreview.com/',
    'https://thenextweb.com/',
    'https://www.scientificamerican.com/technology/',
]

REDDIT_URLS = [
    'https://www.reddit.com/r/technology/',
    'https://www.reddit.com/r/science/',
    'https://www.reddit.com/r/worldnews/',
    'https://www.reddit.com/r/programming/',
    'https://www.reddit.com/r/todayilearned/',
    'https://www.reddit.com/r/explainlikeimfive/',
    'https://www.reddit.com/r/Futurology/',
    'https://www.reddit.com/r/dataisbeautiful/',
]

GITHUB_URLS = [
    'https://github.com/trending',
    'https://github.com/trending/python',
    'https://github.com/trending/javascript',
    'https://github.com/explore',
]

NOVEL_URLS = [
    'https://www.gutenberg.org/cache/epub/1342/pg1342-images.html',  # Pride & Prejudice
    'https://www.gutenberg.org/cache/epub/84/pg84-images.html',      # Frankenstein
    'https://www.gutenberg.org/cache/epub/74/pg74-images.html',      # Tom Sawyer
    'https://www.gutenberg.org/cache/epub/1661/pg1661-images.html',  # Sherlock Holmes
    'https://www.gutenberg.org/cache/epub/2701/pg2701-images.html',  # Moby Dick
    'https://www.gutenberg.org/cache/epub/98/pg98-images.html',      # A Tale of Two Cities
    'https://www.gutenberg.org/cache/epub/11/pg11-images.html',      # Alice in Wonderland
    'https://www.gutenberg.org/cache/epub/1260/pg1260-images.html',  # Jane Eyre
    'https://www.gutenberg.org/cache/epub/5200/pg5200-images.html',  # Metamorphosis
    'https://www.gutenberg.org/cache/epub/16/pg16-images.html',      # Peter Pan
    'https://www.gutenberg.org/cache/epub/345/pg345-images.html',    # Dracula
    'https://www.gutenberg.org/cache/epub/219/pg219-images.html',    # Heart of Darkness
]

ESSAY_TOPICS = [
    (
        "The rapid advancement of artificial intelligence has fundamentally altered how we "
        "approach problem solving across every major industry. From predictive diagnostics in "
        "medicine to dynamic pricing in retail, machine learning systems now handle decisions "
        "that once required years of human expertise.\n\n"
        "Yet this transformation is not without its shadows. The concentration of AI capability "
        "in the hands of a few large technology companies raises genuine concerns about power, "
        "accountability, and the democratisation of opportunity. A small engineer team today can "
        "build tools that affect millions of lives, often without meaningful oversight.\n\n"
        "What is needed is not a slowdown of innovation, but a maturation of governance. "
        "Open research, auditable systems, and internationally coordinated policy frameworks "
        "could allow society to capture the benefits of AI while distributing its risks more fairly.\n\n"
    ),
    (
        "Climate science is unambiguous: the planet is warming at a rate unprecedented in the "
        "last ten thousand years, and human industrial activity is the primary driver. The "
        "consequences range from more frequent extreme weather events to rising sea levels that "
        "threaten coastal cities on every continent.\n\n"
        "The economic case for rapid decarbonisation is now stronger than the case against it. "
        "Renewable energy costs have collapsed over the past decade. Battery storage is following "
        "the same trajectory. The industries of the green economy — solar manufacturing, grid "
        "modernisation, electric vehicles — represent the largest employment opportunity of the "
        "coming generation.\n\n"
        "The barrier is not technological or even economic. It is political. Incumbent fossil fuel "
        "interests have spent decades funding doubt and delay. Breaking that gridlock requires "
        "informed voters, courageous legislators, and a media ecosystem capable of distinguishing "
        "scientific consensus from manufactured controversy.\n\n"
    ),
    (
        "The history of computing is a history of abstraction. Each generation of engineers built "
        "a higher floor for the next to stand on. Assembly language abstracted machine code. "
        "High-level languages abstracted assembly. Garbage collection abstracted memory management. "
        "The internet abstracted physical distance.\n\n"
        "Today, large language models are beginning to abstract natural language itself into "
        "executable computation. A developer can describe intent in plain English and receive "
        "working code. This is not a replacement for programming skill — it is a new and powerful "
        "tool that amplifies it.\n\n"
        "The developers who thrive in this era will be those who understand the underlying "
        "systems well enough to verify, correct, and direct AI-generated output. Deep knowledge "
        "of data structures, algorithms, and system design will matter more, not less, when AI "
        "handles the boilerplate.\n\n"
    ),
]

# ============================================================
# THREADING STATE
# ============================================================
_automation_active    = threading.Event()
stop_automation_event = threading.Event()

# ============================================================
# WINDOWS IDLE DETECTION  (must be before killswitch)
# ============================================================
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]

def get_idle_time_ms():
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
        return ctypes.windll.kernel32.GetTickCount() - lii.dwTime
    return 0

# ============================================================
# UNIVERSAL KILL-SWITCH & INTERCEPTION PATCH
# ============================================================
_bot_moving_mouse = False
_last_bot_mouse_pos = None

_last_input_tick = ctypes.windll.kernel32.GetTickCount()
_last_bot_activity_tick = ctypes.windll.kernel32.GetTickCount()

import interception
_orig_move_to = interception.move_to
_orig_scroll = interception.scroll
_orig_mouse_down = interception.mouse_down
_orig_mouse_up = interception.mouse_up
_orig_click = interception.click
_orig_key_down = interception.key_down
_orig_key_up = interception.key_up
_orig_press = interception.press
_orig_write = interception.write

def _mark_bot_active():
    global _last_bot_activity_tick
    _last_bot_activity_tick = ctypes.windll.kernel32.GetTickCount()

def _w_move_to(x, y):
    _mark_bot_active()
    import interception
    # Instead of sending an absolute packet (which fails on some touchpads/games),
    # we calculate the delta and send a relative packet!
    cx, cy = interception.mouse_position()
    dx = int(x) - cx
    dy = int(y) - cy
    if dx != 0 or dy != 0:
        interception.move_relative(dx, dy)
def _w_scroll(*a, **kw): _mark_bot_active(); return _orig_scroll(*a, **kw)
def _w_mouse_down(*a, **kw): _mark_bot_active(); return _orig_mouse_down(*a, **kw)
def _w_mouse_up(*a, **kw): _mark_bot_active(); return _orig_mouse_up(*a, **kw)
def _w_click(*a, **kw): _mark_bot_active(); return _orig_click(*a, **kw)
def _w_key_down(*a, **kw): _mark_bot_active(); return _orig_key_down(*a, **kw)
def _w_key_up(*a, **kw): _mark_bot_active(); return _orig_key_up(*a, **kw)
def _w_press(*a, **kw): _mark_bot_active(); return _orig_press(*a, **kw)
def _w_write(*a, **kw): _mark_bot_active(); return _orig_write(*a, **kw)

interception.move_to = _w_move_to
interception.scroll = _w_scroll
interception.mouse_down = _w_mouse_down
interception.mouse_up = _w_mouse_up
interception.click = _w_click
interception.key_down = _w_key_down
interception.key_up = _w_key_up
interception.press = _w_press
interception.write = _w_write

def _get_last_input_tick():
    """Return Windows tick count of the last keyboard or mouse input event."""
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
    return lii.dwTime

def mouse_killswitch_daemon():
    """
    Background thread that detects human input via GetLastInputInfo.
    """
    global _last_input_tick
    _last_input_tick = _get_last_input_tick()

    while True:
        time.sleep(0.04)

        if not _automation_active.is_set() or stop_automation_event.is_set():
            _last_input_tick = _get_last_input_tick()
            continue

        tick = _get_last_input_tick()
        if tick != _last_input_tick:
            diff = (tick - _last_bot_activity_tick) & 0xFFFFFFFF
            if diff > 0x7FFFFFFF:
                diff -= 0x100000000
                
            # If the Windows input event timestamp is more than 400ms away from
            # the bot's injection timestamp, it was definitely a human.
            if abs(diff) > 400:
                log('Human input detected. Yielding control.')
                stop_automation_event.set()
                try:
                    emergency_cleanup()
                except Exception:
                    pass
            _last_input_tick = tick

_injecting_key        = threading.Lock()

# ============================================================
# LOGGING
# ============================================================
def log(msg):
    try:
        stamp = time.strftime('%H:%M:%S')
        line  = f'[{stamp}] {msg}\n'
        with open(LOG_FILE, 'a') as f:
            f.write(line)
        print(line, end='')
    except Exception:
        pass



# ============================================================
# ESC HANDOFF  — double-tap ESC within 0.8s
# _injecting_key lock prevents our own interception calls
# from falsely triggering this (interception has NO injected flag)
# ============================================================
_last_esc_time = 0.0
_esc_tap_count = 0

def on_press(key):
    global _last_esc_time, _esc_tap_count
    if key == keyboard.Key.esc:
        if _injecting_key.locked():
            return
        if _automation_active.is_set():
            now = time.monotonic()
            if now - _last_esc_time <= 0.8:
                _esc_tap_count += 1
            else:
                _esc_tap_count = 1
            _last_esc_time = now
            if _esc_tap_count >= 2:
                _esc_tap_count = 0
                log('Double-ESC: yielding control to human...')
                emergency_cleanup()
                stop_automation_event.set()

listener = keyboard.Listener(on_press=on_press)
listener.daemon = True
listener.start()

# ============================================================
# INPUT SAFETY
# ============================================================
def emergency_cleanup():
    import interception
    for k in ('shift', 'ctrl', 'alt', 'win', 'enter', 'escape'):
        try:
            interception.key_up(k)
        except Exception:
            pass
    for btn in ('left', 'right'):
        try:
            interception.mouse_up(btn)
        except Exception:
            pass
    log('Input state cleaned. Human has control.')

def _safe_key_down(k):
    import interception
    with _injecting_key:
        interception.key_down(k)

def _safe_key_up(k):
    import interception
    with _injecting_key:
        interception.key_up(k)

def _safe_press(k):
    import interception
    with _injecting_key:
        interception.press(k)

def interception_hotkey(*keys):
    for k in keys:
        _safe_key_down(k)
    time.sleep(random.uniform(0.04, 0.09))
    for k in reversed(keys):
        _safe_key_up(k)

# ============================================================
# HUMAN MOUSE  — WindMouse physics
# Produces curved paths, natural overshoot, no straight lines
# ============================================================
def _wind_mouse_raw(sx, sy, ex, ey, move_fn, G=9, W=3, M=15, D=12):
    sqrt3 = math.sqrt(3)
    sqrt5 = math.sqrt(5)
    cx, cy = float(sx), float(sy)
    vx = vy = wx = wy = 0.0
    while True:
        dist = math.hypot(ex - cx, ey - cy)
        if dist < 1:
            break
        W_mag = min(W, dist)
        if dist >= D:
            wx = wx / sqrt3 + (2 * random.random() - 1) * W_mag / sqrt5
            wy = wy / sqrt3 + (2 * random.random() - 1) * W_mag / sqrt5
        else:
            wx /= sqrt3
            wy /= sqrt3
        vx += wx + G * (ex - cx) / dist
        vy += wy + G * (ey - cy) / dist
        v_mag = math.hypot(vx, vy)
        if v_mag > M:
            clip = M / 2 + random.random() * M / 2
            vx = vx / v_mag * clip
            vy = vy / v_mag * clip
        cx += vx
        cy += vy
        move_fn(int(round(cx)), int(round(cy)))

def human_mouse_move(tx, ty, duration=None):
    import interception
    global _bot_moving_mouse, _last_bot_mouse_pos
    if stop_automation_event.is_set():
        return
    _bot_moving_mouse = True
    try:
        sx, sy = get_mouse_pos()
        dist = math.hypot(tx - sx, ty - sy)
        if dist < 2:
            return
        if duration is None:
            duration = random.uniform(0.3, 1.0) * (dist / 900)
        steps = []
        _wind_mouse_raw(sx, sy, tx, ty, lambda x, y: steps.append((x, y)))
        if not steps:
            return
        step_delay = duration / max(len(steps), 1)
        
        for px, py in steps:
            if stop_automation_event.is_set():
                break
            interception.move_to(px, py)
            time.sleep(max(step_delay, 0.003))
            
        # 15% overshoot + correction
        if random.random() < 0.15 and not stop_automation_event.is_set():
            angle = random.uniform(0, 2 * math.pi)
            d = random.uniform(3, 14)
            ox, oy = int(tx + math.cos(angle) * d), int(ty + math.sin(angle) * d)
            interception.move_to(ox, oy)
            time.sleep(random.uniform(0.05, 0.13))
            if not stop_automation_event.is_set():
                interception.move_to(tx, ty)
    finally:
        _bot_moving_mouse = False
        try:
            _last_bot_mouse_pos = get_mouse_pos()
        except Exception:
            pass

def _screen_size():
    return (ctypes.windll.user32.GetSystemMetrics(0),
            ctypes.windll.user32.GetSystemMetrics(1))

def get_mouse_pos():
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return (pt.x, pt.y)

def random_mouse_drift(stop_event):
    """Move mouse to a random natural position (simulate looking at content)."""
    if stop_event.is_set():
        return
    sw, sh = _screen_size()
    human_mouse_move(
        random.randint(int(sw * 0.10), int(sw * 0.90)),
        random.randint(int(sh * 0.15), int(sh * 0.85)),
    )

def active_wait(wait_time, stop_event):
    """Wait for wait_time with subtle periodic cursor drift to register activity."""
    start = time.time()
    while time.time() - start < wait_time and not stop_event.is_set():
        remaining = wait_time - (time.time() - start)
        chunk = min(remaining, random.uniform(4.0, 8.0))
        if stop_event.wait(chunk):
            break
        if not stop_event.is_set():
            try:
                sx, sy = get_mouse_pos()
                sw, sh = _screen_size()
                nx = max(0, min(sw - 1, sx + random.randint(-15, 15)))
                ny = max(0, min(sh - 1, sy + random.randint(-15, 15)))
                human_mouse_move(nx, ny, duration=random.uniform(0.3, 0.8))
            except Exception:
                pass

# ============================================================
# HUMAN TYPING — burst-pause, bigrams, fatigue, QWERTY typos
# ============================================================
QWERTY_NEIGHBORS = {
    'a': 'sqzw', 'b': 'vghn', 'c': 'xdfv', 'd': 'serfcx',
    'e': 'wsdr', 'f': 'drtgvc', 'g': 'ftyhbv', 'h': 'gyujnb',
    'i': 'ujko', 'j': 'huikm', 'k': 'jiol', 'l': 'kop',
    'm': 'njk',  'n': 'bhjm', 'o': 'iklp', 'p': 'ol',
    'q': 'wa',   'r': 'edft', 's': 'qazxdew', 't': 'rfgy',
    'u': 'yhji', 'v': 'cfgb', 'w': 'qase', 'x': 'zsdc',
    'y': 'tghu', 'z': 'asx',
}
FAST_BIGRAMS = {'th', 'er', 'in', 'on', 'at', 'nd', 'st', 'es', 'en', 'of', 'to', 'it', 'is'}

def _press_char(char):
    import interception
    if char == '\n':
        _safe_press('enter')
    elif char == '\t':
        _safe_press('tab')
    elif char == '\b':
        _safe_press('backspace')
    else:
        with _injecting_key:
            interception.write(char)

def human_typing(text, stop_event, wpm=65):
    base_delay = 60.0 / (wpm * 5)
    burst_rem  = random.randint(4, 9)
    prev_char  = ''
    t0 = time.time()
    for i, char in enumerate(text):
        if stop_event.is_set():
            break
        burst_rem -= 1
        if burst_rem <= 0:
            burst_rem = random.randint(4, 9)
            pause = random.choices(
                [random.uniform(0.12, 0.40), random.uniform(0.55, 2.0)],
                weights=[0.75, 0.25]
            )[0]
            if stop_event.wait(pause):
                break
        fatigue     = 1.0 + min(0.30, (time.time() - t0) / 3600 * 0.30)
        pair        = (prev_char + char).lower()
        bigram_mult = 0.65 if pair in FAST_BIGRAMS else 1.0
        if (char.isalpha() and random.random() < 0.018
                and char.lower() in QWERTY_NEIGHBORS
                and not stop_event.is_set()):
            _press_char(random.choice(QWERTY_NEIGHBORS[char.lower()]))
            if stop_event.wait(max(0.05, random.gauss(0.18, 0.06))):
                break
            _safe_press('backspace')
            if stop_event.wait(random.uniform(0.05, 0.14)):
                break
        _press_char(char)
        prev_char = char
        delay = base_delay * fatigue * bigram_mult * random.gauss(1.0, 0.25)
        if stop_event.wait(max(0.008, delay)):
            break

# ============================================================
# CONTENT-AWARE SCROLL ENGINE
# Real reading-speed pacing based on content type
# ============================================================
#   Each entry: (notches_per_burst, pause_secs_range, backscroll_prob,
#                distraction_prob, distraction_pause_range)
SCROLL_PROFILES = {
    # notch_range, pause_range, back_prob, distract_prob, distract_range
    'reading':  ((1, 3), (2.5, 6.5),  0.10, 0.02, (6.0, 12.0)),
    'scanning': ((2, 5), (1.0, 3.5),  0.05, 0.01, (4.0, 8.0)),
    'novel':    ((1, 2), (3.5, 8.5),  0.12, 0.03, (8.0, 15.0)),
    'reddit':   ((2, 4), (2.0, 5.0),  0.08, 0.02, (5.0, 10.0)),
    'github':   ((1, 3), (2.0, 6.0),  0.08, 0.02, (5.0, 10.0)),
}

def human_scroll(direction, notches, stop_event):
    """Simulate realistic human scrolling with inertia/velocity curve."""
    import interception
    import time
    import random
    if stop_event.is_set(): return
    try:
        for i in range(notches):
            if stop_event.is_set(): break
            interception.scroll(direction)
            # ease-out curve for delay: starts fast (small delay), ends slow (large delay)
            # simulates a finger flick losing momentum
            progress = i / max(1, notches - 1) if notches > 1 else 1.0
            delay = 0.02 + 0.15 * (progress ** 2) + random.uniform(0.0, 0.03)
            time.sleep(delay)
    except Exception as e:
        log(f"Error in human_scroll: {e}")


def content_scroll_session(content_type, duration, stop_event):
    """Scroll at human reading speed for content_type over duration seconds."""
    if stop_event.is_set():
        return
    import interception
    sw, sh = _screen_size()
    human_mouse_move(sw // 2, sh // 2)
    notch_range, pause_range, back_prob, distract_prob, distract_range = \
        SCROLL_PROFILES.get(content_type, SCROLL_PROFILES['reading'])
    sw, sh = _screen_size()
    start = time.time()
    while time.time() - start < duration and not stop_event.is_set():
        # Scroll burst
        n = random.randint(*notch_range)
        human_scroll('down', n, stop_event)

        if stop_event.is_set():
            break

        pause = random.uniform(*pause_range)

        # Back-scroll: re-reading something
        if random.random() < back_prob:
            back_n = random.randint(1, 3)
            human_scroll('up', back_n, stop_event)
            pause *= random.uniform(1.2, 1.8)

        # Distraction pause (tabbed away / phone / lost focus)
        if random.random() < distract_prob:
            pause += random.uniform(*distract_range)

        if random.random() < 0.18 and not stop_event.is_set():
            random_mouse_drift(stop_event)

        active_wait(pause, stop_event)
        if stop_event.is_set():
            break

def shorts_scroll_session(duration, stop_event):
    """
    YouTube Shorts: watch each short 10-55 seconds, then snap-scroll to next.
    YouTube Shorts snaps to next video on ANY downward scroll — so 1-2 notches.
    """
    import interception
    sw, sh = _screen_size()
    human_mouse_move(sw // 2, sh // 2)
    start = time.time()
    while time.time() - start < duration and not stop_event.is_set():
        # Watch current short
        watch_time = random.uniform(8.0, 30.0)
        active_wait(watch_time, stop_event)
        if stop_event.is_set():
            break
        # Snap swipe down (1-2 notches is enough for Shorts snap)
        swipe = random.randint(1, 2)
        human_scroll('down', swipe, stop_event)
        # Next short loading gap
        if not stop_event.is_set():
            if stop_event.wait(random.uniform(0.8, 2.2)):
                break

# ============================================================
# WINDOW UTILITIES
# ============================================================
def get_foreground_title():
    hwnd   = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    if not length:
        return ''
    buf = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value

def wait_for_window(fragment, timeout=12.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if fragment.lower() in get_foreground_title().lower():
            return True
        time.sleep(0.3)
    return False

def focus_window_by_title(fragment):
    """Bring an already-open window matching fragment to foreground."""
    found = [False]
    def cb(hwnd, _):
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf    = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        if fragment.lower() in buf.value.lower():
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            current_thread = kernel32.GetCurrentThreadId()
            window_thread = user32.GetWindowThreadProcessId(hwnd, 0)
            foreground_window = user32.GetForegroundWindow()
            foreground_thread = user32.GetWindowThreadProcessId(foreground_window, 0) if foreground_window else 0

            if current_thread != window_thread:
                user32.AttachThreadInput(current_thread, window_thread, True)
            if foreground_thread and foreground_thread != window_thread:
                user32.AttachThreadInput(foreground_thread, window_thread, True)

            # Force foreground by toggling minimize/restore
            if not user32.IsIconic(hwnd):
                user32.ShowWindow(hwnd, 6) # SW_MINIMIZE
                time.sleep(0.05)
            user32.ShowWindow(hwnd, 9) # SW_RESTORE
            user32.SetForegroundWindow(hwnd)

            if current_thread != window_thread:
                user32.AttachThreadInput(current_thread, window_thread, False)
            if foreground_thread and foreground_thread != window_thread:
                user32.AttachThreadInput(foreground_thread, window_thread, False)
                
            found[0] = True
            return False
        return True
    Proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    ctypes.windll.user32.EnumWindows(Proc(cb), 0)
    if found[0]:
        return wait_for_window(fragment, timeout=3.0)
    return False

def maximize_active_window():
    if platform.system() == 'Windows':
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if hwnd and not ctypes.windll.user32.IsZoomed(hwnd):
            ctypes.windll.user32.ShowWindow(hwnd, 3) # SW_MAXIMIZE
            time.sleep(0.5)

def close_app_safely():
    interception_hotkey('alt', 'f4')
    time.sleep(random.uniform(0.7, 1.2))

def close_tab_safely():
    interception_hotkey('ctrl', 'w')
    time.sleep(random.uniform(0.7, 1.2))

# ============================================================
# APP LAUNCH
# ============================================================
def focus_or_open_firefox():
    """Focus existing Firefox window; open it if not running."""
    if focus_window_by_title('Mozilla Firefox'):
        return True
    # Not running — open via Run dialog
    import interception
    interception_hotkey('win', 'r')
    if not wait_for_window('Run', timeout=3.0):
        interception_hotkey('win', 'r')
        if not wait_for_window('Run', timeout=3.0):
            log('Warning: Run dialog did not appear or focus')
            return False
    time.sleep(random.uniform(0.1, 0.4))
    interception.write('firefox')
    time.sleep(0.35)
    _safe_press('enter')
    
    if not wait_for_window('Mozilla Firefox', timeout=15):
        log('Warning: Firefox window did not appear')
        return False
        
    time.sleep(random.uniform(1.0, 2.5))
    return True

def open_app_via_run(app_name):
    import interception
    interception_hotkey('win', 'r')
    if not wait_for_window('Run', timeout=3.0):
        interception_hotkey('win', 'r')
        if not wait_for_window('Run', timeout=3.0):
            log('Warning: Run dialog did not appear or focus')
            return False
    time.sleep(random.uniform(0.1, 0.4))
    human_typing(app_name, stop_automation_event, wpm=random.randint(60, 95))
    time.sleep(random.uniform(0.3, 0.6))
    _safe_press('enter')
    time.sleep(random.uniform(2.5, 4.5))
    return True

def _open_url(url, stop_event):
    """Open a new tab, navigate to url. Returns False if stopped."""
    interception_hotkey('ctrl', 't')
    time.sleep(random.uniform(0.35, 0.65))
    interception_hotkey('ctrl', 'l')
    time.sleep(random.uniform(0.20, 0.40))
    human_typing(url, stop_event, wpm=95)
    if stop_event.is_set():
        return False
    _safe_press('enter')
    time.sleep(random.uniform(2.5, 4.5))
    return True

# ============================================================
# TASKS
# ============================================================

def task_watch_shorts(duration, stop_event):
    log('Task: Watching YouTube Shorts on Firefox')
    if not focus_or_open_firefox(): return
    if stop_event.is_set(): return
    if not _open_url(SHORTS_URL, stop_event): return
    # Mute tab so audio doesn't play
    interception_hotkey('ctrl', 'm')
    time.sleep(random.uniform(1.5, 3.0))
    maximize_active_window()
    # Wait for first short to actually load
    time.sleep(random.uniform(2.0, 4.0))
    shorts_scroll_session(duration, stop_event)
    if not stop_event.is_set():
        close_tab_safely()

def task_read_wiki(duration, stop_event):
    log('Task: Reading Wikipedia on Firefox')
    if not focus_or_open_firefox(): return
    if stop_event.is_set(): return
    url = random.choice(WIKI_URLS)
    if not _open_url(url, stop_event): return
    maximize_active_window()
    # Extra load time for Wikipedia's images
    time.sleep(random.uniform(1.5, 3.0))

    start = time.time()
    # Read current article, occasionally jump to another random article
    while time.time() - start < duration and not stop_event.is_set():
        read_chunk = random.uniform(45.0, 90.0)   # read for 45-90s per article
        read_chunk = min(read_chunk, duration - (time.time() - start))
        if read_chunk <= 0: break
        content_scroll_session('reading', read_chunk, stop_event)
        if stop_event.is_set(): break
        # Navigate to another random article (stay on Wikipedia)
        if time.time() - start < duration - 30:
            interception_hotkey('ctrl', 'l')
            time.sleep(0.3)
            next_url = random.choice(WIKI_URLS)
            human_typing(next_url, stop_event, wpm=95)
            if stop_event.is_set(): break
            _safe_press('enter')
            time.sleep(random.uniform(2.0, 4.0))

    if not stop_event.is_set():
        close_tab_safely()

def task_browse_news(duration, stop_event):
    log('Task: Browsing Tech News on Firefox')
    if not focus_or_open_firefox(): return
    if stop_event.is_set(): return
    url = random.choice(TECH_NEWS_URLS)
    if not _open_url(url, stop_event): return
    maximize_active_window()
    time.sleep(random.uniform(1.0, 2.5))

    start = time.time()
    # Scan headlines on the homepage
    scan_time = random.uniform(40.0, 90.0)
    content_scroll_session('scanning', min(scan_time, duration), stop_event)

    # Mid-session: navigate to another news site
    if not stop_event.is_set() and (time.time() - start) < duration - 60:
        interception_hotkey('ctrl', 'l')
        time.sleep(0.3)
        next_url = random.choice(TECH_NEWS_URLS)
        human_typing(next_url, stop_event, wpm=95)
        if not stop_event.is_set():
            _safe_press('enter')
            time.sleep(random.uniform(2.0, 4.0))
            remaining = duration - (time.time() - start)
            if remaining > 0:
                content_scroll_session('scanning', remaining, stop_event)

    if not stop_event.is_set():
        close_tab_safely()

def task_read_novel(duration, stop_event):
    log('Task: Reading a Novel on Firefox')
    if not focus_or_open_firefox(): return
    if stop_event.is_set(): return
    url = random.choice(NOVEL_URLS)
    if not _open_url(url, stop_event): return
    time.sleep(random.uniform(2.0, 4.0))
    maximize_active_window()
    content_scroll_session('novel', duration, stop_event)
    if not stop_event.is_set():
        close_tab_safely()

def task_browse_reddit(duration, stop_event):
    log('Task: Browsing Reddit on Firefox')
    if not focus_or_open_firefox(): return
    if stop_event.is_set(): return
    url = random.choice(REDDIT_URLS)
    if not _open_url(url, stop_event): return
    maximize_active_window()
    time.sleep(random.uniform(1.5, 3.0))

    start = time.time()
    # Browse the feed
    chunk = random.uniform(90.0, 180.0)
    content_scroll_session('reddit', min(chunk, duration), stop_event)

    # Navigate to another subreddit partway through
    if not stop_event.is_set() and (time.time() - start) < duration - 45:
        interception_hotkey('ctrl', 'l')
        time.sleep(0.3)
        human_typing(random.choice(REDDIT_URLS), stop_event, wpm=90)
        if not stop_event.is_set():
            _safe_press('enter')
            time.sleep(random.uniform(2.0, 4.0))
            remaining = duration - (time.time() - start)
            if remaining > 0:
                content_scroll_session('reddit', remaining, stop_event)

    if not stop_event.is_set():
        close_tab_safely()

def task_browse_github(duration, stop_event):
    log('Task: Browsing GitHub Trending on Firefox')
    if not focus_or_open_firefox(): return
    if stop_event.is_set(): return
    url = random.choice(GITHUB_URLS)
    if not _open_url(url, stop_event): return
    maximize_active_window()
    time.sleep(random.uniform(1.0, 2.5))
    content_scroll_session('github', duration, stop_event)
    if not stop_event.is_set():
        close_tab_safely()

def task_view_task_manager(duration, stop_event):
    log('Task: Viewing Task Manager')
    if not open_app_via_run('taskmgr'): return
    if stop_event.is_set(): return
    if not wait_for_window('Task Manager', timeout=10):
        log('Warning: Task Manager did not appear in time')
        return
    time.sleep(1.0)
    maximize_active_window()

    sw, sh = _screen_size()
    tab_keys = ['ctrl', 'tab']   # cycle through Task Manager tabs
    start = time.time()
    tab_switch_at = time.time() + random.uniform(30.0, 90.0)

    while time.time() - start < duration and not stop_event.is_set():
        # Hover mouse over a random process row
        human_mouse_move(
            random.randint(int(sw * 0.15), int(sw * 0.85)),
            random.randint(int(sh * 0.25), int(sh * 0.80)),
        )
        # Occasionally scroll through the process list
        if random.random() < 0.35 and not stop_event.is_set():
            import interception
            human_scroll('down', random.randint(1, 4), stop_event)
            time.sleep(random.uniform(0.5, 1.5))
            human_scroll('up', random.randint(1, 3), stop_event)
        # Switch to a different Task Manager tab periodically
        if time.time() >= tab_switch_at and not stop_event.is_set():
            interception_hotkey(*tab_keys)
            tab_switch_at = time.time() + random.uniform(30.0, 90.0)
            time.sleep(0.8)
        if stop_event.wait(random.uniform(4.0, 14.0)):
            break

    if not stop_event.is_set():
        close_app_safely()

def task_type_essay(duration, stop_event):
    log('Task: Typing an Essay in Notepad')
    if not open_app_via_run('notepad'): return
    if stop_event.is_set(): return
    if not wait_for_window('Notepad', timeout=10):
        log('Warning: Notepad did not appear in time')
        return
    interception_hotkey('ctrl', 'n')
    time.sleep(random.uniform(0.8, 1.3))
    maximize_active_window()

    topic = random.choice(ESSAY_TOPICS)
    full_text = topic * 12   # ~1200-1500 words total

    start = time.time()
    human_typing(full_text, stop_event, wpm=random.randint(52, 72))

    # Fill remaining time staying in the document
    remaining = duration - (time.time() - start)
    wait_time = min(remaining, random.uniform(20.0, 115.0))
    if wait_time > 0 and not stop_event.is_set():
        active_wait(wait_time, stop_event)

    if not stop_event.is_set():
        interception_hotkey('ctrl', 'a')
        time.sleep(0.25)
        _safe_press('backspace')
        time.sleep(0.35)
        close_app_safely()

# ============================================================
# TASK SCHEDULER — weighted, anti-repeat
# ============================================================
TASK_WEIGHTS = {
    task_watch_shorts:      4,
    task_read_wiki:         3,
    task_browse_news:       3,
    task_browse_reddit:     3,
    task_read_novel:        2,
    task_browse_github:     2,
    task_type_essay:        1,
    task_view_task_manager: 1,
}

_last_task = None

def pick_next_task():
    global _last_task
    pool    = [t for t in TASK_WEIGHTS if t is not _last_task]
    weights = [TASK_WEIGHTS[t] for t in pool]
    chosen  = random.choices(pool, weights=weights, k=1)[0]
    _last_task = chosen
    return chosen

# ============================================================
# AUTOMATION SCHEDULER
# ============================================================
def automation_scheduler():
    stop_automation_event.clear()
    log('Idle threshold reached. Starting automation. (Double-tap ESC to yield)')
    start_time         = time.time()
    consecutive_errors = 0

    while not stop_automation_event.is_set():
        if time.time() - start_time > TOTAL_RUNTIME:
            log('10 hours elapsed. Stopping.')
            break

        task     = pick_next_task()
        dur      = random.randint(600, 900)
        log(f'Starting {task.__name__} for {dur//60}m {dur%60}s.')

        try:
            task(dur, stop_automation_event)
            consecutive_errors = 0
        except Exception as e:
            import traceback
            log(f'Error in {task.__name__}: {e}\n{traceback.format_exc()}')
            consecutive_errors += 1
            if consecutive_errors >= 3:
                log('3 consecutive errors. Pausing 5 min...')
                if stop_automation_event.wait(300):
                    break
                consecutive_errors = 0
            else:
                time.sleep(2.0)

        if stop_automation_event.is_set():
            break

        brk = random.randint(240, 300)
        log(f'Break: {brk//60}m {brk%60}s.')
        elapsed = 0.0
        while elapsed < brk:
            chunk = min(5.0, brk - elapsed)
            if stop_automation_event.wait(chunk):
                break
            elapsed += chunk

    _automation_active.clear()
    log('Automation ended. Monitoring for idle...')

# ============================================================
# IDLE MONITOR
# ============================================================
def monitor_idle():
    log(f'Script ready. Waiting for {IDLE_TIMEOUT}s idle. Double-tap ESC to stop automation.')
    while True:
        time.sleep(0.5)
        if not _automation_active.is_set() and not stop_automation_event.is_set():
            if get_idle_time_ms() >= IDLE_TIMEOUT * 1000:
                stop_automation_event.clear()
                _automation_active.set()
                threading.Thread(target=automation_scheduler, daemon=True).start()

# ============================================================
# ENTRY POINT
# ============================================================
def _bind_to_interactive_desktop():
    """
    Ensure this process/thread is attached to the interactive input desktop.
    Fixes GetCursorPos 'Access Denied' (error 5) when launched from a sandboxed
    or non-default desktop context (e.g. ExeBox, RunAs, scheduled tasks).
    """
    GENERIC_ALL = 0x10000000
    desk = ctypes.windll.user32.OpenInputDesktop(0, False, GENERIC_ALL)
    if desk:
        ctypes.windll.user32.SetThreadDesktop(desk)
        ctypes.windll.user32.CloseDesktop(desk)

def main():
    import interception
    _bind_to_interactive_desktop()
    interception.auto_capture_devices()
    threading.Thread(target=mouse_killswitch_daemon, daemon=True).start()
    try:
        monitor_idle()
    except KeyboardInterrupt:
        log('Terminated manually.')
        emergency_cleanup()

if __name__ == '__main__':
    main()
