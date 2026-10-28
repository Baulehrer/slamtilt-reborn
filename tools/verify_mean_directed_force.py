#!/usr/bin/env python3
"""Compare native directed acceleration against saved original x86 fixtures."""
import json
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
source = json.loads((ROOT / 'analysis/mean-directed-force.json').read_text())
cases = [{'operation': 'free', 'bytes': list(bytes.fromhex(f['initial_bytes']))}
         for f in source['fixtures']]
path = ROOT / 'build/oracle/directed-force-cases.json'
path.write_text(json.dumps(cases))
result = json.loads(subprocess.check_output([
    str(ROOT / 'build/native/mean_probe'), str(path),
    str(ROOT / 'build/mean-prepared/lookup.bin'),
    str(ROOT / 'build/mean-prepared/pe-data.bin')], text=True))
assert len(result) == len(cases)
differences = [i for i, (actual, fixture) in enumerate(zip(result, source['fixtures']))
               if bytes(actual).hex() != fixture['final_bytes']]
report = dict(build_sha256=source['build_sha256'], cases=len(cases),
              differences=differences, scope='All100 ball bytes vs saved original409e18 fixtures')
(ROOT / 'analysis/traces/mean-directed-force-validation.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report))
assert not differences
