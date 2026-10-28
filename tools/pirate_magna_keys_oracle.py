#!/usr/bin/env python3
"""Independent original proof of searched key-only Magna flight/reward/return.

Frozen diagnostic table entry only; from top trap1209 onward, movement and
capture are original simulation + legal Shift edges, no physical waypoints.
"""
import json
from pirate_magna_oracle import Magna
from pirate_adventure_oracle import ROOT,BUILD_SHA,compact
CASE='magna-key-reward'

def main():
    source=json.loads((ROOT/'build/oracle/pirate-magna-key-search/best-candidate.json').read_text())
    prefix=json.loads((ROOT/'build/oracle/pirate-modes/magna-natural-both/trace.json').read_text())
    r=Magna(0);keys={};shots={e['tick']:e for e in source['diagnostic_shots']}
    for e in source['inputs']:keys.setdefault(e['tick'],[]).append(e)
    r.inputs=source['inputs'];r.shots=source['diagnostic_shots'];rewarded=False
    wanted={1352:'field_released',1820:'natural_award',1970:'natural_return'}
    for tick in range(source['tick_count']):
        for e in keys.get(tick,[]):r.apply_input(r.m,e)
        if tick in shots:
            e=shots[tick];r.m.shot(e['layer'],e['x'],e['y'],e.get('ball',0))
        if tick==1819:r.mark('before_award');r.m.track_calls()
        r.step()
        if tick==1819:r.m.pause_calls()
        if r.tick<=1352:
            assert r.states[-1]==prefix['states'][r.tick]
            assert r.samples[-1]=={k:prefix[k][r.tick-1]for k in r.samples[-1]},('prefix',r.tick)
        if r.tick in wanted:r.mark(wanted[r.tick])
        if r.m.get(0x46c1b4,2)==3 and r.m.get(0x46c1b6,2)==6 and not rewarded:
            assert r.tick==1820;r.mark('first_reward_capture');rewarded=True
    assert rewarded and r.m.get(0x46c1b4,2)==2 and r.m.get(0x46e542,2)==0
    assert not any(e['tick']>=1209 for e in r.shots if e['label']!='top_trap')
    trace=r.finish(CASE);trace.update(scope=__doc__,prefix_ticks=1352,natural_flight_ticks=468,
        reward_tick=1820,return_tick=1970,call_edge_coverage='Only actual natural capture step observed; full original state independently replayed from reset.')
    folder=ROOT/'build/oracle/pirate-modes'/CASE;(folder/'trace.json').write_bytes(compact(trace)+b'\n')
    path=ROOT/f'analysis/traces/pirate-{CASE}.json';f=json.loads(path.read_text())
    for key in ['scope','prefix_ticks','natural_flight_ticks','reward_tick','return_tick','call_edge_coverage']:f[key]=trace[key]
    path.write_text(json.dumps(f,indent=2)+'\n')
    (ROOT/'analysis/pirate-magna-keys-boundary.json').write_text(json.dumps(dict(build_sha256=BUILD_SHA,
        gameplay_stubs=[],executed_call_edges=trace['executed_call_edges']),indent=2)+'\n')
if __name__=='__main__':main()
