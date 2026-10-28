#!/usr/bin/env python3
"""Observe every Battle gate write in frozen four-/five-lock campaigns.

Bounded negative runtime evidence only; does not establish global unreachability.
Reuses already verified trajectories and executes real original handlers/ticks.
"""
import json
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.x86_const import UC_X86_REG_EIP
from pirate_multiball_oracle import Multiball
from pirate_adventure_oracle import ROOT,BUILD_SHA,DAT_SHA,compact,digest

def main():
    reports=[]
    for case in ['multiball-campaign','multiball-surplus']:
        path=ROOT/f'build/oracle/pirate-modes/{case}/trace.json';t=json.loads(path.read_text())
        m=Multiball.fresh_original();events={};shots={e['tick']:e for e in t['diagnostic_shots']};writes=[];battle_steps=0
        for e in t['inputs']:events.setdefault(e['tick'],[]).append(e)
        def observe(u,access,address,size,value,_):
            writes.append(dict(tick=tick,pc=hex(u.reg_read(UC_X86_REG_EIP)),phase=m.get(0x46c6ac),
                played=m.get(0x46e2be,2),table_mode=m.get(0x46e2c0,2),address=hex(address),size=size,value=value))
        m.u.hook_add(UC_HOOK_MEM_WRITE,observe,begin=0x46e556,end=0x46e557)
        for tick in range(t['tick_count']):
            for e in events.get(tick,[]):Multiball.apply_input(m,e)
            if tick in shots:
                e=shots[tick];m.shot(e['layer'],e['x'],e['y'],e.get('ball',0))
            m.step(tick)
            assert m.ball()==t['states'][tick+1],(case,tick,'ball')
            sample=m.sample();assert sample=={k:t[k][tick]for k in sample},(case,tick,'state')
            if m.get(0x46c6ac)==4 and m.get(0x46e2be,2)==3:
                battle_steps+=1;assert m.get(0x46e556,2)==0,(case,tick,'unexpected arming')
        assert battle_steps>1000
        battle_writes=[w for w in writes if w['phase']==4 and w['played']==3]
        assert battle_writes and all(w['value']==0 for w in battle_writes)
        reports.append(dict(case=case,trace_sha256=digest(path.read_bytes()),tick_count=t['tick_count'],
            battle_steps=battle_steps,battle_writes=battle_writes,all_gate_writes=writes))
    result=dict(schema=1,status='VERIFIED bounded original runtime observation',build_sha256=BUILD_SHA,dat_sha256=DAT_SHA,
        address='0x46e556',cases=reports,
        conclusion='Retained four- and five-lock Battle campaigns including distinct-target wraps never arm this gate. All overlapping writes are observed within these trajectories.',
        limitations=['Not proof that all possible gameplay paths are unreachable.','No inferred freestanding Battle triple-Jackpot rule; handbook does not specify one.','Diagnostic free-ball waypoints retained; no gate/rule injection.'])
    (ROOT/'analysis/traces/pirate-battle-gate-original.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Battle4/5-lock gate observed;',sum(r['battle_steps']for r in reports),'Battle steps, no arming; original state exact')
if __name__=='__main__':main()
