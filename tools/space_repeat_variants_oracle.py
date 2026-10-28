#!/usr/bin/env python3
"""Earned second standard multiball and Walker trap/sight replay; no rule writes."""
import argparse,json
from space_weapons_oracle import Weapons
from space_multiball_oracle import Multiball
from pirate_adventure_oracle import ROOT
class Repeat(Weapons):
 def step(self):
  # Retain score observation; discover only the new repeat, not known prefix/video.
  if getattr(self,'discover',False):
   if not self.m.tracking:self.m.track_calls(exclude=((0x445100,0x445600),))
  elif self.m.tracking:self.m.pause_calls()
  Multiball.step(self)
 def frozen(self,case,end=None):
  t=json.loads((ROOT/f'build/oracle/space-modes/{case}-rewards.json').read_text());limit=end or t['tick_count'];events={};shots={e['tick']:e for e in t['diagnostic_shots']}
  for e in t['inputs']:events.setdefault(e['tick'],[]).append(e)
  while self.tick<limit:
   for e in events.get(self.tick,[]):self.event(e)
   if self.tick in shots:
    e=shots[self.tick];self.shots.append(e);self.m.shot(e['layer'],e['x'],e['y'],e.get('ball',0))
   self.step();assert self.states[-1]==t['states'][self.tick]
   for k in ['globals','poses','lifecycle','highscore_sha256','lamp_sha256','raw_state_sha256','ball_pool_sha256']:
    assert self.samples[-1][k]==t[k][self.tick-1],(self.tick,k)
  self.mark('frozen_'+case+'_prefix');self.discover=True
 def normal(self):
  start=self.tick
  while self.m.get(0x46c6ac)!=2:self.park(1);assert self.tick-start<5000
  self.free()
 def lose_multiballs(self):
  self.free();self.park(1400)
  while self.m.get(0x46c67c)>1:self.drain_one()
  self.normal()
 def perform(self,case):
  if case=='multiball-repeat':
   self.frozen('multiball');self.mark('second_cycle_ready');threshold=self.m.get(0x46ed42,2);assert threshold==3
   for i in range(threshold):self.top('second_lock_'+str(i));self.mark('second_lock_'+str(i)+'_checked')
   self.mark('below_higher_threshold');assert self.m.get(0x46ee66,2)==65535
   self.top('second_required_lock');self.mark('second_cycle_armed')
   self.shot('second_airlock',0,199,188);start=self.tick
   while self.m.get(0x46c67c)<3:self.park(1);assert self.tick-start<5000
   self.mark('second_three_balls');self.lose_multiballs();self.mark('second_cycle_returned')
  else:
   t=json.loads((ROOT/'build/oracle/space-modes/walker-rewards.json').read_text());end=next(m['tick']for m in t['milestones']if m['label']=='walker_spawned_balls')
   self.frozen('walker',end);self.mark('first_walker_hit_spawned');assert self.m.get(0x46c67c)==3
   self.free();self.park(220);self.shot('walker_repeat_mode_trap',0,166,101);self.mark('walker_recaptured')
   start=self.tick
   while not 71<=self.m.get(0x46ee4e,2)<=87:self.park(1);assert self.tick-start<4000
   self.mark('walker_second_aim');self.key('enter',True);self.step();self.key('enter',False);self.mark('walker_second_shot')
   self.park(1600);self.mark('walker_after_second_shot');self.lose_multiballs();self.mark('walker_repeat_returned')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',choices=['multiball-repeat','walker-repeat'],required=True);a=p.parse_args();Repeat().generate_rewards(a.case)
