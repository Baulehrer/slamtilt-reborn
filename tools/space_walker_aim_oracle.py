#!/usr/bin/env python3
"""Real Walker aim edges70/87/88 plus ignored earlyEnter; original state only."""
import argparse
from space_repeat_variants_oracle import Repeat
class Aim(Repeat):
 def step(self):
  self.discover=self.tick<getattr(self,'trace_end',0)
  super().step()
 def perform(self,case):
  target=int(case.removeprefix('walker-aim'))
  self.frozen('walker',665);self.discover=False
  if self.m.tracking:self.m.pause_calls()
  self.mark('early_enter_before');before=self.sample();paid=len(self.payments)
  self.key('enter',True);self.key('enter',False)
  assert self.sample()==before and len(self.payments)==paid
  self.mark('early_enter_ignored')
  start=self.tick
  while self.m.get(0x46ee4e,2)!=target:
   self.park(1);assert self.tick-start<4000,('target not reached',target,self.m.get(0x46ee4e,2))
  self.mark('aim_edge_before');self.trace_end=self.tick+600;self.discover=True
  self.m.track_calls(exclude=((0x445100,0x445600),))
  self.key('enter',True);self.step();self.key('enter',False);self.mark('aim_edge_fired')
  self.lose_multiballs();self.mark('aim_edge_returned')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',choices=['walker-aim70','walker-aim87','walker-aim88'],required=True);a=p.parse_args();Aim().generate_rewards(a.case)
