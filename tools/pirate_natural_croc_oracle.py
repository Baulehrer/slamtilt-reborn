#!/usr/bin/env python3
"""Natural Cave->cannon->Crocodile->finite game through legal actions only.

A silent native reachable-state search proposes inputs. This proof executes
fresh original Retail from reset twice; no checkpoints/waypoints/state writes.
"""
import json
from collections import Counter
from unicorn import UC_HOOK_CODE
from pirate_legal_cave_oracle import Legal
from pirate_adventure_oracle import ROOT,BUILD_SHA,compact,digest
CASE='natural-crocodile-game'

def main():
    source=ROOT/'build/oracle/pirate-natural-croc/frozen-candidate.json';candidate=json.loads(source.read_text())
    assert candidate['policy']['multiball']and candidate['diagnostic_shots']==[]
    r=Legal(0);keys={};g=r.m.get;prefix=json.loads((ROOT/'build/oracle/pirate-modes/legal-cave-game/trace.json').read_text());edges=Counter();copies=[]
    for e in candidate['inputs']:keys.setdefault(e['tick'],[]).append(e)
    def dispatch(u,address,size,_):edges[(address,g(0x46c69c))]+=1
    hook=r.m.u.hook_add(UC_HOOK_CODE,dispatch,begin=0x407c09,end=0x407c09)
    old=(0,1,0,0);seen=set();awards=[]
    def observe():
        nonlocal old
        now=(g(0x46e2bc,2),g(0x46c6ac),g(0x46c67c),g(0x46e298))
        if now[0]>old[0]and now[0]<=2:r.mark('natural_lock_'+str(now[0]))
        if now[1]==6 and 'cannon'not in seen:seen.add('cannon');r.mark('cannon_entered')
        if now[1]==4 and 'multiball'not in seen:seen.add('multiball');r.mark('crocodile_entered')
        if now[1]==4 and now[2]==2 and all(g(0x46c15c+100*i+0x58,2)==2 for i in range(2))and 'released'not in seen:
            seen.add('released');r.mark('two_free_balls')
        if now[1]==4 and now[3]>old[3]:
            mark=r.mark('natural_jackpot_'+str(len(awards)+1));mark['collected_delta']=now[3]-old[3];awards.append(mark)
        if old[2]==2 and now[2]==1 and 'compacted'not in seen:
            seen.add('compacted');r.mark('single_ball_compacted')
        if 'multiball'in seen and now[1]==2 and now[2]==1 and 'returned'not in seen:
            seen.add('returned');r.mark('normal_return')
        old=now
    for tick in range(candidate['tick_count']):
        for e in keys.get(tick,[]):r.inputs.append(e);r.apply_input(r.m,e)
        r.step();observe()
        if r.tick<=5400:
            assert r.states[-1]==prefix['states'][r.tick]
            assert r.samples[-1]=={k:prefix[k][r.tick-1]for k in r.samples[-1]},('earned prefix',r.tick)
    assert 'multiball'in seen and 'cannon'in seen
    assert next(m for m in r.milestones if m['label']=='cannon_entered')['tick']==candidate['policy']['cannon_tick']
    r.mark('native_candidate_end');letters=[0x1e,0x30,0x2e,0x1c];admitted=False
    while g(0x46c6ac)!=0:
        if g(0x46c6ac)==1 and r.tick%200==0:r.event('enter');r.event('enter',False)
        if g(0x46c6ac)==3 and g(0x46c61c)==6:
            if not admitted:r.mark('initials_admitted');admitted=True
            if r.tick%4==0 and letters:r.event('key',scan=letters.pop(0))
        r.step();observe();assert r.tick<24000,('finite end',g(0x46c6ac),g(0x46c67c))
    assert awards,'No actual jackpot collected'
    assert {'cannon','multiball','released','compacted','returned'}<=seen and admitted and not letters
    r.mark('game_over');records=bytes(r.m.u.mem_read(0x46c542,50));frozen=r.m.ball()
    for _ in range(64):r.step();assert g(0x46c6ac)==0 and r.m.ball()==frozen
    r.mark('game_over_stable');r.event('new_game');r.mark('new_game')
    assert g(0x46e2bc,2)==g(0x46e2be,2)==0 and bytes(r.m.u.mem_read(0x46c542,50))==records
    start=r.tick
    while r.tick-start<1200 or g(0x46c1b4,2)!=2:
        if g(0x46c6ac)==1 and r.tick%200==0:r.event('enter');r.event('enter',False)
        r.step();assert r.tick-start<4000
    r.mark('second_game_running');assert g(0x46c6ac)==2
    r.m.u.hook_del(hook)
    for e,n in edges.items():r.m.calls[e]+=n
    t=r.finish(CASE);t.update(scope=__doc__,key_only=True,candidate_sha256=digest(source.read_bytes()),source_policy=candidate['policy'],prefix_case='legal-cave-game',prefix_ticks=5400,
        source_native_steps=candidate['tick_count'],natural_jackpots=awards,call_edge_coverage='Full DMD dispatcher only; original simulation/hash vectors and independent reset replay complete.')
    (ROOT/f'build/oracle/pirate-modes/{CASE}/trace.json').write_bytes(compact(t)+b'\n')
    p=ROOT/f'analysis/traces/pirate-{CASE}.json';f=json.loads(p.read_text())
    for k in ['scope','key_only','candidate_sha256','source_policy','prefix_case','prefix_ticks','source_native_steps','natural_jackpots','call_edge_coverage']:f[k]=t[k]
    p.write_text(json.dumps(f,indent=2)+'\n')
    (ROOT/'analysis/pirate-natural-croc-boundary.json').write_text(json.dumps(dict(build_sha256=BUILD_SHA,gameplay_stubs=[],executed_call_edges=t['executed_call_edges']),indent=2)+'\n')
if __name__=='__main__':main()
