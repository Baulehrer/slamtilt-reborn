#!/usr/bin/env python3
"""Real weapon rollovers/keys, multiplier payout and Magnasaver force control."""
import argparse
import space_multiball_rewards_oracle as base
from space_base_rules_oracle import BaseRules
base.KEYS=base.KEYS+['weapon_state']
CONTACTS=[(210,86),(240,86),(270,86)]
class Weapons(BaseRules):
 def __init__(self):
  super().__init__();self.m.pause_calls();self.m.track_calls(exclude=((0x445100,0x445600),),extra_ranges=((0x4070bc,0x407340),))
  import capstone
  from unicorn import UC_HOOK_CODE
  cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True
  for site in [0x404ab4,0x404af7]:
   self.m.indirect[site]=next(cs.disasm(bytes(self.m.u.mem_read(site,8)),site))
   self.m.call_hooks.append(self.m.u.hook_add(UC_HOOK_CODE,self.m._indirect,begin=site,end=site))
 def sample(self):
  s=super().sample();g=self.m.get;s['weapon_state']=[g(a,2)for a in [0x46ed2e,0x46ed30,0x46ed32,0x46ed36,0x46ee5c,0x466568,g(0x46b758)+18]];return s
 def mark(self,label):
  r=super().mark(label);r['weapon_state']=self.sample()['weapon_state'];return r
 def bank(self,label):
  for i,(x,y)in enumerate(CONTACTS):self.shot(label+'_'+str(i),0,x,y)
  self.mark(label)
 def activate(self):
  for down in [True,False]:self.event(dict(tick=self.tick,action='key',scan=0x9d,down=down))
 def perform(self,case):
  while self.tick<600:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
  self.mark('weapons_normal')
  if case=='special-left':
   self.mark('special_left_before')
   for down in [True,False]:self.event(dict(tick=self.tick,action='key',scan=0x1d,down=down))
   for _ in range(20):self.step()
   self.mark('special_left_after');return
  if case=='weapons-ladder':
   self.shot('first_weapon',0,210,86);self.mark('one_lit');self.shot('duplicate_weapon',0,210,86);self.mark('duplicate_weapon_guard')
   self.key('left',True);self.step();self.key('left',False);self.mark('flipper_rotated')
   for i in range(6):self.bank('weapon_bank_'+str(i))
   self.shot('earned_bonus_ramp',3,255,151);self.free();self.mark('nonzero_bonus');self.mark('before_bonus_drain');self.shot('physical_bonus_drain',0,160,590)
   start=self.tick;entered=False
   while self.m.get(0x46c6ac)!=1:
    self.step()
    if self.m.get(0x46c6ac)==3 and not entered:entered=True;self.mark('bonus_entered')
    assert self.tick-start<5000
   self.mark('bonus_settled');self.launch();self.mark('following_ball')
  else:
   self.bank('earned_magna');
   while self.tick%4:self.step()
   self.mark('activation_boundary')
   if case!='magna-off':self.activate()
   self.shot('same_magna_test_state',0,263,450);self.mark('magna_start')
   for _ in range(19):self.step()
   self.mark('magna_20_steps')
   if case!='magna-off':
    self.activate();self.mark('retrigger_guard');start=self.tick
    while self.m.get(0x466568,2):self.park(1);assert self.tick-start<1200
    self.mark('magna_expired');self.activate();self.mark('unarmed_activation_guard');self.bank('magna_rearmed')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',choices=['weapons-ladder','magna-off','magna-on','special-left'],required=True);a=p.parse_args();Weapons().generate_rewards(a.case)
