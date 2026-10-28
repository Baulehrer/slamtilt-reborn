#!/usr/bin/env python3
"""Freeze native-discovered legal keys; verify Original natural score/game/initials/reset."""
import json
from demon_variants_oracle import Variants
from pirate_adventure_oracle import ROOT
class Legal(Variants):
 def shot(self,*args,**kwargs):raise AssertionError('Legal fixture must never reposition a ball')
 def park(self,*args,**kwargs):raise AssertionError('Legal fixture must never use diagnostic parking')
 def mark(self,label):
  r=super().mark(label);r['highscore_hex']=bytes(self.m.u.mem_read(self.m.get(0x46c498),50)).hex();return r
 def perform(self,case):
  t=json.loads((ROOT/'build/demon-legal-candidate.json').read_text());events={}
  for e in t['inputs']:events.setdefault(e['tick'],[]).append(e)
  while self.tick<t['tick_count']:
   for e in events.get(self.tick,[]):self.event(e)
   self.step()
  self.mark('first_natural_score');assert int(bytes(self.m.u.mem_read(self.m.get(0x46b758),6)).hex())>0
  self.key('left',False);self.key('right',False);letters=[0x1e,0x30,0x2e,0x1c];last=2
  while self.m.get(0x46c6ac)!=0:
   phase=self.m.get(0x46c6ac)
   if phase!=last:self.mark('phase_'+str(phase)+'_'+str(self.tick));last=phase
   if phase==1 and self.tick%200==0:self.key('enter',True);self.step();self.key('enter',False)
   elif phase==3 and self.m.get(0x46c61c)==6 and letters and self.tick%4==0:
    if len(letters)==4:self.mark('initials_ready')
    scan=letters.pop(0)
    for down in [True,False]:self.event(dict(tick=self.tick,action='key',scan=scan,down=down))
    self.step()
   else:self.step()
   assert self.tick<30000
  self.mark('game_over');assert not letters
  for _ in range(64):self.step()
  self.mark('game_over_stable')
  for down in [True,False]:self.event(dict(tick=self.tick,action='new_game',down=down))
  self.mark('new_game');start=self.tick
  while self.m.get(0x46c1b4,2)!=2:
   if self.tick%200==0:self.key('enter',True);self.step();self.key('enter',False)
   else:self.step()
   assert self.tick-start<2000
  for _ in range(48):self.step()
  self.mark('second_game_running');assert not self.shots
if __name__=='__main__':Legal().generate_rewards('legal-game')
