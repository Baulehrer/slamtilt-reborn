#!/usr/bin/env python3
"""Original trap contacts -> earned Clock Tower pool lifecycle."""
from demon_base_oracle import Demon
import space_multiball_rewards_oracle as base
if "clock_state"not in base.KEYS:base.KEYS=base.KEYS+["clock_state"]
class Clock(Demon):
 def sample(self):
  s=super().sample();g=self.m.get;p=g(0x46d60c);s["clock_state"]=[g(p),g(p+0x34),g(0x46d658),g(0x46d6c0),g(0x46d6c4)];return s
 def mark(self,label):
  r=super().mark(label);g=self.m.get;r.update(ball_count=g(0x46c67c),ball_states=[g(0x46c15c+100*i+88,2)for i in range(g(0x46c67c))],field_5a=g(0x46c1b6,2),observed_words={hex(a):g(a,2)for a in range(0x46d600,0x46d740,2)if g(a,2)});return r
 def perform(self,case):
  while self.tick<600:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
  self.mark('normal')
  for i in range(3):
   self.free();self.park(220);self.mark('clock_'+str(i)+'_before');self.shot('clock_'+str(i),0,21,196);self.mark('clock_'+str(i)+'_capture');self.free();self.mark('clock_'+str(i)+'_released')
  start=self.tick
  while self.m.get(0x46c67c)<3:self.park(1);assert self.tick-start<6000
  self.mark('three_balls');self.park(1400)
  while self.m.get(0x46c67c)>1:self.drain_one()
  start=self.tick
  while self.m.get(0x46c6ac)!=2:self.park(1);assert self.tick-start<5000
  self.mark('clock_returned')
if __name__=='__main__':Clock().generate_rewards('clock-tower')
