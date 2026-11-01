#!/usr/bin/env python3
"""Compare a tracker module across two libraries with an explicit mix mode."""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--probe', type=Path, required=True)
p.add_argument('--baseline', type=Path, required=True)
p.add_argument('--fixed', type=Path, required=True)
p.add_argument('--module', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--mode', choices=('retail', 'default'), default='retail')
a = p.parse_args()
outputs = []
for library in (a.baseline.absolute(), a.fixed.absolute()):
    env = dict(os.environ, LD_LIBRARY_PATH=str(library.parent))
    linked = subprocess.check_output(['ldd', str(a.probe.resolve())], env=env, text=True)
    assert str(library) in linked
    cmd = [str(a.probe.resolve()), str(a.module.resolve()), '88200', '137', 'restart', '0']
    if a.mode == 'retail': cmd.append('retail')
    outputs.append(subprocess.check_output(cmd, env=env))
assert len(outputs[0]) == 88200 * 4 and outputs[0] == outputs[1]
report = {'status': 'VERIFIED_BOUNDED', 'scope': __doc__, 'frames': 88200, 'mix_mode': a.mode,
          'module_sha256': hashlib.sha256(a.module.read_bytes()).hexdigest(),
          'pcm_sha256': hashlib.sha256(outputs[0]).hexdigest(), 'equal': True}
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps(report, indent=2) + '\n')
print(f'PASS: module unchanged over 88200 frames in {a.mode} mode')
