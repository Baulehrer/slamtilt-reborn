#!/usr/bin/env python3
"""Space real top-lock/airlock admission; only FREE-ball diagnostic contacts."""
import argparse,json
from space_asteroid_oracle import Chain
from pirate_adventure_oracle import ROOT,Original,compact,digest
class Multiball(Chain):
 def sample(self):
  s=super().sample();s['ball_pool_sha256']=digest(bytes(self.m.u.mem_read(0x46c15c,800)));return s
 def step(self):
  self.m.step(self.tick);self.tick+=1;self.states.append(self.m.ball());self.samples.append(self.sample())
 def mark(self,label):
  r=super().mark(label);g=self.m.get;r.update(locks=g(0x46ed40,2),threshold=g(0x46ed42,2),airlock_timer=g(0x46ee66,2),spawn_timer=g(0x46ee68,2),ball_count=g(0x46c67c),ball_states=[g(0x46c15c+100*i+88,2)for i in range(g(0x46c67c))]);print('POOL',r['ball_count'],r['ball_states'],flush=True);return r
 def shot(self,label,layer,x,y,index=0):
  e=dict(tick=self.tick,label=label,layer=layer,x=x,y=y,ball=index);self.shots.append(e);self.m.shot(layer,x,y,index);self.step()
 def park(self,n):
  for _ in range(n):
   i=self.tick%40
   if i<self.m.get(0x46c67c) and self.m.get(0x46c15c+100*i+88,2)==2:
    e=dict(tick=self.tick,label='park',layer=0,x=160+30*i,y=400,ball=i);self.shots.append(e);self.m.shot(0,160+30*i,400,i)
   self.step()
 def generate(self,case="multiball"):
  while self.tick<600:
   if self.tick in (200,201):self.key('enter',self.tick==200)
   self.step()
  self.mark('normal')
  if case=='multiball':
   for i in range(3):
    self.shot('top_lock_'+str(i),0,210,18);self.free();self.mark('top_released_'+str(i))
    if i<2:self.park(220)
   self.shot('airlock_admission',0,199,188)
  else:
   self.shot('alien_arm_ramp',2,247,174);self.free();self.mark('alien_armed')
   self.shot('alien_mode_capture',0,166,101)
  self.park(6400);self.mark('after_admission')
  assert self.m.get(0x46c67c)==3 and self.m.get(0x46c6ac)==(4 if case=='multiball' else 6),'Admission failed'
  while self.tick%4:self.step()
  keys=['globals','poses','lifecycle','highscore_sha256','lamp_sha256','raw_state_sha256','ball_pool_sha256']
  t=dict(schema=1,table='space',build_sha256=json.loads((self.prepared/'summary.json').read_text())['build_sha256'],dat_sha256=json.loads((self.prepared/'summary.json').read_text())['dat_sha256'],tick_count=self.tick,inputs=self.inputs,diagnostic_shots=self.shots,milestones=self.marks,payments=self.payments,states=self.states,**{k:[s[k]for s in self.samples]for k in keys},executed_call_edges=[dict(callsite=hex(a),target=hex(b),count=n)for(a,b),n in sorted(self.m.calls.items())])
  fresh=Original(self.prepared,table='space');events={};shots={e['tick']:e for e in self.shots};keep=self.m;self.m=fresh
  for e in self.inputs:events.setdefault(e['tick'],[]).append(e)
  assert len(shots)==len(self.shots),'Duplicate diagnostic tick'
  for tick in range(self.tick):
   for e in events.get(tick,[]):self.apply(fresh,e)
   if tick in shots:
    e=shots[tick];fresh.shot(e['layer'],e['x'],e['y'],e.get('ball',0))
   fresh.step(tick);assert fresh.ball()==self.states[tick+1],(tick,'ball')
   sample=self.sample()
   for k in keys:assert sample[k]==t[k][tick],(tick,k)
  self.m=keep;t['original_reset_exact']=True
  out=ROOT/f'build/oracle/space-modes/{case}.json';out.write_bytes(compact(t)+b'\n');print('SAVED',out,self.tick,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',choices=['multiball','alien'],default='multiball');a=p.parse_args();Multiball().generate(a.case)
