#!/usr/bin/env python3
"""Earn Demon six-lamp multipliers/cap, physical bonus/drains/initials/reset."""
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP
from pirate_adventure_oracle import ROOT,Original,digest
from space_multiball_rewards_oracle import Rewards
CONTACTS=[(126,60),(148,60),(170,60)]
class Demon(Rewards):
 def __init__(self):
  self.table='demon';self.prepared=ROOT/'build/oracle/demon-full-game';self.m=Original(self.prepared,table='demon',track_edges=True);self.tick=0;self.inputs=[];self.shots=[];self.states=[self.m.ball()];self.samples=[];self.marks=[];self.payments=[]
  def paid(u,pc,size,data):self.payments.append(dict(tick=self.tick+1,amount=u.reg_read(UC_X86_REG_EAX),return_address=hex(self.m.get(u.reg_read(UC_X86_REG_ESP)))))
  self.m.u.hook_add(UC_HOOK_CODE,paid,begin=0x405fac,end=0x405fac)
 def sample(self):
  s=super().sample();s['raw_state_sha256']=digest(bytes(self.m.u.mem_read(0x46d400,0x400)));return s
 def mark(self,label):
  g=self.m.get;p=g(0x46b758);r=dict(label=label,tick=self.tick,phase=g(0x46c6ac),state=g(0x46c1b4,2),flags=[g(0x46d690+4*i)for i in range(3)],multiplier=g(p+18,2),bonus_base=g(p+8),ball_number=g(p+14,2),score=bytes(self.m.u.mem_read(p,6)).hex());self.marks.append(r);print(r,flush=True);return r
 def bank(self,label):
  for i,(x,y)in enumerate(CONTACTS):
   if self.m.get(0x46d690+4*i)==0:self.shot(label+'_'+str(i),0,x,y)
   if not any(self.m.get(0x46d690+4*j)for j in range(3)):break
  assert not any(self.m.get(0x46d690+4*j)for j in range(3));self.mark(label)
 def perform(self,case):
  while self.tick<600:
   if self.tick in (200,201):self.key('enter',self.tick==200)
   self.step()
  self.mark('normal');self.shot('first_six',0,126,60);self.mark('one_six');self.shot('same_six',0,126,60);self.mark('duplicate_guard')
  self.key('left',True);self.step();self.key('left',False);self.mark('flipper_cycle')
  for i in range(5):self.bank('six_bank_'+str(i))
  for i in [1,2,3]:
   self.mark('before_drain_'+str(i));self.drain(i);self.mark('after_drain_'+str(i))
   if i<3:self.launch();self.mark('ball_'+str(i+1)+'_launched')
  self.event(dict(tick=self.tick,action='new_game',down=True));self.mark('new_game');self.launch();self.mark('new_game_launched')
if __name__=='__main__':Demon().generate_rewards('base-rules')
