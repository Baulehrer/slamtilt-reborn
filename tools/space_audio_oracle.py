#!/usr/bin/env python3
"""Observe shared original audio service registers while replaying frozen Space."""
import json
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_EBX
from pirate_adventure_oracle import Original,ROOT
from space_asteroid_oracle import Chain
SERVICES={0x406600:0x5c,0x406268:0x80,0x406240:0x84,0x40621c:0x88,0x4061f8:0x8c,0x4061c4:0x90}
def main():
 rows=[]
 sources=[('launch',ROOT/'build/oracle/space-full-tick/trace.json')]+[(c,ROOT/f'build/oracle/space-modes/{c}.json')for c in ['race','hack','blam','blam-guard','asteroid-chain','asteroid-traps']]
 for case,path in sources:
  t=json.loads(path.read_text());m=Original(ROOT/'build/oracle/space-full-game',table='space');assert m.ball()==t['states'][0]
  events=[[0,0x90,m.get(0x454a68),m.get(0x454a64),0]];tick=0
  def observed(u,pc,size,data):
   service=SERVICES[pc];eax=u.reg_read(UC_X86_REG_EAX);edx=u.reg_read(UC_X86_REG_EDX);ebx=u.reg_read(UC_X86_REG_EBX)
   signed=lambda x:x if x<0x80000000 else x-0x100000000
   if service==0x5c:bank,order,desc=signed(edx),signed(ebx),eax
   elif service in [0x80,0x8c]:bank,order,desc=0,0,0
   else:bank,order,desc=signed(edx),signed(eax),0
   events.append([tick+1,service,bank,order,desc])
  for address in SERVICES:m.u.hook_add(UC_HOOK_CODE,observed,begin=address,end=address)
  inputs={};shots={e['tick']:e for e in t.get('diagnostic_shots',[])}
  for e in t['inputs']:inputs.setdefault(e['tick'],[]).append(e)
  for tick in range(t['tick_count']):
   for e in inputs.get(tick,[]):Chain.apply(m,e)
   if tick in shots:
    e=shots[tick];m.shot(e['layer'],e['x'],e['y'])
   m.run(0x405234,(tick+1)*5,until=0x405486)
   if (tick+1)%4==0:m.run(0x408da8)
   assert m.ball()==t['states'][tick+1],(case,tick)
  rows.append(dict(case=case,steps=t['tick_count'],source=str(path.relative_to(ROOT)),events=events));print(case,len(events),'original requests',flush=True)
 (ROOT/'analysis/traces/space-audio-events.json').write_text(json.dumps(dict(schema=1,cases=rows,scope='Original register/service request stream; not original mixed-device PCM equivalence.'),indent=2)+'\n')
if __name__=='__main__':main()
