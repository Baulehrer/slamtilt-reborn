#!/usr/bin/env python3
"""Exercise actual SDL Left-special dispatch and its event-admission gates."""
import json
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
viewer = Path(sys.argv[1]).resolve()
dat = root / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT'
prepared = root / 'build/oracle/pirate-full-tick'
output = root / 'build/oracle/pirate-special-frontend.json'
trace = root / 'build/oracle/pirate-special-frontend-trace.json'
env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy')
subprocess.run([str(viewer), str(dat), '--pirate-play', str(prepared),
                '--frames', '14', '--no-audio', '--special-acceptance', str(output),
                '--trace-output', str(trace)], check=True, env=env)
calls = json.loads(output.read_text())
expected = [dict(frame=frame, scancode=scan, accepted=True)
            for frame, scan in [(1, 224), (5, 224), (7, 224),
                                (9, 224), (11, 224), (12, 29)]]
assert calls == expected, calls
state = json.loads(trace.read_text())
assert state.get('error', '') == '', state.get('error')
assert state['tick_count'] == 40, state['tick_count']
print('PASS actual SDL Left-special default/remapped key dispatch; repeat, key-up, '
      'focus, pause, options, minimize and unbound Right Ctrl gates')
