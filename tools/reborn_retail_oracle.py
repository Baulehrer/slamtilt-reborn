#!/usr/bin/env python3
"""Fresh Original Retail play, legal observed-state key policy only; no diagnostic writes."""
import argparse,hashlib,json,struct,time
from collections import Counter
from pathlib import Path
from pirate_adventure_oracle import Original,ROOT,compact,digest
from space_audio_oracle import SERVICES
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_EBX
PREP={'pirate':'pirate-complete-game-lamps-ready','space':'space-full-game','demon':'demon-full-game'}
def apply(m,e):
 scan=e.get('scan',dict(enter=0x1c,left=0x2a,right=0x36,new_game=0x3b).get(e['action']))
 m.run(0x40404c,0 if e['down']else 1,scan)
def sample(m):
 g=m.get;p=g(0x46b758);h=lambda a,n:digest(bytes(m.u.mem_read(a,n)))
 common=dict(lifecycle=[g(0x46c6ac),g(0x46c67c),g(0x46c680),g(0x46c684),g(p+14,2),g(p+16,2),g(0x46c61c),g(0x46c620),*m.u.mem_read(p,6),g(0x46c60c)],highscore_sha256=h(g(0x46c498),50),lamp_sha256=digest(b''.join(bytes(m.u.mem_read(a+8,2))for a in m.lamp_descriptors)),ball_pool_sha256=h(0x46c15c,800))
 if m.table=='pirate':
  other=m.sample();common.update({k:other[k]for k in ['timing','dmd_sha256','rule_sha256','video_sha256']})
 else:
  common.update(poses=[g(a,2)for a in [0x46c786,0x46c76c,0x46c752]],globals=dict(previous_ms=g(0x46c734),physics_accumulator=g(0x46c744),frame_accumulator=g(0x46c740),frame_count=g(0x46c704),crt_seed=g(0x100900c),rng_b4=g(0x46c6b4),rng_b8=g(0x46c6b8),phase=g(0x46c6ac),dmd_state=g(0x46c68c),dmd_sha256=h(g(0x46c47c),1920)))
  if m.table=='demon':common['raw_state_sha256']=h(0x46d400,0x400)
 return common

