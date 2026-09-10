#!/usr/bin/env python3
"""Open/focus a real Hyprland window running a coding agent's CLI for one local agent
slot (A-018). Never a hidden background job: the window is the same one Alex would get
launching and pasting the handoff prompt into a terminal himself. Delegates the actual
launch-or-focus matching to Omarchy's own omarchy-launch-or-focus-tui, the same primitive
the rest of the desktop uses for this pattern (see ADR-023's open_app_by_name)."""
import argparse
import fcntl
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'actions'))
from core import hypr, dispatch

# One real CLI per known agent kind; 'human' has no process for Jarvis to launch —
# a human slot means Alex works it himself in his own terminal.
AGENT_COMMANDS = {'claude-code': ['claude'], 'cursor': ['codex']}


def app_id(slot_id):
    return 'jarvis-agent-' + slot_id


def is_agent_window(client, target_app_id):
    return target_app_id in (client.get('class') or '')


def open_agent(slot_id, kind):
    if not re.fullmatch(r'slot-[0-9a-f]{1,60}', slot_id):
        raise ValueError('Invalid agent slot id')
    command = AGENT_COMMANDS.get(kind)
    if not command:
        raise ValueError('Human slots are worked in your own terminal; there is nothing for Jarvis to open.')
    with urlopen('http://127.0.0.1:7421/health', timeout=2) as response:
        if json.load(response).get('service') != 'omarchy-jarvis':
            raise RuntimeError('Start Jarvis before opening an agent window')
    target = app_id(slot_id)
    existing = next((c for c in hypr('clients') if is_agent_window(c, target)), None)
    if existing:
        dispatch('focuswindow', 'address:' + existing['address'])
        return
    (ROOT / 'logs/agent-windows').mkdir(exist_ok=True, mode=0o700, parents=True)
    with (ROOT / f'logs/agent-windows/{slot_id}.lock').open('w') as lock:
        # A second click before the window appears must not spawn a second one.
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with (ROOT / f'logs/agent-windows/{slot_id}.log').open('a') as out:
            subprocess.Popen(['omarchy-launch-or-focus-tui', '--app-id=' + target, *command],
                              stdout=out, stderr=out, start_new_session=True)
        for _ in range(75):
            client = next((c for c in hypr('clients') if is_agent_window(c, target)), None)
            if client:
                dispatch('focuswindow', 'address:' + client['address'])
                return
            time.sleep(.1)
    raise RuntimeError(f'Agent window did not appear; inspect logs/agent-windows/{slot_id}.log')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--slot-id', required=True)
    parser.add_argument('--kind', required=True)
    args = parser.parse_args()
    try:
        open_agent(args.slot_id, args.kind)
    except Exception as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
