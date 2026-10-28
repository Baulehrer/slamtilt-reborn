#!/usr/bin/env python3
"""Replay complete original upper capture fixtures without an emulator."""
import argparse,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--probe',required=True);p.add_argument('--fixtures',type=Path,required=True);a=p.parse_args()
for variant,name in enumerate(['mean-upper-original-cycle','mean-upper-second-original-cycle','mean-upper-third-original-cycle']):
 expected=json.loads((a.fixtures/(name+'.json')).read_text());actual=json.loads(subprocess.check_output([a.probe,*(['variant']*variant)],text=True))
 assert len(actual)==len(expected),(name,len(actual),len(expected))
 differences=[i for i,(x,y) in enumerate(zip(actual,expected)) if x!=y]
 assert not differences,(name,differences[:5],{k:(actual[differences[0]][k],expected[differences[0]][k]) for k in expected[0] if actual[differences[0]][k]!=expected[differences[0]][k]})
 print(json.dumps(dict(fixture=name,steps=len(actual),differences=0)))

for selected in [1,2]:
 name=f"mean-upper-selected{selected}-original-cycle"
 expected=json.loads((a.fixtures/(name+".json")).read_text());actual=json.loads(subprocess.check_output([a.probe,f"selected{selected}"],text=True))
 assert actual==expected,(name,len(actual),len(expected))
 print(json.dumps(dict(fixture=name,steps=len(actual),differences=0)))
