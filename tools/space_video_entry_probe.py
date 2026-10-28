#!/usr/bin/env python3
"""Observe the first missing video entry in original execution, not native guesses."""
import json
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from pirate_adventure_oracle import Original,ROOT
from space_asteroid_oracle import Chain
m=Original(ROOT/'build/oracle/space-full-game',table='space');t=json.loads((ROOT/'build/oracle/space-modes/planet-rewards.json').read_text());seen=[];tick=0

def observe(u,a,size,data):
 target=m.get(u.reg_read(UC_X86_REG_ESP));seen.append(dict(tick=tick+1,callsite=hex(a),target=hex(target),return_address='0x44551d',opcode=bytes(u.mem_read(a,size)).hex()))
m.u.hook_add(UC_HOOK_CODE,observe,begin=0x44551a,end=0x44551a)
inputs={};shots={e['tick']:e for e in t['diagnostic_shots']}
for e in t['inputs']:inputs.setdefault(e['tick'],[]).append(e)
for tick in range(2000):
 for e in inputs.get(tick,[]):Chain.apply(m,e)
 if tick in shots:
  e=shots[tick];m.shot(e['layer'],e['x'],e['y'],e.get('ball',0))
 m.step(tick);assert m.ball()==t['states'][tick+1]
 if seen:break
assert seen
from collections import Counter
counts=Counter((v['tick'],v['callsite'],v['target'],v['return_address'],v['opcode'])for v in seen)
seen=[dict(tick=k[0],callsite=k[1],target=k[2],return_address=k[3],opcode=k[4],count=n)for k,n in counts.items()]
p=ROOT/'analysis/space-video-entry-probe.json';p.write_text(json.dumps(dict(build_sha256=t['build_sha256'],observations=seen),indent=2)+'\n');print('Original call[esp] target groups observed',len(seen),'times at tick',tick+1)
