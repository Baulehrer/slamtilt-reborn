#!/usr/bin/env python3
"""Replay original mode-entry sentinels without an emulator dependency."""
import argparse,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--probe',required=True);p.add_argument('--fixture',type=Path,required=True);a=p.parse_args()
f=json.loads(a.fixture.read_text());actual=json.loads(subprocess.check_output([a.probe],text=True))
assert actual==f['expected'],'Native mode entry differs from original'
print(json.dumps(dict(original_cases=len(actual),differences=0)))
