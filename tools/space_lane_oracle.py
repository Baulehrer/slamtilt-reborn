#!/usr/bin/env python3
"""Original loop direction selected by actual left-special input, no rule edits."""
import argparse
from space_weapons_oracle import Weapons
class Lane(Weapons):
 def mark(self,label):
  r=super().mark(label);g=self.m.get;r.update(direction=g(0x46ed2c,2),passage=g(0x46ee4a,2),direction_lamps=list(self.m.u.mem_read(0x46ec74,8)),ball=self.m.ball());return r
 def special(self):
  for down in [True,False]:self.event(dict(tick=self.tick,action='key',scan=0x1d,down=down))
 def perform(self,case):
  while self.tick<600:
   if self.tick in (200,201):self.key('enter',self.tick==200)
   self.step()
  self.mark('initial_direction')
  if case=='lane-toggle':self.special()
  elif case=='lane-double':self.special();self.special()
  elif case=='lane-shift':self.key('left',True);self.key('left',False)
  self.mark('selected_direction')
  self.shot('loop_entry',1,156,25);self.mark('loop_admission')
  if case=='lane-live':
   while self.tick<680:self.step()
   self.special();self.mark('mid_loop_selected')
  while self.tick<1001:self.step()
  self.mark('loop_400_steps')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',choices=['lane-default','lane-toggle','lane-double','lane-shift','lane-live'],required=True);a=p.parse_args();Lane().generate_rewards(a.case)
