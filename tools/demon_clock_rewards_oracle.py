#!/usr/bin/env python3
"""Clock jackpot earned with actual ramp and one/three simultaneous trap locks."""
import json
from demon_clock_oracle import Clock
from pirate_adventure_oracle import ROOT
class Rewards(Clock):
 def mark(self,label):
  r=super().mark(label);g=self.m.get;p=g(0x46d60c);r.update(clock_counter=g(0x46d658),clock_total=g(0x46d6c0),requirement=g(0x46d6c4),field_34=g(p+0x34));print(label,r['tick'],r['ball_count'],r['requirement'],r['field_34'],flush=True);return r
 def prefix(self):
  t=json.loads((ROOT/'build/oracle/demon-modes/clock-tower-rewards.json').read_text());end=next(m['tick']for m in t['milestones']if m['label']=='three_balls');events={};shots={e['tick']:e for e in t['diagnostic_shots']};self.m.pause_calls()
  for e in t['inputs']:events.setdefault(e['tick'],[]).append(e)
  while self.tick<end:
   for e in events.get(self.tick,[]):self.event(e)
   if self.tick in shots:
    e=shots[self.tick];self.shots.append(e);self.m.shot(e['layer'],e['x'],e['y'],e.get('ball',0))
   self.step();assert self.states[-1]==t['states'][self.tick]
   for k in ['globals','poses','lifecycle','highscore_sha256','lamp_sha256','raw_state_sha256','ball_pool_sha256']:assert self.samples[-1][k]==t[k][self.tick-1],k
  self.m.track_calls();self.mark('frozen_three_balls')
 def ramp(self,label):
  self.free();self.park(220);self.shot(label,1,130,30);self.free();self.mark(label+'_after')
 def capture(self,label,point):
  start=self.tick
  while True:
   free=[i for i in range(self.m.get(0x46c67c))if self.m.get(0x46c15c+100*i+88,2)==2]
   if free:break
   self.park(1);assert self.tick-start<4000
  self.shot(label,0,*point,free[0]);self.mark(label+'_contact')
 def wait_award(self,n):
  start=self.tick
  while len([p for p in self.payments if p['return_address']=='0x414544'])<n:self.park(1);assert self.tick-start<6000
 def perform(self,case):
  self.prefix();self.park(220);self.capture('unarmed_trap_guard',(91,14));self.free();self.mark('unarmed_released');self.ramp('first_ramp');self.ramp('armed_duplicate_ramp')
  for i,point in enumerate([(21,196),(266,153),(91,14)]):
   self.capture('jackpot_lock_'+str(i),point);start=self.tick
   if i<2:
    while self.m.get(self.m.get(0x46d60c)+0x34)<i+1:self.park(1);assert self.tick-start<4000
    self.mark('held_'+str(i+1))
   else:self.wait_award(1)
  self.mark('three_ball_jackpot');self.free();self.mark('released_after_jackpot');self.park(220);self.capture('rearm_trap_guard',(21,196));self.free();self.mark('rearm_guard_released')
  for i in range(4):self.ramp('rearm_ramp_'+str(i))
  self.mark('second_jackpot_armed');self.park(1400)
  while self.m.get(0x46c67c)>1:self.drain_one()
  self.mark('last_ball_armed');self.capture('single_ball_jackpot',(21,196));self.wait_award(2);self.mark('single_ball_paid')
  start=self.tick
  while self.m.get(0x46c6ac)!=2:self.park(1);assert self.tick-start<6000
  self.free();self.mark('rewards_returned')
if __name__=='__main__':Rewards().generate_rewards('clock-rewards')
