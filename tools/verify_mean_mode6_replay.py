#!/usr/bin/env python3
"""Frozen original entry and capture boundary states against native code."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
probe=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build/native/mean_mode6_probe'
total=0
for kind,name in [('entry','mean-mode6-entry-original.json'),('capture','mean-mode6-capture-fixture.json'),('clock','mean-mode6-clock-fixture.json')]:
 fixture=json.loads((ROOT/'analysis/traces'/name).read_text());cases=fixture['cases']
 actual=json.loads(subprocess.check_output([str(probe)],input=json.dumps(dict(kind=kind,cases=cases)).encode()))
 expected=[c['final'] if kind=='entry' else c['output'] if kind=='clock' else {k:c[k] for k in ['output','calls']} for c in cases]
 assert len(actual)==len(expected)
 assert actual==expected,[(i,a,e) for i,(a,e) in enumerate(zip(actual,expected)) if a!=e][:1]
 total+=len(cases)
fixture=json.loads((ROOT/'analysis/traces/mean-mode6-display-fixture.json').read_text())
expected=fixture['states']
actual=json.loads(subprocess.check_output([str(probe)],input=json.dumps(dict(kind='display',ticks=len(expected))).encode()))
assert actual==expected,[(i,a,e) for i,(a,e) in enumerate(zip(actual,expected)) if a!=e][:1]
print(json.dumps(dict(verified_cases=total,display_ticks=len(expected),differences=0)))
