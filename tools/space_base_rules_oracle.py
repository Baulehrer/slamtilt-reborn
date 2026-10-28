#!/usr/bin/env python3
"""Real launch/ramp chains, earned Combo credits and physical bonus/ball replay."""
from space_planet_success_oracle import Planet
from space_missions_oracle import EVENTS
class BaseRules(Planet):
 def mark(self,label):
  r=super().mark(label);g=self.m.get;p=g(0x46b758);r.update(skillshot_next=g(0x46ed58),skillshot_timer=g(0x46ee5a,2),combo_count=g(p+12,2),combo_threshold=g(0x46ed5c,2),bonus_base=g(p+8),speed_grade=g(0x46ee4c,2),speed_window=g(0x46ee3c,2),speed_decay=g(0x46ee3e,2),combo_timers=[g(0x46ee08+2*i,2)for i in range(7)]);return r
 def combo(self,i):
  self.free();self.park(120);self.shot('combo_'+str(i),*EVENTS[0 if i%2==0 else 5]);self.free()
 def perform(self,case):
  while self.tick<300:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
  self.mark('launch_ready');self.shot('skillshot_first',*EVENTS[4]);self.free();self.mark('skillshot_10m')
  self.park(120);self.shot('skillshot_repeat',*EVENTS[4]);self.free();self.mark('skillshot_repeat_guard')
  i=0
  for threshold in [20,40]:
   while self.m.get(self.m.get(0x46b758)+12,2)<threshold:self.combo(i);i+=1;assert i<100
   self.mark('combo_'+str(threshold)+'_earned');self.top('combo_'+str(threshold)+'_collect');self.mark('combo_'+str(threshold)+'_collected')
  for n in range(2):
   self.drain(1);self.mark('credit_'+str(n+1)+'_consumed');self.launch();self.mark('credit_'+str(n+1)+'_launched')
  self.drain(1);self.mark('normal_next_ball_ready');self.launch();self.mark('normal_next_ball_launched')
  self.shot('skillshot_next_ball',*EVENTS[4]);self.free();self.mark('skillshot_15m')
if __name__=='__main__':BaseRules().generate_rewards('base-rules')
