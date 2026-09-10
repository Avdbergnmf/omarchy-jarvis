#!/usr/bin/env python3
"""Open/focus Training independently; never toggle chat or restart shared services."""
import fcntl
import json
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'actions'))
from core import hypr, dispatch


def is_training(client):
    return 'jarvis-training' in (client.get('class') or '')


def open_training():
    with urlopen('http://127.0.0.1:7421/health', timeout=2) as response:
        if json.load(response).get('service') != 'omarchy-jarvis':
            raise RuntimeError('Start Jarvis before opening Training')
    (ROOT/'logs').mkdir(exist_ok=True, mode=0o700)
    with (ROOT/'logs/training-window.lock').open('w') as lock:
        # A second click must not leave a second launcher waiting indefinitely.
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        existing = next((c for c in hypr('clients') if is_training(c)), None)
        if existing:
            dispatch('focuswindow', 'address:'+existing['address'])
            return
        with (ROOT/'logs/training-window.log').open('a') as out:
            subprocess.Popen(['chromium', '--user-data-dir='+str(ROOT/'logs/training-profile'),
                              '--class=jarvis-training', '--no-first-run', '--disable-extensions',
                              '--disable-background-networking', '--no-default-browser-check',
                              '--disable-background-mode', '--app=http://127.0.0.1:7421/jarvis-training',
                              '--window-size=1180,820'], stdout=out, stderr=out, start_new_session=True)
        for _ in range(75):
            client = next((c for c in hypr('clients') if is_training(c)), None)
            if client:
                window = json.dumps('address:'+client['address'])
                # Address every operation; never float/resize the user's focused window.
                if not client.get('floating'):
                    subprocess.run(['hyprctl', 'dispatch', 'hl.dsp.window.float({ window = '+window+', action = "toggle" })'], check=True, capture_output=True, timeout=2)
                subprocess.run(['hyprctl', 'dispatch', 'hl.dsp.window.center({ window = '+window+' })'], check=True, capture_output=True, timeout=2)
                dispatch('focuswindow', 'address:'+client['address'])
                return
            time.sleep(.1)
        raise RuntimeError('Training window did not appear; inspect logs/training-window.log')


if __name__ == '__main__':
    try:
        open_training()
    except Exception as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
