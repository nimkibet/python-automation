import time
import os
from config.settings import LOG_FILE

def log(msg):
    try:
        stamp = time.strftime('%H:%M:%S')
        line  = f'[{stamp}] {msg}\n'
        with open(LOG_FILE, 'a') as f:
            f.write(line)
        print(line, end='', flush=True)
    except Exception:
        pass
