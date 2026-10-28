#!/usr/bin/env python3
"""Verified right-inlane/event2 path, passage cooldown, real window/grade expiry."""
from space_base_rules_oracle import BaseRules
class SpeedRules(BaseRules):
 def loop(self,label):self.free();self.shot(label,1,156,25);self.free()
 def inlane(self,label):self.free();self.shot(label,0,241,468)
 def advance(self,grade):
  for i in range(4):
   self.inlane('speed_inlane_'+str(grade)+'_'+str(i));self.loop('speed_pass_'+str(grade)+'_'+str(i));self.mark('pass_'+str(grade)+'_'+str(i))
   if self.m.get(0x46ee4c,2)==grade:break
  assert self.m.get(0x46ee4c,2)==grade
  self.mark('speed_grade_'+str(grade))
 def perform(self,case):
  while self.tick<600:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
  self.mark('speed_normal');self.loop('no_inlane_loop');self.mark('unarmed_speed_guard')
  for grade in range(1,5):self.advance(grade)
  for i in range(4):
   self.loop('lunatic_pass_'+str(i))
   if self.m.get(0x46ee4c,2)==0:break
  assert self.m.get(0x46ee4c,2)==0;self.mark('lunatic_paid')
  self.inlane('expiry_inlane');self.mark('speed_window_armed');self.park(1204)
  for i in range(4):self.loop('expired_speed_pass_'+str(i))
  self.mark('expired_speed_guard');self.advance(1);self.mark('decay_started')
  start=self.tick
  while self.m.get(0x46ee4c,2):self.park(1);assert self.tick-start<4000
  self.mark('speed_grade_decayed')
if __name__=='__main__':SpeedRules().generate_rewards('speed-rules')
