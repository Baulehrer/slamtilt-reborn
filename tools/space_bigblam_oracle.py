#!/usr/bin/env python3
"""One earned five-mode campaign and final; no rule/played/spawn edits."""
from space_planet_success_oracle import Planet
from space_missions_oracle import EVENTS
class Campaign(Planet):
 def step(self):
  # Modes0..4 already have independent nine-vector acceptance; discover only final.
  if self.m.get(0x46c6ac)==2 and all(self.m.get(0x46ed44+2*i,2)for i in range(5)):self.final_discovery=True
  discover=getattr(self,'final_discovery',False)
  if not discover and self.m.tracking:self.m.pause_calls()
  elif discover and not self.m.tracking:self.m.track_calls(exclude=((0x445100,0x445600),))
  from space_multiball_oracle import Multiball
  Multiball.step(self)
 def mark(self,label):
  r=super().mark(label);g=self.m.get;r.update(final_base=g(0x46ed10),field_46ee5e=g(0x46ee5e,2),field_46ee5c=g(0x46ee5c,2));return r
 def park(self,n):
  for _ in range(n):
   i=self.tick%40
   if i<self.m.get(0x46c67c) and self.m.get(0x46c15c+100*i+88,2)==2:self.shot('campaign_park',0,150+20*i,400,i)
   else:self.step()
 def drain_one(self):
  self.free();count=self.m.get(0x46c67c);start=self.tick;self.shot('campaign_drain_'+str(count),0,160,590)
  while self.m.get(0x46c67c)==count:
   i=self.tick%40
   if 0<i<count and self.m.get(0x46c15c+100*i+88,2)==2:self.shot('campaign_survivor',0,150+20*i,400,i)
   else:self.step()
   assert self.tick-start<5000
  self.mark('final_pool_'+str(count)+'_to_'+str(self.m.get(0x46c67c)))
 def normal(self):
  start=self.tick
  while self.m.get(0x46c6ac)!=2:self.park(1);assert self.tick-start<18000
  self.free()
 def admit(self,index):
  self.normal()
  for _ in range(6):
   if self.m.get(0x46ed4e,2)==index:break
   self.bumper('campaign_selector')
  assert self.m.get(0x46ed4e,2)==index
  self.shot('campaign_arm_'+str(index),*EVENTS[5]);self.shot('campaign_mode_'+str(index),0,166,101);start=self.tick
  while not self.m.get(0x46c6c0) and self.m.get(0x46c6ac)==2:self.step();assert self.tick-start<1000
  self.mark('mode_'+str(index)+'_started')
 def spawn_and_drain(self):
  start=self.tick
  while self.m.get(0x46c67c)<3:self.park(1);assert self.tick-start<5000
  self.free();self.park(1400)
  while self.m.get(0x46c67c)>1:self.drain_one()
  self.normal()
 def perform(self,case):
  while self.tick<600:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
  self.mark('campaign_start')
  for index in range(5):
   self.admit(index)
   if index==0:self.spawn_and_drain()
   elif index==1:
    self.free()
    for i in range(70):
     if self.m.get(0x46ee20,2)==0:break
     self.bumper('campaign_sabre_damage')
    assert self.m.get(0x46ee20,2)==0
    self.top('campaign_sabre_finish');self.normal()
   elif index==2:
    start=self.tick
    while self.m.get(0x46c6c0):self.step();assert self.tick-start<10000
    self.free()
   elif index==3:
    start=self.tick
    while not 71<=self.m.get(0x46ee4e,2)<=87:self.park(1);assert self.tick-start<5000
    self.key('enter',True);self.step();self.key('enter',False);self.spawn_and_drain()
   else:self.normal()
   self.mark('mode_'+str(index)+'_completed')
  assert all(self.m.get(0x46ed44+2*i,2)for i in range(5));self.mark('all_five_played')
  self.shot('earned_bigblam_capture',0,166,101);start=self.tick
  while self.m.get(0x46c6ac)==2:self.step();assert self.tick-start<1000
  self.mark('bigblam_admitted');self.park(6000);self.mark('bigblam_spawned')
  self.top('unearned_final_top');self.mark('unearned_final_guard')
  self.hit(1);self.mark('disabled_final_ramp_guard');self.hit(0);self.hit(0);self.mark('duplicate_final_ramp_guard')
  self.top('first_final_bank');self.mark('first_bank_collected')
  for e in [0,2,3,4,5,6]:self.hit(e)
  self.top('bigblam_top');self.mark('bigblam_rewards');self.top('duplicate_final_top');self.mark('duplicate_final_top_guard')
  self.park(1200)
  while self.m.get(0x46c67c)>1:self.drain_one()
  self.normal();self.mark('bigblam_returned')
if __name__=='__main__':Campaign().generate_rewards('bigblam')
