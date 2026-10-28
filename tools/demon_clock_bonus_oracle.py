#!/usr/bin/env python3
"""Earn Demon x8, real Clock capture bonusbase, drain and actual multiplied payout."""
from demon_clock_oracle import Clock
class Bonus(Clock):
 def perform(self,case):
  while self.tick<600:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
  for i in range(4):self.bank('bonus_bank_'+str(i))
  self.free();self.park(220);self.shot('clock_bonus_capture',0,21,196);self.free();self.mark('earned_bonusbase');self.drain(1);self.mark('bonus_settled');self.launch();self.mark('following_ball')
if __name__=='__main__':Bonus().generate_rewards('clock-bonus')
