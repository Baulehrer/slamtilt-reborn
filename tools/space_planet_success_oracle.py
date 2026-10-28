#!/usr/bin/env python3
"""Frozen real DeathPlanet steering success; no writes to video or rule state."""
import argparse,json
from space_mode_family_oracle import Family
from pirate_adventure_oracle import ROOT
class Planet(Family):
 def __init__(self):
  super().__init__();self.m.pause_calls()
  # Reuse044's proven raster closure; do not trace per-pixel indirect calls again.
  self.m.track_calls(exclude=((0x445100,0x445600),))
 def step(self):
  # The video renderer is already verified044. Keep score hooks/state hashes,
  # resume call-edge discovery for the new success/collection/ball lifecycle.
  video=self.m.get(0x46c6c0)!=0 and self.m.get(0x466b72,2)>0
  if video and self.m.tracking:self.m.pause_calls()
  elif not video and not self.m.tracking:self.m.track_calls(exclude=((0x445100,0x445600),))
  super().step()
 def mark(self,label):
  r=super().mark(label);g=self.m.get;r.update(remaining_levels=g(0x466b72,2),video_state=g(0x466b74,2),pending_extra=g(0x46ed50,2),extra_credits=g(g(0x46b758)+16,2));return r
 def collect(self):
  self.top('collect_extra_ball');self.mark('extra_collected')
  self.drain(1);self.mark('extra_consumed_after_bonus');self.launch();self.mark('extra_ball_launched');self.park(100)
 def resume(self,case):
  super().resume(case);self.collect()
 def perform(self,case):
  old=json.loads((ROOT/'build/oracle/space-modes/planet-rewards.json').read_text());candidate=json.loads((ROOT/'build/oracle/space-planet-success/candidate.json').read_text());inputs={};shots={e['tick']:e for e in old['diagnostic_shots']}
  for e in old['inputs']+candidate['inputs']:inputs.setdefault(e['tick'],[]).append(e)
  previous=None
  while self.tick<candidate['tick_count']:
   for e in inputs.get(self.tick,[]):self.event(e)
   if self.tick in shots:
    assert self.tick<661,'No physical waypoints during video';e=shots[self.tick];self.shots.append(e);self.m.shot(e['layer'],e['x'],e['y'],e.get('ball',0))
   self.step()
   if self.tick<=661:
    assert self.states[-1]==old['states'][self.tick]
    if self.tick==661:self.mark('video_started')
   if self.tick>=661:
    now=(self.m.get(0x466b72,2),self.m.get(0x466b78,2),self.m.get(0x46c6c0))
    if now!=previous:self.mark('video_transition_'+str(self.tick));previous=now
  assert self.m.get(0x466b72,2)==0 and self.m.get(0x466b78,2)==3 and self.m.get(0x46c6c0)==0
  self.mark('six_levels_complete');self.free();self.mark('ball_released');self.park(500);self.mark('extra_pending');self.collect()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--resume',action='store_true');a=p.parse_args();Planet().generate_rewards('planet-success',a.resume)
