#!/usr/bin/env python3
"""Same earned Asteroid admission; all four actual trap consumers independently."""
import json
from space_asteroid_oracle import Chain
from pirate_adventure_oracle import Original,ROOT,compact
TRAPS=[(1,10,295),(2,210,18),(5,166,101),(3,199,188)]
def main():
 r=Chain();old=json.loads((ROOT/'build/oracle/space-modes/asteroid-chain.json').read_text());end=next(m['tick']for m in old['milestones']if m['label']=='asteroid_started');events={};shots={e['tick']:e for e in old['diagnostic_shots']}
 for e in old['inputs']:events.setdefault(e['tick'],[]).append(e)
 while r.tick<end:
  for e in events.get(r.tick,[]):r.event(e)
  if r.tick in shots:
   e=shots[r.tick];r.shots.append(e);r.m.shot(e['layer'],e['x'],e['y'])
  r.step();assert r.states[-1]==old['states'][r.tick]
  for k in ['globals','poses','lifecycle','highscore_sha256','lamp_sha256','raw_state_sha256']:assert r.samples[-1][k]==old[k][r.tick-1]
 r.mark('matrix_started')
 for cap,x,y in TRAPS:
  r.park(220);r.mark(f'capture_{cap}_before');r.shot(f'capture_{cap}',0,x,y)
  assert r.m.get(0x46c1b4,2)==3 and r.m.get(0x46c1b6,2)==cap,(cap,r.m.get(0x46c1b6,2))
  r.free();r.mark(f'capture_{cap}_after')
 r.park(80)
 while r.tick%4:r.step()
 t=dict(schema=1,table='space',build_sha256=old['build_sha256'],dat_sha256=old['dat_sha256'],tick_count=r.tick,inputs=r.inputs,diagnostic_shots=r.shots,milestones=r.marks,payments=r.payments,states=r.states,**{k:[s[k]for s in r.samples]for k in ['globals','poses','lifecycle','highscore_sha256','lamp_sha256','raw_state_sha256']},executed_call_edges=[dict(callsite=hex(a),target=hex(b),count=n)for(a,b),n in sorted(r.m.calls.items())])
 fresh=Original(r.prepared,table='space');events={};shots={e['tick']:e for e in r.shots};keep=r.m;r.m=fresh
 for e in r.inputs:events.setdefault(e['tick'],[]).append(e)
 for tick in range(r.tick):
  for e in events.get(tick,[]):r.apply(fresh,e)
  if tick in shots:
   e=shots[tick];fresh.shot(e['layer'],e['x'],e['y'])
  fresh.run(0x405234,(tick+1)*5,until=0x405486)
  if (tick+1)%4==0:fresh.run(0x408da8)
  assert fresh.ball()==r.states[tick+1];s=r.sample()
  for k in ['globals','poses','lifecycle','highscore_sha256','lamp_sha256','raw_state_sha256']:assert s[k]==t[k][tick],(tick,k)
 r.m=keep;t['original_reset_exact']=True
 (ROOT/'build/oracle/space-modes/asteroid-traps.json').write_bytes(compact(t)+b'\n');print('ORIGINAL TRAP MATRIX VERIFIED',r.tick,r.payments,flush=True)
if __name__=='__main__':main()
