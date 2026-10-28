#!/usr/bin/env python3
"""Extend proven admissions through actual ramp/trap rewards and physical drains."""
import argparse,json
from space_multiball_oracle import Multiball
from space_missions_oracle import EVENTS
from pirate_adventure_oracle import Original,ROOT,compact
KEYS=['globals','poses','lifecycle','highscore_sha256','lamp_sha256','raw_state_sha256','ball_pool_sha256']
class Rewards(Multiball):
 def prefix(self,case):
  old=json.loads((ROOT/f'build/oracle/space-modes/{case}.json').read_text());end=next(i+1 for i,r in enumerate(old['lifecycle'])if r[1]==3);end=(end+3)//4*4
  events={};shots={e['tick']:e for e in old['diagnostic_shots']}
  for e in old['inputs']:events.setdefault(e['tick'],[]).append(e)
  while self.tick<end:
   for e in events.get(self.tick,[]):self.event(e)
   if self.tick in shots:
    e=shots[self.tick];self.shots.append(e);self.m.shot(e['layer'],e['x'],e['y'],e.get('ball',0))
   self.step();assert self.states[-1]==old['states'][self.tick]
   for k in KEYS:assert self.samples[-1][k]==old[k][self.tick-1],(self.tick,k)
  self.mark('three_balls')
 def mark(self,label):
  r=super().mark(label);g=self.m.get;r.update(standard_flags=[g(0x46edde+i*2,2)for i in range(7)],alien_flags=[g(0x46edd0+i*2,2)for i in range(7)],field_46ee3e=g(0x46ee3e,2),field_46ee40=g(0x46ee40,2),jackpot_base=g(0x46ecc0),selected=g(0x46ed4e,2));return r
 def free(self):
  start=self.tick
  while self.m.get(0x46c1b4,2)!=2:self.park(1);assert self.tick-start<4000
 def hit(self,event):
  self.free();self.park(220)
  if event==1:
   self.shot('ramp1_first',0,72,99);self.shot('ramp1_second',0,137,34)
  else:self.shot('ramp_'+str(event),*EVENTS[event])
  self.free();self.mark('ramp_'+str(event)+'_done')
 def top(self,label):
  self.free();self.park(220);self.shot(label,0,210,18);self.free();self.mark(label+'_released')
 def drain_one(self):
  self.free();count=self.m.get(0x46c67c);start=self.tick;self.shot('drain_ball0_'+str(count),0,160,590)
  while self.m.get(0x46c67c)==count:
   i=self.tick%40
   if 0<i<count and self.m.get(0x46c15c+100*i+88,2)==2:self.shot('park_survivor',0,160+30*i,400,i)
   else:self.step()
   assert self.tick-start<4000,('drain failed',count,self.m.get(0x46c6ac))
  self.mark('pool_'+str(count)+'_to_'+str(self.m.get(0x46c67c)))
 def perform(self,case):
  self.prefix(case);self.top('unearned_top_guard')
  if case=='multiball':
   for n,events in enumerate([[0],[0,5],[0,5,6]],1):
    for e in events:self.hit(e)
    self.top('jackpot_'+str(n))
  else:
   self.hit(0);self.hit(0);self.mark('duplicate_guard')
   for e in [1,2,3,4,5,6]:self.hit(e)
   self.top('alien_super_jackpot');self.top('alien_super_duplicate')
  self.park(1400);self.drain_one();self.drain_one();self.park(80);self.mark('one_ball_pending_return')
 def resume(self,case):
  old=json.loads((ROOT/f'build/oracle/space-modes/{case}-rewards.json').read_text());events={};shots={e['tick']:e for e in old['diagnostic_shots']}
  for e in old['inputs']:events.setdefault(e['tick'],[]).append(e)
  while self.tick<old['tick_count']:
   for e in events.get(self.tick,[]):self.event(e)
   if self.tick in shots:
    e=shots[self.tick];self.shots.append(e);self.m.shot(e['layer'],e['x'],e['y'],e.get('ball',0))
   self.step();assert self.states[-1]==old['states'][self.tick]
   for k in KEYS:assert self.samples[-1][k]==old[k][self.tick-1]
  self.marks=old['milestones']
  for r in self.marks:
   if r['label']=='normal_return':r['label']='one_ball_pending_return'
 def generate_rewards(self,case,resume=False):
  table=getattr(self,"table","space")
  if resume:self.resume(case)
  else:self.perform(case)
  start=self.tick
  while self.m.get(0x46c6ac)!=2:
   self.park(1);assert self.tick-start<4000,'Return timeout'
  self.mark('normal_return_verified')
  while self.tick%4:self.step()
  summary=json.loads((self.prepared/'summary.json').read_text());t=dict(schema=1,table=table,case=case,build_sha256=summary['build_sha256'],dat_sha256=summary['dat_sha256'],tick_count=self.tick,inputs=self.inputs,diagnostic_shots=self.shots,milestones=self.marks,payments=self.payments,states=self.states,**{k:[s[k]for s in self.samples]for k in KEYS},executed_call_edges=[dict(callsite=hex(a),target=hex(b),count=n)for(a,b),n in sorted(self.m.calls.items())])
  path=ROOT/f'build/oracle/{table}-modes/{case}-rewards.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(compact(t)+b'\n');print('PROBE SAVED',path,flush=True)
  fresh=Original(self.prepared,table=table);events={};shots={e['tick']:e for e in self.shots};keep=self.m;self.m=fresh
  from unicorn import UC_HOOK_CODE
  from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_EBX
  from space_audio_oracle import SERVICES
  audio_events=[[0,0x90,fresh.get(0x454a68),fresh.get(0x454a64),0]]
  def observed(u,pc,size,data):
   service=SERVICES[pc];eax=u.reg_read(UC_X86_REG_EAX);edx=u.reg_read(UC_X86_REG_EDX);ebx=u.reg_read(UC_X86_REG_EBX)
   signed=lambda v:v if v<0x80000000 else v-0x100000000
   if service==0x5c:bank,order,desc=signed(edx),signed(ebx),eax
   elif service in [0x80,0x8c]:bank,order,desc=0,0,0
   else:bank,order,desc=signed(edx),signed(eax),0
   audio_events.append([tick+1,service,bank,order,desc])
  for address in SERVICES:fresh.u.hook_add(UC_HOOK_CODE,observed,begin=address,end=address)
  for e in self.inputs:events.setdefault(e['tick'],[]).append(e)
  assert len(shots)==len(self.shots)
  for tick in range(self.tick):
   for e in events.get(tick,[]):self.apply(fresh,e)
   if tick in shots:
    e=shots[tick];fresh.shot(e['layer'],e['x'],e['y'],e.get('ball',0))
   fresh.step(tick);assert fresh.ball()==self.states[tick+1]
   s=self.sample()
   for k in KEYS:assert s[k]==t[k][tick],(tick,k)
  self.m=keep;t['original_reset_exact']=True;t['audio_events']=audio_events;path.write_bytes(compact(t)+b'\n');print('RESET VERIFIED',case,self.tick,len(self.payments),'payments',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',choices=['multiball','alien'],required=True);p.add_argument('--resume',action='store_true');a=p.parse_args();Rewards().generate_rewards(a.case,a.resume)
