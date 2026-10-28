#!/usr/bin/env python3
"""Original earned grey bank -> paired physical sidelane save/consumption."""
import argparse
from space_weapons_oracle import Weapons
CONTACTS=[(61,330),(102,180),(197,264),(207,277)]
class Kickback(Weapons):
 def mark(self,label):
  r=super().mark(label);g=self.m.get
  r.update(grey_flags=[g(0x46e930+i*2,2)for i in range(4)],kickback_charge=g(0x46ed34,2),kickback_grace=g(0x46ee58,2),ball=self.m.ball());return r
 def perform(self,case):
  while self.tick<600:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
  self.mark('ready')
  for i,(x,y)in enumerate(CONTACTS):
   if case=='kickback-on' or i>0:self.shot('grey_'+str(i),0,x,y);self.mark('grey_'+str(i))
   else:self.park(1)
  while self.tick<620:self.park(1)
  self.mark('before_sidelane');self.shot('physical_sidelane',0,5,533);self.mark('sidelane_response')
  for _ in range(79):self.step()
  self.mark('sidelane_80_steps')
  if case=='kickback-on':
   self.free();self.mark('saved_ball_free')
   assert 0<self.m.get(0x46ee58,2)<250
   self.shot('grace_sidelane_repeat',0,5,533);self.mark('grace_repeat_response')
   start=self.tick
   while self.m.get(0x46ee58,2)!=65535:
    self.park(1);assert self.tick-start<1200
   self.free();self.mark('grace_expired')
   self.shot('expired_sidelane',0,5,533);self.mark('expired_response')
   for i,(x,y)in enumerate(CONTACTS):
    self.shot('rearm_grey_'+str(i),0,x,y);self.mark('rearm_grey_'+str(i))
   self.shot('rearmed_sidelane',0,5,533);self.mark('rearmed_response')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',choices=['kickback-on','kickback-off'],required=True);a=p.parse_args();Kickback().generate_rewards(a.case)
