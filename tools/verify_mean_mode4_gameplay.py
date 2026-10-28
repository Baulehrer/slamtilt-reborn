#!/usr/bin/env python3
"""Native composition regression; component oracles establish original boundaries."""
import json, subprocess, sys, hashlib
from pathlib import Path
root = Path(__file__).resolve().parents[1]
dat = next((root / 'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
probe = sys.argv[1]
def run(seed, steps=12000, summary=True):
    args = [probe, str(dat), str(root/'build/mean-prepared'),
            str(root/'analysis/traces/mean-flight-100.json'), str(steps), 'mode4', str(seed)]
    if summary:
        args += ['summary']
    return json.loads(subprocess.check_output(args, text=True))
scenarios = [run(seed) for seed in range(4)]
for a in scenarios:
    assert a['active'] and a['states'] == 12001
    assert a['mode4_starts'] == 1 and a['mode4_completions'] == 1
    assert a['state7_steps'] == 18 and a['pending_mode4_rewards'] == 0
assert run(0) == scenarios[0], 'Non-deterministic native mode4 composition'
trace = run(0, 1200, False)
# Keep the visible guided section as a compact native trace, not an original oracle.
samples = trace['samples'] if 'samples' in trace else trace['states']
guided = [s for s in samples if s['state'] == 7]
assert len(guided) == 18 and len({(s['x'], s['y']) for s in guided}) > 5
keys = ['active','states','mode4_starts','mode4_completions','state7_steps','score','table_mode']
report = dict(scope='Native-only composed synthetic input; original trajectory equivalence unverified',
              image_sha256=hashlib.sha256((root/'build/mean-prepared/pe-data.bin').read_bytes()).hexdigest(),
              scenarios=[{k:a[k] for k in keys if k in a} for a in scenarios], guided=guided)
(root/'analysis/traces/mean-mode4-native-cycle.json').write_text(json.dumps(report, indent=2)+'\n')
print('PASS four12000-step mode4 cycles,18guidedsteps each,deterministic repeat')
