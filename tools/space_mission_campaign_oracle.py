#!/usr/bin/env python3
"""Earn all four missions in one game, collect station award, restart mission bank."""
from space_weapons_oracle import Weapons
from space_missions_oracle import EVENTS
class Campaign(Weapons):
 def mark(self,label):
  r=super().mark(label);g=self.m.get;r['mission_played']=[g(0x46ed38+2*i,2)for i in range(4)];return r
 def station(self,label):
  self.free();self.park(220);self.shot(label,0,10,295);self.free();self.mark(label+'_released')
 def admit_mission(self,i,label):
  for n in range(20):
   if self.m.get(0x46eae0+2*i,2):break
   self.station(label+'_arm_'+str(n))
  else:raise AssertionError(('mission not armed',i))
  self.shot(label+'_admission',*EVENTS[[0,2,4,5][i]]);self.free();self.mark(label+'_started')
  assert self.m.get(0x46c6ac)==5 and self.m.get(0x46ee34,2)==i
 def normal(self):
  start=self.tick
  while self.m.get(0x46c6ac)!=2:self.park(1);assert self.tick-start<16000
  self.free()
 def perform(self,case):
  while self.tick<600:
   if self.tick in(200,201):self.key('enter',self.tick==200)
   self.step()
  self.station('unearned_station_guard')
  for i in range(4):
   self.admit_mission(i,'mission_'+str(i))
   if i<2:
    self.drain(i+1);self.mark('mission_'+str(i)+'_carried_to_next_ball');self.launch()
   elif i==2:
    self.hit(self.m.get(0x46ee54,2));self.normal()
   else:
    for event in [0,2,3,4,5,6]:self.hit(event)
    self.top('mission_3_finish');self.normal()
   self.mark('mission_'+str(i)+'_completed')
   if i==2:self.station('three_mission_station_guard')
  self.mark('all_four_played');self.station('earned_station_super');self.mark('super_collected')
  self.station('duplicate_station_guard');self.mark('duplicate_super_guard')
  self.admit_mission(0,'fresh_asteroid');self.mark('fresh_mission_bank');self.drain(3);self.mark('campaign_game_over');self.event(dict(tick=self.tick,action='new_game',down=True));self.mark('new_game_reset');self.launch();self.mark('fresh_game_launched')
if __name__=='__main__':Campaign().generate_rewards('mission-campaign')
