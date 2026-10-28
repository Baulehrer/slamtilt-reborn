#!/usr/bin/env python3
"""Four original Space mode dispatches, actual switches/keys, no rule writes."""
import argparse
import space_multiball_rewards_oracle as base
from pirate_adventure_oracle import digest
from space_missions_oracle import EVENTS
base.KEYS=base.KEYS+['aux_state_sha256']
class Family(base.Rewards):
 def sample(self):
  s=super().sample();s['aux_state_sha256']=digest(bytes(self.m.u.mem_read(0x466b6c,256)));return s
 def mark(self,label):
  r=super().mark(label);g=self.m.get;r.update(field_46ee20=g(0x46ee20,2),field_46ee48=g(0x46ee48,2),field_46ee4e=g(0x46ee4e,2),field_466b78=g(0x466b78,2),video_flag=g(0x46c6c0),played_modes=[g(0x46ed44+2*i,2)for i in range(5)]);return r
 def bumper(self,label):
  self.shot(label,0,200,128)
  for _ in range(3):self.step()
 def resume(self,case):
  super().resume(case)
  if case=='planet':self.free();self.mark('planet_ball_released')
 def perform(self,case):
  selected={'sabre':1,'planet':2,'walker':3,'bikes':4}[case]
  while self.tick<600:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
  for i in range(selected):self.bumper('select_'+str(i+1));assert self.m.get(0x46ed4e,2)==i+1
  self.mark('selected');self.shot('mode_arm',*EVENTS[5]);self.shot('mode_capture',0,166,101)
  start=self.tick
  while (self.m.get(0x46c6c0)==0 if case=='planet' else self.m.get(0x46c6ac)==2):self.step();assert self.tick-start<1000
  self.mark('mode_started');assert (self.m.get(0x46c6c0)==1 if case=='planet' else self.m.get(0x46c6ac)==6) and self.m.get(0x46ed4e,2)==selected
  if case=='sabre':
   self.free();self.top('unearned_finish_guard');self.mark('damage_before')
   for i in range(70):
    if self.m.get(0x46ee20,2)==0:break
    self.bumper('sabre_bumper_'+str(i))
   else:raise AssertionError('Sabre damage stalled')
   self.mark('damage_complete');self.top('sabre_finish');self.mark('sabre_paid')
   start=self.tick
   while self.m.get(0x46c6ac)==6:self.park(1);assert self.tick-start<17000
  elif case=='bikes':
   self.free();self.park(220);side=self.m.get(0x46ee48,2);assert side in(0,5)
   self.shot('wrong_side',*EVENTS[5 if side==0 else 0]);self.mark('wrong_side_guard')
   for i in range(3):
    self.park(220);side=self.m.get(0x46ee48,2);assert side in(0,5)
    self.shot('matching_side_'+str(i),*EVENTS[side]);self.mark('matching_side_'+str(i)+'_paid')
   start=self.tick
   while self.m.get(0x46c6ac)==6:self.park(1);assert self.tick-start<15000
  elif case=='walker':
   start=self.tick
   while not 71<=self.m.get(0x46ee4e,2)<=87:self.park(1);assert self.tick-start<4000
   self.mark('walker_aim');self.key('enter',True);self.step();self.key('enter',False);self.mark('walker_shot')
   start=self.tick
   while self.m.get(0x46c67c)<2:self.park(1);assert self.tick-start<5000
   self.free();self.park(1600);self.mark('walker_spawned_balls')
   while self.m.get(0x46c67c)>1:self.drain_one()
   start=self.tick
   while self.m.get(0x46c6ac)==6:self.park(1);assert self.tick-start<4000
  else:
   start=self.tick
   while self.m.get(0x46c6c0)!=0:self.step();assert self.tick-start<25000
   self.mark('planet_failed_naturally');self.free();self.mark('planet_ball_released')
  self.mark('mode_outcome')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',choices=['sabre','planet','walker','bikes'],required=True);p.add_argument('--resume',action='store_true');a=p.parse_args();Family().generate_rewards(a.case,a.resume)
