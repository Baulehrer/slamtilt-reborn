#!/usr/bin/env python3
"""Earn Wolf/Spirit admissions via original DAT contacts; no rule-state writes."""
import argparse
from demon_clock_oracle import Clock
import space_multiball_rewards_oracle as base
from pirate_adventure_oracle import digest
if 'mode_aux_sha256' not in base.KEYS:base.KEYS=base.KEYS+['mode_aux_sha256']
RAMPS=[(1,130,30),(2,54,30),(2,172,45),(2,281,30)]
MODES={'bat':(9,0),'grave':(8,1),'meatball':(10,2),'zombie':(5,0),'witch':(11,1),'twice':(6,2),'vampires':(7,3)}
class Modes(Clock):
 def sample(self):
  s=super().sample();s['mode_aux_sha256']=digest(bytes(self.m.u.mem_read(0x463b54,0x100))+bytes(self.m.u.mem_read(0x46ceec,0x20)));return s
 def mark(self,label):
  r=super().mark(label);g=self.m.get;r.update(wolf_selected=g(0x46d6d0),spirit_selected=g(0x46d6c8),timer=g(0x46d5f4),mode_total=g(0x46d5d0),wolf_played=[g(0x46d6b0+4*i)for i in range(3)],spirit_played=[g(0x46d69c+4*i)for i in range(4)],aux=[g(0x463b94+4*i)for i in range(12)]);print('MODE',label,self.tick,r['phase'],r['wolf_selected'],r['spirit_selected'],r['timer'],flush=True);return r
 def ramp(self,index,label):
  self.free();self.park(220);self.shot(label,*RAMPS[index]);self.free();self.mark(label+'_done')
 def trap(self,xy,label):
  self.free();self.park(220);self.shot(label,0,*xy);self.mark(label+'_contact');self.free();self.mark(label+'_released')
 def perform(self,case):
  name=case.removeprefix('mode-');phase,index=MODES[name]
  while self.tick<600:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
  self.mark('normal')
  if name in ['bat','grave','meatball']:
   self.trap((266,153),'unarmed_wolf_guard');assert self.m.get(0x46c6ac)==2
   self.ramp(index,'wolf_select');assert self.m.get(0x46d6d0)=={0:3,1:2,2:1}[index]
   self.trap((266,153),'wolf_admission')
  else:
   self.ramp(3,'unarmed_spirit_guard');assert self.m.get(0x46c6ac)==2
   self.trap((91,14),'spirit_arm');assert self.m.get(0x46d6c8)==1
   for i in range(index):self.ramp(0,'spirit_cycle_'+str(i))
   assert self.m.get(0x46d6c8)==index+1
   self.ramp(3,'spirit_admission')
  assert self.m.get(0x46c6ac)==phase,(name,'admission',self.m.get(0x46c6ac));self.mark('mode_started')
  for i in range(4):
   if self.m.get(0x46c6ac)!=phase:break
   self.ramp(i,'reward_ramp_'+str(i))
  self.mark('ramps_finished')
  if self.m.get(0x46c6ac)==phase:
   self.trap((21,196),'mode_clock_reward')
  self.mark('rewards_finished')
  self.park(1400)
  while self.m.get(0x46c67c)>1:self.drain_one()
  if self.m.get(0x46c6ac)!=2:
   self.drain(1);self.mark('physical_loss');self.launch()
  start=self.tick
  while self.m.get(0x46c6ac)!=2:self.park(1);assert self.tick-start<5000
  self.free();self.mark('mode_returned')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',choices=list(MODES),required=True);a=p.parse_args();Modes().generate_rewards('mode-'+a.case)
