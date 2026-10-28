#!/usr/bin/env python3
"""Frozen original408110 lamp command clock versus native consumer."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
probe=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build/native/mean_lamp_clock_probe'
f=json.loads((ROOT/'analysis/traces/mean-lamp-clock-fixture.json').read_text())
actual=json.loads(subprocess.check_output([str(probe)],input=json.dumps(f).encode()))
expected=[c['steps'] for c in f['cases']]
assert len(actual)==len(expected)
assert actual==expected,[(i,a,e) for i,(a,e) in enumerate(zip(actual,expected)) if a!=e][:1]
print(json.dumps(dict(cases=len(expected),states=sum(map(len,expected)),differences=0)))
