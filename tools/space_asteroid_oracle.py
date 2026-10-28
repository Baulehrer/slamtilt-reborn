#!/usr/bin/env python3
"""Frozen real-event admission -> three awards -> expiry -> ball/new-game state."""
import json
from space_modes_oracle import Space
from pirate_adventure_oracle import ROOT,Original,compact,digest
class Chain(Space):
 def sample(self):
  r=super().sample();g=self.m.get;p=g(0x46b758)
  r['globals']=dict(previous_ms=g(0x46c734),physics_accumulator=g(0x46c744),frame_accumulator=g(0x46c740),frame_count=g(0x46c704),crt_seed=g(0x100900c),rng_b4=g(0x46c6b4),rng_b8=g(0x46c6b8),phase=g(0x46c6ac),dmd_state=g(0x46c68c),dmd_sha256=r['dmd'])
  r['poses']=[g(a,2)for a in [0x46c786,0x46c76c,0x46c752]]
  r['lifecycle']=[g(0x46c6ac),g(0x46c67c),g(0x46c680),g(0x46c684),g(p+14,2),g(p+16,2),g(0x46c61c),g(0x46c620),*self.m.u.mem_read(p,6),g(0x46c60c)]
  r['highscore_sha256']=digest(bytes(self.m.u.mem_read(g(0x46c498),50)))
  r['lamp_sha256']=digest(b''.join(bytes(self.m.u.mem_read(a+8,2))for a in self.m.lamp_descriptors))
  return r
 def mark(self,label):
  r=super().mark(label);g=self.m.get;r.update(played_0=g(0x46ed38,2),ball_number=g(g(0x46b758)+14,2));return r
 def event(self,e):self.inputs.append(e);self.apply(self.m,e)
 @staticmethod
 def apply(m,e):
  scan=e.get('scan',dict(enter=0x1c,left=0x2a,right=0x36,new_game=0x3b).get(e['action']))
  m.run(0x40404c,0 if e['down']else 1,scan)
 def launch(self):
  start=self.tick
  while self.m.get(0x46c1b4,2)!=2:
   if self.tick%200==0:self.key('enter',True);self.key('enter',False)
   self.step();assert self.tick-start<2000
 def drain(self,i):
  self.shot('physical_drain_'+str(i),0,160,590);start=self.tick;letters=[0x1e,0x30,0x2e,0x1c]
  while self.m.get(0x46c6ac)!=(0 if i==3 else 1):
   if i==3 and self.m.get(0x46c6ac)==3 and self.m.get(0x46c61c)==6 and letters and self.tick%4==0:
    scan=letters.pop(0)
    for down in [True,False]:self.event(dict(tick=self.tick,action='key',scan=scan,down=down))
   self.step();assert self.tick-start<6000
  self.mark('drain_'+str(i)+'_settled')
 def generate(self):
  old=json.loads((ROOT/'build/oracle/space-modes/asteroid-probe.json').read_text());inputs={};shots={e['tick']:e for e in old['diagnostic_shots']};marks={}
  for e in old['inputs']:inputs.setdefault(e['tick'],[]).append(e)
  for e in old['milestones']:marks.setdefault(e['tick'],[]).append(e['label'])
  while self.tick<old['tick_count']:
   for e in inputs.get(self.tick,[]):self.event(e)
   if self.tick in shots:
    e=shots[self.tick];self.shots.append(e);self.m.shot(e['layer'],e['x'],e['y'])
   self.step();assert self.states[-1]==old['states'][self.tick]
   for k,v in old['samples'][self.tick-1].items():assert self.samples[-1][k]==v,(self.tick,k)
   for label in marks.get(self.tick,[]):self.mark(label)
  assert self.payments==old['payments'];self.mark('frozen_prefix_retained')
  self.park(220);self.mark('ramps_guard_before')
  for i in range(2):self.shot('no_asteroid_from_ramp_'+str(i),1,91,179)
  self.mark('ramps_guard_after');self.park(220)
  self.mark('award_2_before');self.shot('asteroid_station_2',0,10,295);self.free();self.mark('award_2_after')
  while self.m.get(0x46c6ac)==5:self.park(1);assert self.tick<19000
  self.mark('mission_expired')
  self.park(220);self.shot('played_station_guard',0,10,295);self.free();self.mark('played_not_rearmed')
  for i in range(1,4):
   self.drain(i)
   if i<3:self.launch();self.mark('ball_'+str(i+1)+'_launched')
  self.event(dict(tick=self.tick,action='new_game',down=True));self.mark('new_game_reset')
  self.park(80)
  while self.tick%4:self.step()
  name='space-asteroid';t=dict(schema=1,table='space',build_sha256='185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6',dat_sha256=json.loads((self.prepared/'summary.json').read_text())['dat_sha256'],tick_count=self.tick,inputs=self.inputs,diagnostic_shots=self.shots,milestones=self.marks,payments=self.payments,states=self.states,**{k:[s[k]for s in self.samples]for k in ['globals','poses','lifecycle','highscore_sha256','lamp_sha256','raw_state_sha256']},executed_call_edges=[dict(callsite=hex(a),target=hex(b),count=n)for(a,b),n in sorted(self.m.calls.items())])
  # Independent original reset, frozen actions only; no call/score hooks.
  fresh=Original(self.prepared,table='space');events={};shots={e['tick']:e for e in self.shots}
  for e in self.inputs:events.setdefault(e['tick'],[]).append(e)
  keep=self.m;self.m=fresh
  for tick in range(self.tick):
   for e in events.get(tick,[]):self.apply(fresh,e)
   if tick in shots:
    e=shots[tick];fresh.shot(e['layer'],e['x'],e['y'])
   fresh.run(0x405234,(tick+1)*5,until=0x405486)
   if (tick+1)%4==0:fresh.run(0x408da8)
   assert fresh.ball()==self.states[tick+1]
   s=self.sample()
   for k in ['globals','poses','lifecycle','highscore_sha256','lamp_sha256','raw_state_sha256']:assert s[k]==t[k][tick],(tick,k)
  self.m=keep;t['original_reset_exact']=True
  p=ROOT/'build/oracle/space-modes/asteroid-chain.json';p.write_bytes(compact(t)+b'\n');print('VERIFIED ORIGINAL RESET',self.tick,flush=True)
if __name__=='__main__':Chain().generate()
