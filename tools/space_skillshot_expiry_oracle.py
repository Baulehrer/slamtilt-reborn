#!/usr/bin/env python3
"""First right-ramp arrival after the real launch window, without timer writes."""
from space_base_rules_oracle import BaseRules
class Expired(BaseRules):
 def perform(self,case):
  while self.tick<300:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
  self.mark('expiry_launch');self.park(1004);self.mark('skillshot_expired')
  self.shot('late_right_ramp',3,255,151);self.free();self.mark('expired_ramp_guard')
if __name__=='__main__':Expired().generate_rewards('skillshot-expiry')
