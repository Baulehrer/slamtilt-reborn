#!/usr/bin/env python3
"""Natural Walk the Plank and finite game via legal keys, no waypoints.

Native search only proposes keys; independent original execution and reset
replay establish the complete frozen route, including all state/hash vectors.
"""
import argparse,json
from pathlib import Path
from collections import Counter
from unicorn import UC_HOOK_CODE
from pirate_legal_cave_oracle import Legal
from pirate_adventure_oracle import ROOT,BUILD_SHA,compact,digest
from pirate_nudge_oracle import ADDRESSES as NUDGE_ADDRESSES
CASE='natural-plank-game'
class PlankLegal(Legal):
    @staticmethod
    def fresh_original():
        m=Legal.fresh_original();m.put(0x46c5ec,0x38);m.put(0x46c5f0,0xb8)
        return m
    @staticmethod
    def apply_input(m,e):
        if e['action'].startswith('nudge_'):
            scan={'nudge_left':0x38,'nudge_right':0xb8,'nudge_up':0x39}[e['action']]
            return m.run(0x40404c,0 if e['down']else 1,scan)
        return Legal.apply_input(m,e)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate',type=Path,default=ROOT/'build/oracle/pirate-natural-plank/frozen-candidate.json')
    p.add_argument('--case',default=CASE)
    p.add_argument('--boundary',default='pirate-natural-plank-boundary.json')
    p.add_argument('--continuation',choices=['right40','off'],default='right40')
    p.add_argument('--expect-rope',action='store_true')
    args=p.parse_args();case=args.case;source=args.candidate
    candidate=json.loads(source.read_text());assert candidate['diagnostic_shots']==[]
    nudge_ticks=[e['tick']for e in candidate['inputs']if e['action'].startswith('nudge_')and e['down']]
    nudge_samples=[]
    r=PlankLegal(0);g=r.m.get;keys={};held={'left':False,'right':False};edges=Counter()
    for e in candidate['inputs']:keys.setdefault(e['tick'],[]).append(e)
    def dispatch(u,address,size,_):edges[(address,g(0x46c69c))]+=1
    hook=r.m.u.hook_add(UC_HOOK_CODE,dispatch,begin=0x407c09,end=0x407c09)
    old_arm=0;entered=False;released=False;returned=False;ropes=None;hits=[]
    def mark(label):
        v=r.mark(label);v.update(adventure=g(0x46e2c0,2),arm=g(0x46e2de,2),
            ropes=[g(0x46e564+i,1)for i in range(5)],timer=g(0x46e546,2),
            super_ready=g(0x46e556,2));return v
    def observe():
        nonlocal old_arm,entered,released,returned,ropes
        arm=g(0x46e2de,2);phase=g(0x46c6ac)
        if nudge_ticks and min(nudge_ticks)<r.tick<=max(nudge_ticks)+96:
            nudge_samples.append([g(a,1 if a==0x46c610 else 4)for a in NUDGE_ADDRESSES])
        if arm and not old_arm and not entered:mark('natural_adventure_armed')
        if phase==5 and not entered:
            entered=True;assert g(0x46e2c0,2)==0;mark('plank_entered')
        if entered and not released and phase==5 and g(0x46c1b4,2)==2:
            released=True;mark('plank_free_ball')
        now=[g(0x46e564+i,1)for i in range(5)]
        if phase==5 and ropes is not None:
            for i in range(5):
                if ropes[i]==1 and now[i]==0:
                    v=mark('natural_rope_'+str(i));v['rope']=i;hits.append(v)
        if entered and not returned and phase!=5:returned=True;mark('plank_return')
        old_arm=arm;ropes=now if phase==5 else None
    def event(e):
        r.inputs.append(e);r.apply_input(r.m,e)
        if e['action']in held:held[e['action']]=e['down']
    for tick in range(candidate['tick_count']):
        for e in keys.get(tick,[]):event(e)
        r.step();observe()
    assert entered and r.tick==candidate['tick_count']
    # Continue the same discovered periodic right-flipper input during Plank.
    # After the mode, release both flippers for a bounded ordinary finite game.
    letters=[0x1e,0x30,0x2e,0x1c];admitted=False
    while g(0x46c6ac)!=0:
        target={'left':False,'right':bool((r.tick//40)%2==0)if not returned and args.continuation=='right40'else False}
        for side,down in target.items():
            if down!=held[side]:event(dict(tick=r.tick,action=side,down=down))
        if g(0x46c6ac)==1 and r.tick%200==0:r.event('enter');r.event('enter',False)
        if g(0x46c6ac)==3 and g(0x46c61c)==6:
            if not admitted:mark('initials_admitted');admitted=True
            if r.tick%4==0 and letters:r.event('key',scan=letters.pop(0))
        r.step();observe();assert r.tick<32000,('finite game',g(0x46c6ac))
    assert released and returned and admitted and not letters
    if args.expect_rope:assert hits,'No actual natural rope hit'
    mark('game_over');records=bytes(r.m.u.mem_read(0x46c542,50));frozen=r.m.ball()
    for _ in range(64):r.step();assert g(0x46c6ac)==0 and r.m.ball()==frozen
    mark('game_over_stable');r.event('new_game');mark('new_game')
    assert g(0x46e2bc,2)==g(0x46e2be,2)==0 and bytes(r.m.u.mem_read(0x46c542,50))==records
    start=r.tick
    while r.tick-start<1200 or g(0x46c1b4,2)!=2:
        if g(0x46c6ac)==1 and r.tick%200==0:r.event('enter');r.event('enter',False)
        r.step();assert r.tick-start<4000
    mark('second_game_running');assert g(0x46c6ac)==2
    r.m.u.hook_del(hook)
    for e,n in edges.items():r.m.calls[e]+=n
    t=r.finish(case);meta=dict(scope=__doc__,key_only=True,candidate_sha256=digest(source.read_bytes()),
        source_policy=candidate['policy'],source_native_steps=candidate['tick_count'],natural_ropes=hits,
        call_edge_coverage='Full DMD dispatcher; fresh original reset replay of all state/hash vectors. No checkpoint/diagnostic shots.')
    if nudge_ticks:meta['nudge_window']=dict(start_tick=min(nudge_ticks)+1,fields=[hex(a)for a in NUDGE_ADDRESSES],states=nudge_samples)
    t.update(meta);(ROOT/f'build/oracle/pirate-modes/{case}/trace.json').write_bytes(compact(t)+b'\n')
    path=ROOT/f'analysis/traces/pirate-{case}.json';f=json.loads(path.read_text());f.update(meta);path.write_text(json.dumps(f,indent=2)+'\n')
    (ROOT/'analysis'/args.boundary).write_text(json.dumps(dict(build_sha256=BUILD_SHA,gameplay_stubs=[],executed_call_edges=t['executed_call_edges']),indent=2)+'\n')
if __name__=='__main__':main()
