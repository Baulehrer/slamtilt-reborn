#!/usr/bin/env python3
"""Actual Sabre target/ramp damage and Original displayed power=field+1."""
import json
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EBX
from space_weapons_oracle import Weapons
from space_missions_oracle import EVENTS
from pirate_adventure_oracle import ROOT,compact
class Sabre(Weapons):
 def __init__(self):
  super().__init__();self.power_display={}
  def shown(u,pc,size,data):
   h=self.m.get(0x46ee20,2);v=u.reg_read(UC_X86_REG_EBX);assert v==h+1;self.power_display[h]=v
  self.m.u.hook_add(UC_HOOK_CODE,shown,begin=0x440803,end=0x440803)
 def perform(self,case):
  while self.tick<600:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
  self.bumper('select_sabre');assert self.m.get(0x46ed4e,2)==1
  self.shot('arm_sabre',*EVENTS[5]);self.shot('capture_sabre',0,166,101)
  start=self.tick
  while self.m.get(0x46c6ac)==2:self.step();assert self.tick-start<1000
  self.free();self.mark('sabre_started');assert self.m.get(0x46ee20,2)==44
  self.top('unearned_finish_guard')
  for i,(x,y)in enumerate([(61,330),(102,180),(197,264),(207,277)]):
   self.mark('target_'+str(i)+'_before');self.shot('sabre_target_'+str(i),0,x,y);self.mark('target_'+str(i)+'_after')
   if i==0:self.shot('target_duplicate',0,x,y);self.mark('target_duplicate_guard')
  self.hit(1);self.mark('excluded_ramp_guard')
  for i,e in enumerate([0,2,3,4,5,6]):
   self.mark('ramp_'+str(i)+'_before');self.hit(e);self.mark('ramp_'+str(i)+'_after')
  for i in range(6):self.hit(0)
  self.mark('near_finish');self.hit(0);self.mark('one_internal_left');self.hit(0);self.mark('zero_internal')
  for _ in range(8):self.step()
  self.mark('one_displayed_unit');assert self.m.get(0x46ee20,2)==0
  self.hit(0);self.mark('defeated_ramp_guard');self.top('sabre_finish');self.mark('sabre_finished')
 def generate_rewards(self,case):
  super().generate_rewards(case);p=ROOT/f'build/oracle/space-modes/{case}-rewards.json';t=json.loads(p.read_text());t['power_display_observations']=[dict(field_46ee20=k,displayed_units=v)for k,v in sorted(self.power_display.items())];p.write_bytes(compact(t)+b'\n')
if __name__=='__main__':Sabre().generate_rewards('sabre-variants')
