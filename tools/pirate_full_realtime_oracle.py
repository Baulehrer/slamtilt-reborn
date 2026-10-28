#!/usr/bin/env python3
"""Retain nine original natural-game vectors; add directly observed magnet state."""
import json
from pirate_adventure_oracle import ROOT,BUILD_SHA,DAT_SHA,compact,digest
from pirate_campaign_magnets_oracle import Combined
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity

def main():
    case='natural-crocodile-game';path=ROOT/f'analysis/traces/pirate-{case}.json'
    f=json.loads(path.read_text());t=json.loads((ROOT/f'build/oracle/pirate-modes/{case}/trace.json').read_text());n=integrity(t,f,BUILD_SHA,DAT_SHA)
    assert n==15600 and not f['diagnostic_shots']
    m=Combined.fresh_original();keys={};states=[]
    for e in f['inputs']:keys.setdefault(e['tick'],[]).append(e)
    for tick in range(n):
        for e in keys.get(tick,[]):Combined.apply_input(m,e)
        m.dispatch_tick=tick+1;m.step(tick);sample=m.sample()
        assert m.ball()==t['states'][tick+1],('ball',tick)
        for k in KEYS[1:]:assert sample[k]==t[k][tick],(k,tick)
        states.append(sample['magnasaver_state'])
    private=ROOT/'build/oracle/pirate-full-realtime/original-magnasaver.json';private.write_bytes(compact(states)+b'\n')
    public=dict(schema=1,case=case,steps=n,build_sha256=BUILD_SHA,dat_sha256=DAT_SHA,source_fixture_sha256=digest(path.read_bytes()),
        preserved_original_vectors=9,magnasaver_state_sha256=digest(compact(states)),
        scope='Fresh original natural key-only full game; nine frozen vectors exact, five directly observed original MS fields added. No new inputs/state/waypoint writes.')
    (ROOT/'analysis/traces/pirate-full-realtime-original.json').write_text(json.dumps(public,indent=2)+'\n')
    print(n,'fresh original steps,9retained vectors+MSstate exact')
if __name__=='__main__':main()
