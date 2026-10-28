#!/usr/bin/env python3
"""A genuinely armed combo timer must not pay during Alien mode."""
from space_base_rules_oracle import BaseRules
class Guard(BaseRules):
 def perform(self,case):
  while self.tick<600:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
  self.shot('arm_mode',2,247,174);self.shot('enter_mode',0,166,101)
  while self.m.get(0x46c6ac)==2:self.step()
  self.free();self.mark('armed_timer_in_mode');assert self.m.get(0x46ee08,2)<0x8000
  self.shot('suppressed_combo_ramp',1,91,179);self.mark('combo_suppressed')
  start=self.tick
  while self.m.get(0x46c67c)<3:self.park(1);assert self.tick-start<5000
  self.free();self.park(1400)
  while self.m.get(0x46c67c)>1:self.drain_one()
if __name__=='__main__':Guard().generate_rewards('combo-mode-guard')
