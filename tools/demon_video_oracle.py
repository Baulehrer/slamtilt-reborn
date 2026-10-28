#!/usr/bin/env python3
"""Earned Demon video modes driven by physical moon contacts and actual keys."""
import argparse
from demon_modes_oracle import Modes
import space_multiball_rewards_oracle as base
if 'video_state'not in base.KEYS:base.KEYS=base.KEYS+['video_state']
MOONS=[(30,318),(30,338),(30,358),(30,378)]
class Video(Modes):
 def __init__(self):
  super().__init__();self.m.pause_calls();self.m.track_calls(exclude=((0x416d6c,0x417620),))
 def video(self):
  g=self.m.get;p=g(0x46d60c);return[g(p+i)for i in [0x10,0x14,0x18,0x20,0x44]]
 def sample(self):
  s=super().sample();s['video_state']=self.video();return s
 def mark(self,label):
  r=super().mark(label);g=self.m.get;r.update(video_state=self.video(),moon_flags=[g(0x46d680+4*i)for i in range(4)],video_armed=g(0x46d57c),field_46d6e4=g(0x46d6e4),field_46d594=g(0x46d594),selected=g(0x46d584),cups=[g(0x46d554+4*i)for i in range(5)],field_463b74=g(0x463b74),field_463b7c=g(0x463b7c),field_463b80=g(0x463b80),field_463b84=g(0x463b84));print('VIDEO',label,self.tick,r['video_state'],r['moon_flags'],r['video_armed'],r['field_46d594'],r['selected'],r['cups'],r['field_463b74'],flush=True);return r
 def start(self):
  while self.tick<600:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
 def moons(self):
  self.mark('before_moons')
  for i,(x,y)in enumerate(MOONS):
   self.shot('moon_'+str(i),0,x,y);self.mark('moon_'+str(i))
   if i==0 and self.case=='video-wolf-idle':self.shot('duplicate_moon',0,x,y);self.mark('duplicate_moon_guard')
  assert self.m.get(0x46d57c)==1;self.mark('video_armed')
  if self.case=='video-wolf-idle':
   for i,(x,y)in enumerate(MOONS):self.shot('armed_bank_'+str(i),0,x,y)
   self.mark('armed_bank_repeat')
 def admit(self,brain):
  self.free();self.park(220);self.shot('video_capture',0,*( (91,14)if brain else(266,153)))
  start=self.tick
  while not self.video()[-1]:self.step();assert self.tick-start<3000
  self.mark('video_started')
 def tap(self,action):
  while self.tick%4:self.step()
  self.key(action,True)
  for _ in range(4):self.step()
  self.key(action,False)
  for _ in range(4):self.step()
 def perform(self,case):
  self.case=case;brain='brain'in case;self.start();self.moons();self.admit(brain)
  start=self.tick
  if brain:
   self.tap('enter');self.mark('early_enter_guard')
   while self.m.get(0x46d594)<0x80000000:self.step();assert self.tick-start<10000
   self.mark('choice_ready')
   if case=='video-brain-win':
    self.tap('right');self.tap('right');self.mark('right_edge')
    self.tap('right');self.mark('right_edge_guard')
    target=next(i for i in range(5)if self.m.get(0x46d554+4*i))
    while self.m.get(0x46d584)!=target:
     action='left'if self.m.get(0x46d584)>target else'right';self.tap(action)
   else:
    target=next(i for i in range(5)if not self.m.get(0x46d554+4*i))
    while self.m.get(0x46d584)!=target:
     action='left'if self.m.get(0x46d584)>target else'right';self.tap(action)
   if case=='video-brain-win':self.mark('left_edge');self.tap('left');self.mark('left_edge_guard')
   self.mark('choice_selected');self.tap('enter');self.mark('choice_confirmed')
  while self.video()[-1]:
   if case=='video-wolf-shoot'and self.tick%4==0 and len([p for p in self.payments if p['return_address']=='0x4170ac'])<2:
    action='left'if(self.tick//4)%2 else'right';self.key(action,True);self.key(action,False)
   self.step();assert self.tick-start<16000
  self.mark('video_ended');self.free();self.park(220);self.mark('video_returned')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',choices=['video-brain-win','video-brain-miss','video-wolf-shoot','video-wolf-idle'],required=True);a=p.parse_args();Video().generate_rewards(a.case)
