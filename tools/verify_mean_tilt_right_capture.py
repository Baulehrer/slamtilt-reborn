#!/usr/bin/env python3
"""Actual4164e1 callback4 service1c transfer then continuation; seeded context."""
import json,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
exec((ROOT/'tools/verify_mean_mode4_right_entry.py').read_text().split("for kind in ['ramp','capture']:")[0])
for mode in [1,2,3,4]:
 for timer in [-1,0,1]:
  for armed in [0,-1]:
   for slot80 in [[-1,3,1],[-1,1,0]]:
    for busy in [False,True]:
     for blocked in [0,3]:
      for b40 in [0,1]:
       raw=bytearray(base)
       for o,v in [(0x392,0),(0x3a2,armed),(0x370,timer),(0x3b8,5)]:struct.pack_into('<h',raw,o,v)
       struct.pack_into('<I',raw,0x038,0)
       ball=bytearray(100);struct.pack_into('<ii',ball,0,280<<16,285<<16);struct.pack_into('<HH',ball,0x58,3,4)
       case=dict(kind='capture',raw=list(raw),mode=mode,ball=list(ball),slot80=slot80,slot3=[0 if busy else -1,100,0],b38=10,b40=b40,blocked=blocked,services_1c=True)
       put(0x100201c,1)
       run(case,0x4164e1)
actual=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases).encode()))
assert len(actual)==len(expected)
for i,(a,b) in enumerate(zip(actual,expected)):
 if a!=b:
  print('FAIL',i,{k:(a[k],b[k]) for k in a if a[k]!=b[k]},cases[i]);raise SystemExit(1)
report=dict(scope=__doc__,cases=len(cases),differences=0,records=[dict(input=c,output=e) for c,e in zip(cases,expected)])
(ROOT/'analysis/traces/mean-tilt-right-capture-original.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
print('PASS',len(cases),'cases')
