#!/usr/bin/env python3
"""Retail keyboard-to-nudge/Tilt fixtures; no rule-state injection.

Three mode cases reuse frozen, explicitly diagnostic physical-entry prefixes.
Only default key bindings are configured; each fixture independently replays
all original key handlers, full ticks, lamps and integer pool compaction.
"""
import json
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESP
from pirate_adventure_oracle import Original,ROOT,BUILD_SHA,compact,digest
from pirate_modes_oracle import Recorder

ADDRESSES=[0x454aac,0x454aa8,0x454ab0,0x454af8,0x454afc,0x46c600,0x46c604,
    0x46c4a4,0x46c5f8,0x46c5f4,0x46c6e4,0x46b764,0x46c6d0,0x46c6d4,
    0x454b58,0x454b5c,0x454b60,0x46c610]
SCANS=dict(enter=0x1c,left=0x2a,right=0x36,nudge_left=0x38,nudge_right=0xb8,nudge_up=0x39)
CASES=['left','right','up','warning','decay','prelaunch','tilt-game','tilt-knife','tilt-magna','tilt-crocodile','tilt-held-magna','tilt-held-crocodile']

class NudgeOriginal(Original):
    def __init__(self):
        super().__init__(ROOT/'build/oracle/pirate-full-tick')
        for a,v in [(0x46c5dc,0x2a),(0x46c5e0,0x36),(0x46c5ec,0x38),(0x46c5f0,0xb8)]:self.put(a,v)
    def sample(self):
        return dict(super().sample(),nudge=[self.get(a,1 if a==0x46c610 else 4)for a in ADDRESSES])

class Nudge(Recorder):
    @staticmethod
    def fresh_original():return NudgeOriginal()
    @staticmethod
    def apply_input(m,e):
        m.run(0x40404c,0 if e['down']else 1,SCANS[e['action']])
    def key(self,action,down=True):
        e=dict(tick=self.tick,action=action,down=down);self.inputs.append(e);self.apply_input(self.m,e)
    def mark(self,label):
        value=super().mark(label);value['nudge']=self.m.sample()['nudge'];return value

