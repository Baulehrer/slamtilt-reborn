#!/usr/bin/env python3
"""Physical skull/right banks, kickback and earned Clock award outcomes."""
import argparse
from demon_video_oracle import Video
SKULLS=[(135,168),(150,162),(166,160)]
RIGHT=[(300,y)for y in [264,284,304,324,344]]
class Banks(Video):
 def __init__(self):
  super().__init__()
  from unicorn import UC_HOOK_CODE
  for pc,label in [(0x415e3b,'award_before'),(0x415f8d,'award_applied')]:
   def observed(u,pc,size,data,label=label):
    if not any(r['label']==label for r in self.marks):
     r=self.mark(label);r['tick']=self.tick+1
   self.m.u.hook_add(UC_HOOK_CODE,observed,begin=pc,end=pc)

 def mark(self,label):
  r=super().mark(label);g=self.m.get;p=g(0x46b758);r.update(skulls=[g(0x46d660+4*i)for i in range(3)],right_flags=[g(0x46d66c+4*i)for i in range(5)],kickback=g(0x46d65c),clock_armed=g(0x46d6ac),clock_index=g(0x46d5d8),spin_elapsed=g(0x46d5e0),field_0c=g(p+12,2),extra_balls=g(p+16,2),field_46d604=g(0x46d604),ball_bytes=self.m.ball());return r
 def skulls(self,label):
  for i,(x,y)in enumerate(SKULLS):self.shot(label+'_'+str(i),0,x,y)
  self.mark(label)
 def perform(self,case):
  self.start()
  if case.startswith('kickback'):
   if case!='kickback-off':self.skulls('earned_skulls')
   else:
    for i,(x,y)in enumerate(SKULLS[:2]):self.shot('partial_skull_'+str(i),0,x,y)
    self.step();self.mark('partial_skull_guard')
   while self.tick<1000:self.park(1)
   self.m.shot(0,16,520);self.mark('same_ball_before');self.shot('kickback_contact',0,16,520);self.mark('after_contact')
   for _ in range(80):self.step()
   self.mark('after_80')
   if case!='kickback-off':
    self.park(80);self.shot('grace_repeat',0,16,520);self.mark('grace_contact');start=self.tick
    while self.m.get(0x46d65c):self.park(1);assert self.tick-start<1400
    self.mark('expired');self.shot('expired_contact',0,16,520);self.mark('expired_guard');self.skulls('rearmed_skulls');self.shot('rearmed_contact',0,16,520);self.mark('second_save')
   else:self.park(80)
  else:
   self.trap((21,196),'earned_bonusbase')
   for i,(x,y)in enumerate(RIGHT):self.shot('right_'+str(i),0,x,y);self.mark('right_'+str(i))
   self.mark('clock_bank_armed');self.park(220+self.delay);self.shot('clock_award_capture',0,21,196);start=self.tick
   while self.m.get(0x46d6ac):self.step();assert self.tick-start<2000
   self.mark('spin_selected');assert self.m.get(0x46d5d8)==self.index
   while self.m.get(0x46d5e0)<312:self.step();assert self.tick-start<4000
   self.key('left',True);self.key('right',True);self.mark('stop_keys')
   self.free();self.key('left',False);self.key('right',False);self.mark('award_released')
   if self.index==6:self.drain(1);self.launch();self.mark('extra_ball_consumed')
   if self.index==10:
    self.shot('award_saver_drain',0,160,599);start=self.tick
    while self.m.get(0x46c1b4,2)==2:self.step();assert self.tick-start<400
    self.mark('saver_triggered');self.free();self.mark('saver_restored')
  self.park(220);self.mark('case_finished')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--delay',type=int,default=0);p.add_argument('--index',type=int,default=0);a=p.parse_args();m=Banks();m.delay=a.delay;m.index=a.index;m.generate_rewards(a.case)
