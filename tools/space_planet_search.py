#!/usr/bin/env python3
"""Offline Original-only key policy search; outputs legal keys, never rule writes."""
import json,struct
from pirate_adventure_oracle import Original,ROOT
from space_asteroid_oracle import Chain
PREFIX=661

def prepared():
 m=Original(ROOT/'build/oracle/space-full-game',table='space');t=json.loads((ROOT/'analysis/traces/space-planet-rewards.json').read_text());inputs={};shots={e['tick']:e for e in t['diagnostic_shots']}
 for e in t['inputs']:inputs.setdefault(e['tick'],[]).append(e)
 for tick in range(PREFIX):
  for e in inputs.get(tick,[]):Chain.apply(m,e)
  if tick in shots:
   e=shots[tick];m.shot(e['layer'],e['x'],e['y'])
  m.step(tick)
 return m

def signed32(x):return x if x<0x80000000 else x-0x100000000

def target(m,margin):
 p=m.get(0x466b7c)+8*m.get(0x466b70,2);depth=m.get(p+2,2);lo,hi=-100.0,100.0
 for i in range(8):
  typ,z,x,_=struct.unpack('<hHhh',m.u.mem_read(p+8*i,8))
  if typ==0 or z!=depth:break
  if typ<0:lo=max(lo,x+margin)
  else:hi=min(hi,x-margin)
 return max(lo,min(hi,0.0))

def run(margin,damping,sign):
 m=prepared();keys={'left':False,'right':False};events=[];rows=[];previous=None
 for tick in range(PREFIX,25000):
  video=m.get(0x46c6c0)
  if tick%4==0:
   x=signed32(m.get(0x466b64))/65536;v=signed32(m.get(0x466b68))/65536;goal=target(m,margin)
   error=goal-(x+v*damping);move=(1 if error>1 else -1 if error< -1 else 0)*sign if video else 0
   for action,on in [('left',move<0),('right',move>0)]:
    if keys[action]!=on:
     e=dict(tick=tick,action=action,down=on);Chain.apply(m,e);events.append(e);keys[action]=on
  m.step(tick)
  state=(m.get(0x466b72,2),m.get(0x466b78,2),m.get(0x46c6c0))
  if state!=previous:
   rows.append(dict(tick=tick+1,remaining=state[0],lives=state[1],video=state[2],progress=m.get(0x466b6c,2),obstacle=m.get(0x466b70,2)));previous=state
  if not state[2] and tick%4==0:break
 p=m.get(0x46b758);out=dict(policy=dict(margin=margin,damping=damping,sign=sign),tick_count=tick+1,inputs=events,transitions=rows,remaining=state[0],lives=state[1],extra_credits=m.get(p+16,2),scope='Native-free Original-only offline policy search; actual keys after earned diagnostic admission, fresh full reset verification pending.')
 print(out['policy'],out['remaining'],out['lives'],out['extra_credits'],out['tick_count'],flush=True)
 return out
if __name__=='__main__':
 work=ROOT/'build/oracle/space-planet-success';work.mkdir(exist_ok=True,parents=True)
 for sign in [1,-1]:
  for margin,damping in [(8,3),(12,3),(4,3),(8,1),(8,5)]:
   t=run(margin,damping,sign);(work/'last-policy.json').write_text(json.dumps(t,indent=2)+'\n')
   if t['remaining']==0 and t['lives']>0:
    (work/'candidate.json').write_text(json.dumps(t,indent=2)+'\n');raise SystemExit(0)
 raise SystemExit('No success policy')
