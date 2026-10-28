#!/usr/bin/env python3
"""Three sibling missions from the same earned four-mission admission prefix."""
import argparse,json
from space_asteroid_oracle import Chain
from pirate_adventure_oracle import Original,ROOT,compact
EVENTS={0:(1,91,179),2:(1,156,25),3:(0,199,188),4:(3,255,151),5:(2,247,174),6:(1,269,51)}
class Mission(Chain):
 def mark(self,label):
  r=super().mark(label);g=self.m.get;r.update(played=[g(0x46ed38+i*2,2)for i in range(4)],field_46ee42=g(0x46ee42,2),field_46ee4a=g(0x46ee4a,2),field_46ee52=g(0x46ee52,2),field_46ee54=g(0x46ee54,2),flags_edec=[g(0x46edec+i*2,2)for i in range(7)],flags_edfa=[g(0x46edfa+i*2,2)for i in range(7)]);return r
 def prefix(self):
  old=json.loads((ROOT/'build/oracle/space-modes/asteroid-chain.json').read_text());end=next(m['tick']for m in old['milestones']if m['label']=='asteroid_armed');events={};shots={e['tick']:e for e in old['diagnostic_shots']}
  for e in old['inputs']:events.setdefault(e['tick'],[]).append(e)
  while self.tick<end:
   for e in events.get(self.tick,[]):self.event(e)
   if self.tick in shots:
    e=shots[self.tick];self.shots.append(e);self.m.shot(e['layer'],e['x'],e['y'])
   self.step();assert self.states[-1]==old['states'][self.tick]
   for k in ['globals','poses','lifecycle','highscore_sha256','lamp_sha256','raw_state_sha256']:assert self.samples[-1][k]==old[k][self.tick-1]
  self.mark('all_four_armed')
 def hit(self,event,label):
  self.free();self.park(220)
  if event==1:
   self.shot(label+'_first',0,72,99);self.shot(label,0,137,34)
  else:self.shot(label,*EVENTS[event])
  self.free();self.mark(label+'_after')
 def top(self,label):
  self.free();self.park(220);self.shot(label,0,210,18);self.free();self.mark(label+'_after')
 def generate_case(self,case):
  mode={'race':1,'hack':2,'blam':3}[case];event={'race':2,'hack':4,'blam':5}[case]
  self.prefix();self.shot('admit_'+case,*EVENTS[event]);self.free();self.mark('mission_started');assert self.m.get(0x46c6ac)==5 and self.m.get(0x46ee34,2)==mode
  if case=='race':
   self.top('top_sets_first');self.hit(2,'goal_first_place');self.mark('race_goal_paid')
   while self.m.get(0x46c6ac)==5:self.park(1);assert self.tick<20000
  elif case=='hack':
   target=self.m.get(0x46ee54,2);assert target<7
   wrong=(target+1)%7;self.hit(wrong,'wrong_password');self.mark('wrong_password_guard')
   self.hit(target,'winning_password');self.mark('hack_paid')
   while self.m.get(0x46c6ac)==5:self.park(1);assert self.tick<16000
  else:
   self.hit(0,'blam_first');self.hit(0,'blam_duplicate');self.mark('duplicate_guard')
   for event in [2,3,4,5,6]:self.hit(event,'blam_target_'+str(event))
   self.mark('all_targets_hit');self.top('final_target');self.mark('blam_paid')
   while self.m.get(0x46c6ac)==5:self.park(1);assert self.tick<18000
  self.mark('normal_return');self.park(80)
  while self.tick%4:self.step()
  t=dict(schema=1,table='space',mission=case,build_sha256='185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6',dat_sha256=json.loads((self.prepared/'summary.json').read_text())['dat_sha256'],tick_count=self.tick,inputs=self.inputs,diagnostic_shots=self.shots,milestones=self.marks,payments=self.payments,states=self.states,**{k:[s[k]for s in self.samples]for k in ['globals','poses','lifecycle','highscore_sha256','lamp_sha256','raw_state_sha256']},executed_call_edges=[dict(callsite=hex(a),target=hex(b),count=n)for(a,b),n in sorted(self.m.calls.items())])
  fresh=Original(self.prepared,table='space');events={};shots={e['tick']:e for e in self.shots};keep=self.m;self.m=fresh
  for e in self.inputs:events.setdefault(e['tick'],[]).append(e)
  for tick in range(self.tick):
   for e in events.get(tick,[]):self.apply(fresh,e)
   if tick in shots:
    e=shots[tick];fresh.shot(e['layer'],e['x'],e['y'])
   fresh.run(0x405234,(tick+1)*5,until=0x405486)
   if (tick+1)%4==0:fresh.run(0x408da8)
   assert fresh.ball()==self.states[tick+1];s=self.sample()
   for k in ['globals','poses','lifecycle','highscore_sha256','lamp_sha256','raw_state_sha256']:assert s[k]==t[k][tick],(tick,k)
  self.m=keep;t['original_reset_exact']=True
  (ROOT/f'build/oracle/space-modes/{case}.json').write_bytes(compact(t)+b'\n');print('MISSION ORIGINAL VERIFIED',case,self.tick,self.payments,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',choices=['race','hack','blam'],required=True);a=p.parse_args();Mission().generate_case(a.case)
