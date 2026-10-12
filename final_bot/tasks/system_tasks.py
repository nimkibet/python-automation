import time
import random
from core import state
from core.logger import log
from core.input_driver import hotkey, safe_press, safe_mouse_down, safe_mouse_up, safe_move_to
from core.human_physics import human_typing, human_mouse_move, active_wait, content_scroll_session, human_scroll, _screen_size
from core.window_manager import maximize_active_window, close_app_safely, wait_for_window, focus_window_by_title
from tasks.shared import open_app_via_run
from config.settings import ESSAY_TOPICS

def task_view_task_manager(duration):
    log('Task: Viewing Task Manager')
    open_app_via_run('taskmgr')
    if state.is_stopped(): return
    if not wait_for_window('Task Manager', timeout=10):
        log('Verification Failed: Task Manager window not detected, aborting safely.')
        return
    focus_window_by_title('Task Manager')
    time.sleep(0.5)
    time.sleep(1.0)
    maximize_active_window()

    sw, sh = _screen_size()
    start = time.time()
    next_tab_switch = time.time() + random.uniform(25.0, 70.0)

    while time.time() - start < duration and not state.is_stopped():
        human_mouse_move(
            random.randint(int(sw * 0.15), int(sw * 0.85)),
            random.randint(int(sh * 0.25), int(sh * 0.80)),
        )
        if random.random() < 0.35 and not state.is_stopped():
            human_scroll('down', random.randint(1, 4))
            time.sleep(random.uniform(0.5, 1.5))
            human_scroll('up', random.randint(1, 3))
        if time.time() >= next_tab_switch and not state.is_stopped():
            hotkey('ctrl', 'tab')
            next_tab_switch = time.time() + random.uniform(25.0, 70.0)
            time.sleep(0.8)
        if state.stop_automation_event.wait(random.uniform(4.0, 14.0)):
            break

    if not state.is_stopped():
        close_app_safely()

def task_type_essay(duration):
    log('Task: Typing an Essay in Notepad')
    open_app_via_run('notepad')
    if state.is_stopped(): return
    if not wait_for_window('Notepad', timeout=10):
        log('Verification Failed: Notepad window not detected, aborting safely.')
        return
    focus_window_by_title('Notepad')
    time.sleep(0.5)
    
    # In newer windows, notepad might open a new tab instead of a fresh window
    hotkey('ctrl', 'n')
    time.sleep(random.uniform(0.8, 1.3))
    maximize_active_window()

    topic = random.choice(ESSAY_TOPICS)
    full_text = topic * 12

    start = time.time()
    try:
        human_typing(full_text, wpm=random.randint(52, 72))
    except Exception as e:
        log(f"Error during typing: {e}")

    remaining = duration - (time.time() - start)
    wait_time = min(remaining, random.uniform(20.0, 115.0))
    if wait_time > 0 and not state.is_stopped():
        active_wait(wait_time)

    if not state.is_stopped():
        hotkey('ctrl', 'a')
        time.sleep(0.25)
        safe_press('backspace')
        time.sleep(0.35)
        close_app_safely()