def generate(table,steps,variant,output,track=False):
 prepared=ROOT/'build/oracle'/PREP[table];m=Original(prepared,table=table,track_edges=track)
 keyboard_bindings=[]
 if table=='pirate':
  # The canonical isolated Pirate snapshot omitted user key configuration.
  # Original404b00/404c0f compare these fields; this is startup input config only.
  for address,value in [(0x46c5dc,0x2a),(0x46c5e0,0x36)]:
   keyboard_bindings.append(dict(address=hex(address),before=m.get(address),after=value));m.put(address,value)
 configured_context_sha256=digest(bytes(m.u.mem_read(0x400000,0x100000)))
 # Bound hooks to the engine's actual table/DMD/collision dispatch calls.
 # Rendering/service internals are already covered by the frozen closure.
 keep={0x405414,0x407c09,0x407c23}
 for a,hook in list(zip(m.indirect,m.call_hooks)):
  if a not in keep:m.u.hook_del(hook)
 tick=0;events=[];audio=[[0,0x90,m.get(0x454a68),m.get(0x454a64),0]];states=[m.ball()];samples=[];phases=[];lastphase=None;pressed=dict(left=False,right=False);pending={};letters=[];initials=False
 def observed(u,pc,size,data):
  s=SERVICES[pc];eax=u.reg_read(UC_X86_REG_EAX);edx=u.reg_read(UC_X86_REG_EDX);ebx=u.reg_read(UC_X86_REG_EBX);signed=lambda x:x if x<0x80000000 else x-0x100000000
  if s==0x5c:bank,order,descriptor=signed(edx),signed(ebx),eax
  elif s in [0x80,0x8c]:bank,order,descriptor=0,0,0
  else:bank,order,descriptor=signed(edx),signed(eax),0
  audio.append([tick if table=='pirate'else tick+1,s,bank,order,descriptor])
 for a in SERVICES:m.u.hook_add(UC_HOOK_CODE,observed,begin=a,end=a)
 def event(action,down,scan=None):
  e=dict(tick=tick,action=action,down=down)
  if scan is not None:e['scan']=scan
  events.append(e);apply(m,e)
 start=time.monotonic()
 for tick in range(steps):
  phase=m.get(0x46c6ac);state=m.get(0x46c1b4,2)
  if phase!=lastphase:phases.append(dict(tick=tick,phase=phase,state=state));lastphase=phase
  for action in pending.pop(tick,[]):event(action,False)
  if phase==1 and tick>=200 and tick%200==0:event('enter',True);pending.setdefault(tick+1,[]).append('enter')
  elif phase==0 and tick%200==0:event('new_game',True);event('new_game',False)
  active=phase==3 and m.get(0x46c61c)==6
  if active and not initials:letters=[0x1e,0x30,0x2e,0x1c]
  if active and letters and tick%8==0:
   scan=letters.pop(0);event('key',True,scan);event('key',False,scan)
  initials=active
  x,y=struct.unpack('<ii',bytes(m.u.mem_read(0x46c15c,8)));x/=65536;y/=65536
  threshold=[440,425,455][variant];duration=[4,6,3][variant]
  firing=state==2 and y>=threshold and tick%40<duration
  targets=dict(left=firing and(x<160 or variant==1),right=firing and(x>=160 or variant==1))
  for action,down in targets.items():
   if pressed[action]!=down:event(action,down);pressed[action]=down
  m.step(tick);states.append(m.ball());samples.append(sample(m));assert m.get(0x46c67c)<=8
  if (tick+1)%10000==0:print(table,variant,tick+1,'Original',round(time.monotonic()-start,1),flush=True)
 t=dict(schema=1,table=table,case=['primary','variant-1','variant-2'][variant],tick_count=steps,inputs=events,diagnostic_shots=[],audio_tick_domain=('before-step-zero-based'if table=='pirate'else'completed-step-one-based'),states=states,audio_events=audio,**{k:[s[k]for s in samples]for k in samples[0]},phases=phases,original_reset_exact=False,executed_call_edges=[dict(callsite=hex(a),target=hex(b),count=n)for(a,b),n in sorted(m.calls.items())],policy=dict(y_threshold=threshold,pulse_steps=duration,period=40,both_flippers=variant==1),scope='Actual supported Original Retail instructions with legal keyboard actions chosen from observed ball/phase; no ball/rule/seed/timer writes. Not human play.')
 source=json.loads((ROOT/'analysis/traces/pirate-complete-game.json'if table=='pirate'else prepared/'summary.json').read_text());t.update(build_sha256=source['build_sha256'],dat_sha256=source['dat_sha256'],context_hashes=source['context_hashes'],keyboard_bindings=keyboard_bindings,configured_image_sha256=configured_context_sha256,canonical_reset_verified_before_input_configuration=True)
 output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(compact(t)+b'\n')
 boundary=ROOT/'analysis/reborn-gameplay-boundary.json';sources={}
 if boundary.exists():sources=json.loads(boundary.read_text()).get('sources',{})
 sources[str(output.relative_to(ROOT))]=dict(sha256=digest(output.read_bytes()),table=table,steps=steps,variant=variant,edges=t['executed_call_edges'])
 totals=Counter()
 for r in sources.values():
  for e in r['edges']:totals[(e['callsite'],e['target'])]+=e['count']
 boundary.write_text(json.dumps(dict(schema=1,build_sha256=t['build_sha256'],sources=sources,executed_call_edges=[dict(callsite=a,target=b,count=n)for(a,b),n in sorted(totals.items())],scope='Actual Original shared table/DMD/collision-dispatch indirect-call edges during legal-input-only playtest routes; rendering/service internals excluded from observation; no diagnostic contacts.'),indent=2)+'\n');return t

def main():
 p=argparse.ArgumentParser();p.add_argument('--table',choices=PREP,required=True);p.add_argument('--steps',type=int,default=60000);p.add_argument('--variant',type=int,choices=[0,1,2],default=0);p.add_argument('--track',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args();assert a.steps>0 and a.steps%4==0
 out=a.output or ROOT/f'build/reborn-playtest/{a.table}/{["primary","variant-1","variant-2"][a.variant]}-oracle.json';generate(a.table,a.steps,a.variant,out,a.track);print(out,flush=True)
if __name__=='__main__':main()
