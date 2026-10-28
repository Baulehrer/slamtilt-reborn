#!/usr/bin/env python3
"""Actual Space station admission -> mission0 -> station awards, no rule writes."""
import json
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP
from pirate_adventure_oracle import Original,ROOT,compact,digest
class Space:
 def __init__(self):
  self.prepared=ROOT/'build/oracle/space-full-game';self.m=Original(self.prepared,table='space',track_edges=True);self.tick=0;self.inputs=[];self.shots=[];self.states=[self.m.ball()];self.samples=[];self.marks=[];self.payments=[]
  def paid(u,a,s,d):self.payments.append(dict(tick=self.tick+1,amount=u.reg_read(UC_X86_REG_EAX),return_address=hex(self.m.get(u.reg_read(UC_X86_REG_ESP)))))
  self.m.u.hook_add(UC_HOOK_CODE,paid,begin=0x405fac,end=0x405fac)
 def sample(self):
  g=self.m.get;p=g(0x46b758)
  return dict(phase=g(0x46c6ac),ball=self.m.ball(),score=bytes(self.m.u.mem_read(p,6)).hex(),dmd=digest(bytes(self.m.u.mem_read(g(0x46c47c),1920))),raw_state_sha256=digest(bytes(self.m.u.mem_read(0x46e970,0x600))))
 def step(self):
  self.m.run(0x405234,(self.tick+1)*5,until=0x405486);self.tick+=1
  if self.tick%4==0:self.m.run(0x408da8)
  self.states.append(self.m.ball());self.samples.append(self.sample())
 def key(self,action,down):
  e=dict(tick=self.tick,action=action,down=down);self.inputs.append(e);self.m.run(0x40404c,0 if down else 1,{'enter':0x1c,'left':0x2a,'right':0x36}[action])
 def mark(self,label):
  g=self.m.get;r=dict(tick=self.tick,label=label,phase=g(0x46c6ac),state=g(0x46c1b4,2),mode=g(0x46ee34,2),timer=g(0x46ee3a,2),award=g(0x46ed18),armed=[g(0x46eae0+i*2,2)for i in range(4)],score=bytes(self.m.u.mem_read(g(0x46b758),6)).hex());self.marks.append(r);print(r,flush=True);return r
 def shot(self,label,layer,x,y):
  e=dict(tick=self.tick,label=label,layer=layer,x=x,y=y);self.shots.append(e);self.m.shot(layer,x,y);self.step()
 def free(self):
  start=self.tick
  while self.m.get(0x46c1b4,2)!=2:self.step();assert self.tick-start<4000
 def park(self,n):
  for _ in range(n):
   if self.tick%40==0 and self.m.get(0x46c1b4,2)==2:self.shot('park',0,160,400)
   else:self.step()
 def main(self):
  while self.tick<600:
   if self.tick in [200,201]:self.key('enter',self.tick==200)
   self.step()
  self.mark('normal')
  for i in range(6):
   self.shot('station_arm_'+str(i),0,10,295);self.free();self.mark('station_release_'+str(i));self.park(220)
   if self.m.get(0x46eae0,2)==1:break
  else:raise AssertionError('Mission0 not armed')
  self.mark('asteroid_armed');self.shot('asteroid_ramp',1,91,179);self.free();self.mark('asteroid_started')
  for i in range(2):
   self.park(220);self.mark('award_'+str(i)+'_before');self.shot('asteroid_station_'+str(i),0,10,295);self.free();self.mark('award_'+str(i)+'_after')
  p=ROOT/'build/oracle/space-modes/asteroid-probe.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(compact(dict(tick_count=self.tick,inputs=self.inputs,diagnostic_shots=self.shots,milestones=self.marks,payments=self.payments,states=self.states,samples=self.samples,executed_call_edges=[dict(callsite=hex(a),target=hex(b),count=n)for(a,b),n in sorted(self.m.calls.items())]))+b'\n');print('DONE',self.tick,self.payments,flush=True)
if __name__=='__main__':Space().main()