def task_terminal_ops(duration):
    log('Task: Running Terminal Commands')
    open_app_via_run('cmd')
    if state.is_stopped(): return
    
    # Verification: cmd window title varies
    if not wait_for_window(['Command Prompt', 'cmd.exe'], timeout=8):
        log('Verification Failed: cmd window did not appear. Aborting task safely.')
        return
        
    focus_window_by_title(['Command Prompt', 'cmd.exe'])
    time.sleep(0.5)
    time.sleep(random.uniform(0.8, 1.5))
    maximize_active_window()

    all_commands = [
        'dir /s /b', 'echo.', 'systeminfo | findstr /i "OS"', 'ping 8.8.8.8 -n 10',
        'netstat -an | findstr ESTABLISHED', 'ipconfig', 'tasklist | findstr "chrome brave firefox"',
        'wmic cpu get name', 'wmic memorychip get capacity', 'wmic diskdrive get model',
        'echo %USERNAME%', 'dir %USERPROFILE%\\Documents'
    ]
    start = time.time()
    used = []

    while time.time() - start < duration and not state.is_stopped():
        remaining_cmds = [c for c in all_commands if c not in used]
        if not remaining_cmds:
            used = []
            remaining_cmds = all_commands[:]
        cmd = random.choice(remaining_cmds)
        used.append(cmd)

        if random.random() < 0.2 and not state.is_stopped():
            safe_press('up')
            time.sleep(random.uniform(0.4, 0.9))
            hotkey('ctrl', 'a')
            time.sleep(0.2)

        try:
            human_typing(cmd, wpm=random.randint(55, 80))
            if state.is_stopped(): break
            safe_press('enter')
        except Exception as e:
            log(f"Error executing command {cmd}: {e}")

        wait_time = random.uniform(5.0, 20.0)
        active_wait(max(0, min(wait_time, duration - (time.time() - start))))

    if not state.is_stopped():
        try:
            human_typing('exit')
            safe_press('enter')
            time.sleep(0.5)
        except Exception:
            pass

