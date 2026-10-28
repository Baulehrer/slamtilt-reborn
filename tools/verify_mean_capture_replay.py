#!/usr/bin/env python3
"""Replay frozen original capture callbacks without an emulator dependency."""
import argparse,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--probe',required=True);p.add_argument('--fixture',type=Path,required=True);a=p.parse_args()
fixture=json.loads(a.fixture.read_text())
cases=fixture['cases'] if isinstance(fixture,dict) else [{'initial':{'ball':fixture[0]['ball']},'expected':fixture}]
steps=0
for case in cases:
 actual=json.loads(subprocess.check_output([a.probe],input=json.dumps(case['initial']),text=True))
 assert actual==case['expected'],'Native capture callback diverges from original fixture'
 steps+=len(actual)
print(json.dumps(dict(original_callback_steps=steps,differences=0)))