def generate(case):
    r=Nudge(0);events={};start=600;end=900
    def schedule(t,action,down=True):events.setdefault(t,[]).append(dict(tick=t,action=action,down=down))
    for t,down in [(200,True),(201,False)]:schedule(t,'enter',down)
    prefix=None
    if case.startswith('tilt-')and case!='tilt-game':
        source,start={'tilt-knife':('knife-success',2112),'tilt-magna':('magna-natural-both',1352),'tilt-crocodile':('crocodile',3146),'tilt-held-magna':('magna-natural-both',1261),'tilt-held-crocodile':('crocodile',2407)}[case]
        prefix=json.loads((ROOT/f'build/oracle/pirate-modes/{source}/trace.json').read_text())
        events={}
        for e in prefix['inputs']:
            if e['tick']<start:events.setdefault(e['tick'],[]).append(e)
        r.shots=[e for e in prefix['diagnostic_shots']if e['tick']<start]
    if case in ('left','right','up'):
        schedule(start,'nudge_'+case);schedule(start+1,'nudge_'+case,False)
    elif case=='warning':
        schedule(600,'nudge_left');schedule(604,'nudge_right');end=1200
    elif case=='decay':
        for i,d in enumerate(['left','right','up']):schedule(600+i*200,'nudge_'+d)
        end=1400
    elif case=='prelaunch':
        for t,d in [(0,'left'),(4,'right'),(8,'up')]:schedule(t,'nudge_'+d)
        end=800
    else:
        held={side:False for side in ['left','right']}
        if prefix:
            for e in prefix['inputs']:
                if e['tick']<start and e['action']in held:held[e['action']]=e['down']
        for side in held:
            if not held[side]:schedule(start if prefix else start-2,side)
        for i,d in enumerate(['left','right','up','left']):schedule(start+i*4,'nudge_'+d)
        for t,down in [(start+20,False),(start+24,True),(start+28,False)]:
            for side in ['left','right']:schedule(t,side,down)
        end=6000 if case=='tilt-game'else start+4500
    shots={e['tick']:e for e in r.shots};warnings=[];edges=Counter()
    def callback(u,address,size,_):
        target=r.m.get(u.reg_read(UC_X86_REG_EDX)+4)
        warnings.append(dict(tick=r.tick,target=hex(target),argument=u.reg_read(UC_X86_REG_EAX),counter=r.m.get(0x46c6e4)))
        edges[(address,target)]+=1
    hook=r.m.u.hook_add(UC_HOOK_CODE,callback,begin=0x405fa1,end=0x405fa1)
    # A nudged Knife exit can reach the original service+74 flipper response
    # after the short general call window. Observe only that concrete entry.
    entry_edges=Counter()
    def response(u,address,size,_):
        ret=r.m.get(u.reg_read(UC_X86_REG_ESP))
        assert bytes(u.mem_read(ret-3,3)) in (bytes.fromhex('ff5374'),bytes.fromhex('ff5378'))
        entry_edges[(ret-3,address)]+=1
    response_hooks=[r.m.u.hook_add(UC_HOOK_CODE,response,begin=a,end=a)for a in [0x40ac08,0x40ab64]]
    auto_launch=0
    while r.tick<end:
        if r.tick==start:r.m.track_calls()
        if r.tick==start+300:r.m.pause_calls()
        if case=='tilt-game'and r.tick>start+100 and r.m.get(0x46c6ac)==1 and r.tick-auto_launch>=200:
            r.key('enter');schedule(r.tick+1,'enter',False);auto_launch=r.tick
        for e in events.get(r.tick,[]):r.inputs.append(e);r.apply_input(r.m,e)
        if r.tick in shots:
            s=shots[r.tick];r.m.shot(s['layer'],s['x'],s['y'],s.get('ball',0))
        if r.tick in [start,start+4,start+8,start+12,start+24]:r.mark('input_'+str(r.tick))
        r.step()
        if prefix and r.tick<=start:
            for key in ['states','timing','lifecycle','rule_sha256','video_sha256','ball_pool_sha256','dmd_sha256','lamp_sha256','highscore_sha256']:
                if key not in prefix:continue
                actual=r.states[-1]if key=='states'else r.samples[-1][key]
                assert actual==prefix[key][r.tick if key=='states'else r.tick-1],(case,r.tick,key)
    r.mark('settled');r.m.u.hook_del(hook)
    for h in response_hooks:r.m.u.hook_del(h)
    r.m.calls.update(edges)
    for edge,count in entry_edges.items():r.m.calls[edge]=max(r.m.calls[edge],count)
    trace=r.finish('nudge-'+case)
    trace.update(scope=__doc__,nudge_addresses=[hex(a)for a in ADDRESSES],warning_calls=warnings,
        prefix_ticks=start if prefix else 0)
    folder=ROOT/'build/oracle/pirate-modes'/('nudge-'+case)
    (folder/'trace.json').write_bytes(compact(trace)+b'\n')
    p=ROOT/f'analysis/traces/pirate-nudge-{case}.json';f=json.loads(p.read_text());f.pop('nudge',None)
    for key in ['scope','nudge_addresses','warning_calls','prefix_ticks']:f[key]=trace[key]
    f['nudge_sha256']=digest(compact(trace['nudge']));p.write_text(json.dumps(f,indent=2)+'\n')
    print(case,'warnings',warnings,'phases',sorted(set(s[7]for s in trace['timing'])),'tilt-final',trace['nudge'][-1][11],flush=True)
    return r.m.calls

def main():
    edges=Counter()
    for case in CASES:edges.update(generate(case))
    (ROOT/'analysis/pirate-nudge-boundary.json').write_text(json.dumps(dict(build_sha256=BUILD_SHA,
        gameplay_stubs=[],executed_call_edges=[dict(callsite=hex(a),target=hex(b),count=n)for(a,b),n in sorted(edges.items())]),indent=2)+'\n')
if __name__=='__main__':main()