def task_ms_paint(duration):
    log('Task: Drawing in MS Paint')
    open_app_via_run('mspaint')
    if state.is_stopped(): return
    
    # Verification: Paint window title is usually "Untitled - Paint"
    if not wait_for_window(['Paint', 'Untitled'], timeout=8):
        log('Verification Warning: Paint window title match failed, proceeding anyway to attempt draw.')
    focus_window_by_title(['Paint', 'Untitled'])
    time.sleep(0.5)
        
    time.sleep(random.uniform(1.5, 2.5))
    maximize_active_window()

    sw, sh = _screen_size()
    
    # Verification Panel: Center canvas click to guarantee focus
    log("Verification: Clicking center of MS Paint to guarantee canvas focus.")
    human_mouse_move(sw // 2, sh // 2)
    safe_mouse_down('left')
    time.sleep(0.1)
    safe_mouse_up('left')
    time.sleep(0.5)

    cx_min, cx_max = 80,  sw - 60
    cy_min, cy_max = 120, sh - 40

    start = time.time()
    stroke_count = 0

    while time.time() - start < duration and not state.is_stopped():
        pattern = random.choice(['freehand', 'arc', 'zigzag'])

        try:
            if pattern == 'freehand':
                x = random.randint(cx_min, cx_max)
                y = random.randint(cy_min, cy_max)
                human_mouse_move(x, y)
                if state.is_stopped(): break
                safe_mouse_down('left')
                points = random.randint(3, 8)
                for _ in range(points):
                    if state.is_stopped(): break
                    dx = random.randint(-200, 200)
                    dy = random.randint(-150, 150)
                    nx = max(cx_min, min(cx_max, x + dx))
                    ny = max(cy_min, min(cy_max, y + dy))
                    human_mouse_move(nx, ny, duration=random.uniform(0.4, 1.2))
                    x, y = nx, ny
                safe_mouse_up('left')

            elif pattern == 'arc':
                x1 = random.randint(cx_min, cx_max)
                y1 = random.randint(cy_min, cy_max)
                x2 = max(cx_min, min(cx_max, x1 + random.randint(-350, 350)))
                y2 = max(cy_min, min(cy_max, y1 + random.randint(-250, 250)))
                human_mouse_move(x1, y1)
                if state.is_stopped(): break
                safe_mouse_down('left')
                human_mouse_move(x2, y2, duration=random.uniform(0.8, 2.0))
                safe_mouse_up('left')

            elif pattern == 'zigzag':
                x = random.randint(cx_min + 100, cx_max - 100)
                y = random.randint(cy_min + 50,  cy_max - 50)
                human_mouse_move(x, y)
                if state.is_stopped(): break
                safe_mouse_down('left')
                for seg in range(random.randint(4, 10)):
                    if state.is_stopped(): break
                    x += random.randint(30, 80)
                    y += random.randint(-60, 60) * (1 if seg % 2 == 0 else -1)
                    x = max(cx_min, min(cx_max, x))
                    y = max(cy_min, min(cy_max, y))
                    safe_move_to(x, y)
                    time.sleep(random.uniform(0.04, 0.12))
                safe_mouse_up('left')
        except Exception as e:
            log(f"Error drawing in Paint: {e}")
            safe_mouse_up('left') # recover mouse state safely

        stroke_count += 1
        active_wait(random.uniform(0.8, 4.0))
        if state.is_stopped():
            break

        if stroke_count % random.randint(3, 7) == 0 and not state.is_stopped():
            human_mouse_move(
                random.randint(cx_min, cx_max),
                random.randint(cy_min, cy_max),
            )
            if state.stop_automation_event.wait(random.uniform(0.5, 1.5)): break

    if not state.is_stopped():
        close_app_safely()
        time.sleep(0.8)
        # Handle "Do you want to save changes?"
        hotkey('right')
        time.sleep(0.3)
        safe_press('enter')

def open_vscode():
    if state.is_stopped(): return False

    if focus_window_by_title('Visual Studio Code'):
        log('Verification: VS Code focused successfully.')
        time.sleep(random.uniform(1.5, 2.5))
        return True

    log('Verification: Opening VS Code via Start Search.')
    hotkey('win')
    time.sleep(random.uniform(0.85, 1.2))
    human_typing('visual studio code', wpm=random.randint(60, 90))
    time.sleep(random.uniform(1.2, 2.0))
    safe_press('enter')
    
    if wait_for_window('Visual Studio Code', timeout=22):
        log('Verification Success: VS Code opened successfully.')
        focus_window_by_title('Visual Studio Code')
        time.sleep(0.5)
        time.sleep(random.uniform(2.0, 3.5))
        return True

    log('Verification Failed: VS Code did not open — skipping task safely.')
    return False

def task_code_vscode(duration):
    log('Task: Coding session in VS Code')
    if not open_vscode():
        return
    if state.is_stopped(): return

    hotkey('ctrl', 'n')
    time.sleep(random.uniform(0.8, 1.4))
    maximize_active_window()

    # Simple python template for now (in full version import CODE_TEMPLATES)
    lines = [
        "import os",
        "import json",
        "",
        "def main():",
        "\tprint('Hello world')",
        "",
        "if __name__ == '__main__':",
        "\tmain()"
    ]
    
    start = time.time()
    save_interval = random.randint(3, 6)

    try:
        for line_idx, line in enumerate(lines):
            if state.is_stopped() or time.time() - start >= duration:
                break

            stripped = line.strip()
            if stripped.startswith(('class ', 'def ')):
                if state.stop_automation_event.wait(random.uniform(0.6, 2.8)): break
            elif stripped == '':
                if random.random() < 0.4:
                    if state.stop_automation_event.wait(random.uniform(0.2, 1.0)): break

            tab_count = len(line) - len(line.lstrip('\t'))
            for _ in range(tab_count):
                if state.is_stopped(): break
                safe_press('tab')
                time.sleep(random.uniform(0.03, 0.08))

            content = line.lstrip('\t')
            if content and not state.is_stopped():
                human_typing(content, wpm=random.randint(60, 95))

            if state.is_stopped(): break
            safe_press('enter')

            if state.stop_automation_event.wait(random.uniform(0.15, 1.1)): break

            if line_idx > 0 and line_idx % save_interval == 0 and not state.is_stopped():
                hotkey('ctrl', 's')
                save_interval = random.randint(3, 6)
                time.sleep(random.uniform(0.3, 0.7))

        if not state.is_stopped():
            hotkey('ctrl', 's')
            time.sleep(0.6)

        remaining = duration - (time.time() - start)
        if remaining > 15 and not state.is_stopped():
            hotkey('ctrl', 'home')
            time.sleep(0.5)
            content_scroll_session('code', remaining - 5)

    except Exception as e:
        log(f"Error during VS Code session: {e}")

    if not state.is_stopped():
        close_app_safely()
