#!/usr/bin/env python3
"""Bounded real-ramp observations; no semantic fields guessed or written."""
import json
from space_mode_family_oracle import Family
from space_missions_oracle import EVENTS
from pirate_adventure_oracle import ROOT,compact
class Probe(Family):
 def perform(self):
  while self.tick<300:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
  self.mark('first_launch');self.shot('early_right_ramp',*EVENTS[4]);self.free();self.mark('first_right_ramp')
  for i,e in enumerate([0,2,4,5]*6):
   self.hit(e);self.mark('base_ramp_'+str(i))
  self.top('pending_extra_collect');self.mark('base_collect')
  (ROOT/'build/oracle/space-modes/base-probe.json').write_bytes(compact(dict(tick_count=self.tick,milestones=self.marks,payments=self.payments,inputs=self.inputs,diagnostic_shots=self.shots))+b'\n');print('BASE PROBE',self.tick,len(self.payments),'payments')
if __name__=='__main__':Probe().perform()
