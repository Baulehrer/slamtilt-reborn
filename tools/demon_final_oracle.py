#!/usr/bin/env python3
"""Earn all seven Demon modes in one game, then original final rewards/pool lifecycle."""
from demon_modes_oracle import Modes,RAMPS
FLAGS=[0x46d69c,0x46d6a0,0x46d6a4,0x46d6a8,0x46d6b0,0x46d6b4,0x46d6b8]
class Campaign(Modes):
 def __init__(self):
  super().__init__();self.m.pause_calls();self.discover=False
 def step(self):
  if not self.discover and sum(bool(self.m.get(a))for a in FLAGS)>=6:self.discover=True;self.m.track_calls()
  super().step()
 def mark(self,label):
  r=super().mark(label);g=self.m.get;r.update(final_ready=g(0x46d6e8),final_count=g(0x46d590),field_463b88=g(0x463b88),played=[g(a)for a in FLAGS]);return r
 def park(self,n):
  for _ in range(n):
   i=self.tick%40
   if i<self.m.get(0x46c67c) and self.m.get(0x46c15c+100*i+88,2)==2:self.shot('campaign_park',0,150+20*i,400,i)
   else:self.step()
 def normal(self):
  start=self.tick
  while self.m.get(0x46c6ac)!=2:self.park(1);assert self.tick-start<16000
  self.free()
 def wolf(self,name,index,phase):
  self.normal();self.ramp(index,'campaign_'+name+'_select');assert self.m.get(0x46d6d0)=={0:3,1:2,2:1}[index]
  self.trap((266,153),'campaign_'+name+'_admit');assert self.m.get(0x46c6ac)==phase
  self.mark(name+'_started')
  if name in ['grave','meatball']:
   for i in range(4):
    if self.m.get(0x46c6ac)!=phase:break
    self.ramp(i,'campaign_'+name+'_reward_'+str(i))
  self.normal();self.mark(name+'_returned')
 def spirit(self,name,index,phase):
  self.normal();self.trap((91,14),'campaign_'+name+'_arm');assert self.m.get(0x46d6c8)==index+1
  self.ramp(3,'campaign_'+name+'_admit');assert self.m.get(0x46c6ac)==phase;self.mark(name+'_started')
  if name=='witch':self.free();self.drain(1);self.launch()
  elif name=='twice':
   start=self.tick
   while self.m.get(0x46c67c)<2:self.park(1);assert self.tick-start<5000
   self.park(1400);self.drain_one()
  elif name=='vampires':
   for i in range(4):self.ramp(i,'campaign_vampire_'+str(i))
  self.normal();self.mark(name+'_returned')
 def wait_pool(self,count):
  start=self.tick
  while self.m.get(0x46c67c)<count:self.park(1);assert self.tick-start<5000
  self.free();self.park(1400)
 def final_ramps(self,label,n=5):
  for i in range(n):self.ramp(i%4,label+'_'+str(i))
  self.mark(label+'_paid')
 def perform(self,case):
  while self.tick<600:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
  self.mark('campaign_start');self.trap((266,153),'unearned_final_guard');assert self.m.get(0x46c6ac)==2
  for row in [('bat',0,9),('grave',1,8),('meatball',2,10)]:self.wolf(*row)
  for row in [('zombie',0,5),('witch',1,11),('twice',2,6),('vampires',3,7)]:self.spirit(*row)
  self.mark('all_seven_played');assert all(self.m.get(a)for a in FLAGS)and self.m.get(0x46d6e8)
  self.trap((21,196),'ready_clock_not_admission');assert self.m.get(0x46c6ac)==2
  self.trap((266,153),'earned_final');assert self.m.get(0x46c6ac)==12;self.mark('final_admitted')
  self.wait_pool(4);self.mark('four_balls');self.final_ramps('four_ball_bank')
  self.drain_one();self.drain_one();self.mark('two_balls')
  self.final_ramps('two_ball_bank');self.wait_pool(3);self.mark('three_balls')
  self.final_ramps('three_ball_bank');self.wait_pool(4);self.mark('restored_four')
  self.final_ramps('cap_four_bank');self.trap((21,196),'final_clock_reward');self.mark('final_rewards_done')
  self.park(1400)
  while self.m.get(0x46c67c)>1:self.drain_one()
  self.normal();self.mark('final_returned')
  self.ramp(0,'fresh_wolf_selection');assert self.m.get(0x46d6d0)==3;self.mark('fresh_bank_armed')
if __name__=='__main__':Campaign().generate_rewards('final-campaign')
