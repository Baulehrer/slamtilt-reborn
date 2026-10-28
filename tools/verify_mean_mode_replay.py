#!/usr/bin/env python3
"""Replay frozen original mode-island cases without emulator dependencies."""
import argparse,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--probe',required=True);p.add_argument('--fixture',type=Path,required=True);a=p.parse_args()
f=json.loads(a.fixture.read_text());actual=json.loads(subprocess.check_output([a.probe],input=json.dumps(f['cases']),text=True))
assert actual==f['expected'],'Native mode island differs from original fixture'
print(json.dumps(dict(original_cases=len(actual),differences=0)))
