#!/usr/bin/env python3
"""Missing Pirate lock-count combinations through original physical events.

Crocodile3/4 and Storm4 close the existing minimum/maximum matrix. Waypoints
move only free balls; cannon uses original keys/flight. No rule-state writes.
"""
import json
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBP
from pirate_surplus_oracle import Surplus
from pirate_adventure_oracle import ROOT,BUILD_SHA,compact,digest
CASES=[('locks-crocodile-3',1,3,7500000),('locks-crocodile-4',1,4,10000000),('locks-storm-4',2,4,12500000)]


def generate(case,ordinal,locks,expected):
    prefix='crocodile'if ordinal==2 else None
    r=Surplus.resume(prefix)if prefix else Surplus(0)
    if not prefix:r.initial();r.compactions=[]
    r.m.pause_calls();r.stage=case;g=r.m.get;prefix_ticks=r.tick if prefix else 0
    if not prefix:
        def copied(u,pc,size,_):
            i=u.reg_read(UC_X86_REG_EAX);count=u.reg_read(UC_X86_REG_EBP)
            src=bytes(u.mem_read(0x46c15c+100*count,100));dst=bytes(u.mem_read(0x46c15c+100*i,100));assert src==dst
            r.compactions.append(dict(tick=r.tick+1,stage=r.stage,index=i,old_count=count+1,new_count=count,
                source_sha256=digest(src),destination_sha256=digest(dst)))
        r.m.u.hook_add(UC_HOOK_CODE,copied,begin=0x4086c1,end=0x4086c1)
    r.mark('prepare');assert g(0x46e2be,2)==ordinal-1 and g(0x46e2bc,2)==0
    for i in range(locks):r.cave(f'lock_{i+1}')
    assert g(0x46e2bc,2)==locks
    result=r.cannon();assert result['phase']==4 and result['played_multiballs']==ordinal
    r.mark('mode_entered');start=r.tick
    while g(0x46e55e,2)or g(0x46c67c)<locks or any(g(0x46c15c+100*i+0x58,2)!=2 for i in range(g(0x46c67c))):
        r.wait_step(park=True,exclude=-1);assert r.tick-start<9000
    r.mark('all_balls_released');assert g(0x46c67c)==locks and g(0x46e2a0)==expected
    # Storm progresses even on an unlit hit. Crocodile's chosen target rotates
    # on the original timer, so query it just before each physical shot.
    target=g(0x46e538,2)if ordinal==1 else 0
    r.mark('before_jackpot');r.ramp('first_jackpot',target);r.mark('after_jackpot')
    r.mark('before_growth');r.cave('jackpot_growth');r.mark('after_growth')
    assert g(0x46e2a0)==expected+1000000
    target=g(0x46e538,2)if ordinal==1 else next(i for i in range(5)if g(0x46e569+i,1))
    r.mark('before_raised');r.ramp('raised_jackpot',target);r.mark('after_raised')
    r.drain();assert g(0x46c67c)==1 and g(0x46c6ac)==2
    trace=r.finish(case);trace.update(scope=__doc__,prefix_case=prefix,prefix_ticks=prefix_ticks,
        ordinal=ordinal,lock_count=locks,initial_jackpot=expected,compactions=r.compactions,
        call_edge_coverage='Actual event steps only; waits/parking unhooked; all state independently replayed from reset.')
    (ROOT/f'build/oracle/pirate-modes/{case}/trace.json').write_bytes(compact(trace)+b'\n')
    p=ROOT/f'analysis/traces/pirate-{case}.json';f=json.loads(p.read_text())
    for k in ['scope','prefix_case','prefix_ticks','ordinal','lock_count','initial_jackpot','compactions','call_edge_coverage']:f[k]=trace[k]
    p.write_text(json.dumps(f,indent=2)+'\n')
    return trace


def main():
    edges=Counter()
    for spec in CASES:
        for e in generate(*spec)['executed_call_edges']:edges[(e['callsite'],e['target'])]+=e['count']
    (ROOT/'analysis/pirate-lock-matrix-boundary.json').write_text(json.dumps(dict(build_sha256=BUILD_SHA,
        gameplay_stubs=[],executed_call_edges=[dict(callsite=a,target=b,count=n)for(a,b),n in sorted(edges.items())]),indent=2)+'\n')
if __name__=='__main__':main()
