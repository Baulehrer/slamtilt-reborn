#!/usr/bin/env python3
"""Stop inside a renderer batch, preserving exactly37original simulation steps."""
import json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
work=ROOT/'build/oracle/pirate-full-realtime';work.mkdir(parents=True,exist_ok=True)
out=work/'stop37.json';timing=work/'stop37-timing.json'
subprocess.run([ROOT/'tools/slampirate','--data',ROOT/'build/imported/pirate-retail','--realtime-steps','37',
    '--replay',ROOT/'analysis/traces/pirate-natural-crocodile-game.json','--no-audio','--full-state-trace','--trace-output',out,'--timing-output',timing],
    check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'),timeout=10)
t=json.loads(out.read_text());g=json.loads((ROOT/'build/oracle/pirate-modes/natural-crocodile-game/trace.json').read_text())
assert not t['error']and t['tick_count']==37
for key in ['states','timing','lifecycle','dmd_sha256','highscore_sha256','lamp_sha256','rule_sha256','video_sha256','ball_pool_sha256']:
    assert t[key]==g[key][:38 if key=='states' else 37],key
assert json.loads(timing.read_text())['frames'][-1][5]==37
print('Exact37realtime steps/original prefix PASS;no4step rounding orovershoot')
