#!/usr/bin/env python3
"""Bounded Original Space earned-grey-bank and physical kickback probe."""
import json,struct
from pathlib import Path
from space_base_rules_oracle import BaseRules
from pirate_adventure_oracle import ROOT
CONTACTS=[(61,330),(102,180),(197,264),(207,277)]
class Kickback(BaseRules):
 def fields(self):
  g=self.m.get
  return dict(flags=[g(0x46e930+i*2,2)for i in range(4)],charge=g(0x46ed34,2),timer=g(0x46ee58,2),ball=self.m.ball())
 def mark(self,label):
  r=super().mark(label);r.update(self.fields());return r
 def start(self):
  while self.tick<600:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
 def probe(self,armed):
  self.start();self.mark('ready')
  for i,(x,y)in enumerate(CONTACTS):
   if armed or i>0:self.shot('grey_'+str(i),0,x,y);self.mark('grey_'+str(i))
   else:self.park(1)
  while self.tick<620:self.park(1)
  self.m.shot(0,5,533);self.mark('same_sidelane_state');self.step();self.mark('after_contact')
  for _ in range(79):self.step()
  self.mark('after_80_steps')
  return dict(armed=armed,tick_count=self.tick,milestones=self.marks,inputs=self.inputs,shots=self.shots,states=self.states)
if __name__=='__main__':
 out=[]
 for armed in [False,True]:out.append(Kickback().probe(armed))
 p=ROOT/'build/oracle/space-modes/kickback-probe.json';p.write_text(json.dumps(out)+'\n');print('saved',p)
