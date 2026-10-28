#!/usr/bin/env python3
"""Earned Witch force/rescues, Twice head cycles/double bonus, Zombie values."""
import argparse
from demon_video_oracle import Video
import space_multiball_rewards_oracle as base
if 'variant_state'not in base.KEYS:base.KEYS=base.KEYS+['variant_state']
class Variants(Video):
 def force(self):return[self.m.get(a,n)for a,n in [(0x463ae4,2),(0x463ae6,2),(0x463ae8,2),(0x463aea,2),(0x46b764,4)]]
 def variant(self):
  g=self.m.get;return[g(0x463ae4,2),g(0x46b764),g(g(0x46b758)+8),g(0x463bc0),g(0x463bc8),g(0x46d5f0),g(0x46d5d0)]
 def sample(self):
  s=super().sample();s['variant_state']=self.variant();return s
 def mark(self,label):
  r=super().mark(label);r.update(force_state=self.force(),ball_bytes=self.m.ball(),head_flags=self.m.get(0x463bc8),head_count=self.m.get(0x463bc0),zombie_value=self.m.get(0x46d5f0));return r
 def park(self,n):
  for _ in range(n):
   i=self.tick%40
   if i<self.m.get(0x46c67c) and self.m.get(0x46c15c+100*i+88,2)==2:self.shot('fixture_park',0,160+10*i,80,i)
   self.step()
 def admit(self,index,phase):
  self.trap((91,14),'spirit_arm')
  for i in range(index):self.ramp(0,'cycle_'+str(i))
  self.ramp(3,'admission');assert self.m.get(0x46c6ac)==phase;self.mark('mode_started')
 def rescue(self,label,layer,x,y):
  self.free();self.shot(label,layer,x,y);self.mark(label+'_contact');start=self.tick
  while self.m.get(0x46c6ac)==11:self.step();assert self.tick-start<2000
  self.free();self.mark(label+'_restored')
 def perform(self,case):
  self.start()
  if case.startswith('witch'):
   self.admit(1,11)
   if case=='witch-left':self.rescue('left_sidelane',0,10,598)
   else:
    if case=='witch-force-off':self.rescue('right_sidelane',1,308,594)
    self.shot('common_physical_skull',0,135,168)
    while self.tick<3000:self.park(1)
    self.m.shot(0,175,300);self.mark('force_initial');self.shot('force_probe',0,175,300)
    for _ in range(19):self.step()
    self.mark('force_20')
    if case=='witch-force-on':self.rescue('right_sidelane',1,308,594)
   self.mark('witch_returned')
  elif case=='twice-cycles':
   self.admit(2,6);self.park(1400);self.mark('two_balls');self.ramp(0,'bonusbase_ramp')
   self.mark('before_double');self.trap((91,14),'double_bonus');self.mark('after_double');self.trap((91,14),'double_duplicate');self.mark('after_double_duplicate')
   self.trap((21,196),'clock_head');self.trap((21,196),'clock_head_duplicate');self.trap((266,153),'wolf_head');self.mark('first_pair_complete')
   self.trap((91,14),'rearmed_double');self.mark('after_rearmed_double');self.trap((266,153),'second_wolf');self.trap((21,196),'second_clock');self.mark('second_pair_complete')
   self.park(1400)
   while self.m.get(0x46c67c)>1:self.drain_one()
   start=self.tick
   while self.m.get(0x46c6ac)!=2:self.park(1);assert self.tick-start<1800
   self.mark('twice_returned');self.mark('before_bonus_drain');self.drain(1);self.launch();self.mark('following_ball')
  else:
   assert case=='zombie-values';self.admit(0,5);self.ramp(0,'base_kill');self.mark('base_value')
   for i,p in enumerate([(21,196),(91,14),(266,153)]):
    self.trap(p,'increase_'+str(i));self.ramp(i,'value_kill_'+str(i));self.mark('value_'+str(i))
   self.drain(1);self.launch();self.mark('zombie_returned')
  self.park(220);self.mark('case_finished')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',choices=['witch-force-on','witch-force-off','witch-left','twice-cycles','zombie-values'],required=True);a=p.parse_args();Variants().generate_rewards(a.case)
