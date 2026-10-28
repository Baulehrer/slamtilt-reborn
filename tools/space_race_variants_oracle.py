#!/usr/bin/env python3
"""Earn Race, advance using physical ramps, collect actual rank rewards."""
from space_weapons_oracle import Weapons
from space_multiball_oracle import Multiball
from space_missions_oracle import EVENTS
class Race(Weapons):
 def step(self):
  if self.tick<600 and self.m.tracking:self.m.pause_calls()
  elif self.tick>=600 and not self.m.tracking:self.m.track_calls(exclude=((0x445100,0x445600),))
  Multiball.step(self)
 def mark(self,label):
  r=super().mark(label);g=self.m.get;r.update(field_46ee40=g(0x46ee40),field_46ee42=g(0x46ee42,2),field_46ee4a=g(0x46ee4a,2));return r
 def perform(self,case):
  while self.tick<600:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
  for i in range(12):
   if self.m.get(0x46eae2,2):break
   self.park(220);self.shot('arm_race_'+str(i),0,10,295);self.free()
  assert self.m.get(0x46eae2,2)
  self.shot('admit_race',*EVENTS[2]);self.free();self.mark('race_started')
  self.hit(1);self.mark('passive_ramp_guard')
  for level in range(1,6):
   for j in range(8):
    if self.m.get(0x46ee4a,2)==65535:break
    self.hit(2);self.mark('goal_gate_'+str(level)+'_'+str(j))
   else:raise AssertionError('Goal gate did not clear')
   for j in range(6):
    if self.m.get(0x46ee42,2)>=level:break
    self.hit(0);self.mark('advance_'+str(level)+'_'+str(j))
   assert self.m.get(0x46ee42,2)==level
   if level==5:self.hit(0);self.mark('rank_cap_guard')
   self.mark('goal_'+str(level)+'_before');self.hit(2);self.mark('goal_'+str(level)+'_after')
  self.drain(1);self.mark('race_drained');self.launch();self.mark('next_ball_launched')
if __name__=='__main__':Race().generate_rewards('race-variants')
