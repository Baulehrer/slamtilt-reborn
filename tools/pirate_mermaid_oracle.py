#!/usr/bin/env python3
"""Earned Magna reward -> repeated Mermaid collection -> two physical drains."""
import argparse,json
from pirate_mermaid_probe import Mermaid
from pirate_adventure_oracle import ROOT,BUILD_SHA,DAT_SHA,compact,digest
from verify_pirate_multiball import KEYS
from pirate_mermaid_contracts import contracts
CASES={'base':None,'growth-2m':8,'growth-3m':9,'hold-bonus':4,'hold-tilt':4,'hold-tilt-combo':4,'hold-multiplier':4}
SCOPE='Actual Enter, reused actual Magna reward prefix and diagnostic FREE-ball DAT contacts; natural captures/drains/bonus. No score/rule/timer/phase/capture writes. Not legal-key-only all-feature acceptance.'
def generate(case):
    r=Mermaid();award=CASES[case];prefix=None
    if award is None:r.initial()
    else:
        prefix=f'magna-award-{award}';path=ROOT/f'build/oracle/pirate-modes/{prefix}/trace.json';t=json.loads(path.read_text());keys={};shots={e['tick']:e for e in t['diagnostic_shots']}
        for e in t['inputs']:keys.setdefault(e['tick'],[]).append(e)
        while r.tick<t['tick_count']:
            for e in keys.get(r.tick,[]):r.inputs.append(e);r.apply_input(r.m,e)
            if r.tick in shots:
                e=shots[r.tick];r.shots.append(e);r.m.shot(e['layer'],e['x'],e['y'],e.get('ball',0))
            r.step();assert r.states[-1]==t['states'][r.tick]
            for key in KEYS[1:]:assert r.samples[-1][key]==t[key][r.tick-1],(prefix,r.tick,key)
    r.mark('reward_ready');r.free();r.idle()
    if case=='hold-multiplier':
        for i in range(2):r.ramp('skull_multiplier_'+str(i),4);r.free();r.idle()
        r.ramp('right_trap_multiplier',0);r.free();r.idle();r.mark('multiplier_earned')
        assert r.m.get(r.m.get(0x46b758)+18,2)==2
    for i in range(2):
        r.mark(f'collection_{i+1}_before');r.shot(f'mermaid_trap_{i+1}',0,291,311);r.free();r.mark(f'collection_{i+1}_after');r.idle()
    if case=='hold-tilt-combo':
        for i in range(3):r.ramp('earned_combo_'+str(i),1)
        r.mark('combos_earned')
    if case.startswith('hold-tilt'):
        for action in ['nudge_left','nudge_right','nudge_up']:
            r.key(action,True);r.key(action,False)
            for _ in range(4):r.step()
        assert r.m.get(0x46b764)!=0;r.mark('tilt_reached')
    r.drain('drain_1');r.launch()
    r.mark('collection_3_before');r.shot('next_ball_mermaid',0,291,311);r.free();r.mark('collection_3_after');r.idle()
    r.drain('drain_2')
    if case=='growth-3m':
        r.launch();r.shot('last_ball_drain',0,160,590);start=r.tick;letters=[0x1e,0x30,0x2e,0x1c]
        while r.m.get(0x46c6ac)!=0:
            if r.m.get(0x46c6ac)==3 and r.m.get(0x46c61c)==6 and letters and r.tick%4==0:
                e=dict(tick=r.tick,action='key',scan=letters.pop(0),down=True);r.inputs.append(e);r.apply_input(r.m,e)
            r.step();assert r.tick-start<7000
        r.mark('game_over');r.key('new_game',True);r.mark('new_game_bank_reset')
    name='mermaid-'+case;t=r.finish(name);t.update(mermaid_case=case,prefix_case=prefix,bonus_score_calls=r.payments,scope=SCOPE);contracts(t)
    (ROOT/f'build/oracle/pirate-modes/{name}/trace.json').write_bytes(compact(t)+b'\n')
    p=ROOT/f'analysis/traces/pirate-{name}.json';f=json.loads(p.read_text());f.pop('magnasaver_state');f.update(mermaid_case=case,prefix_case=prefix,bonus_score_calls=r.payments,scope=SCOPE,magnasaver_state_sha256=digest(compact(t['magnasaver_state'])));p.write_text(json.dumps(f,indent=2)+'\n')
    print('FINISHED',name,t['tick_count'],r.payments,flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cases',nargs='+',default=list(CASES));a=p.parse_args()
    for c in a.cases:generate(c)
