#!/usr/bin/env python3
"""Unchanged earned-ExtraBall prefix -> spend two credits through real drains."""
import json
from pirate_extra_threshold_oracle import Extra
from pirate_adventure_oracle import ROOT,compact,digest
from verify_pirate_multiball import KEYS
from pirate_extra_use_contracts import contracts
class Use(Extra):
    def mark(self,label):
        row=super().mark(label);row['ball_number']=self.m.get(self.m.get(0x46b758)+14,2);return row

def main():
    fpath=ROOT/'analysis/traces/pirate-extra-threshold-chain.json';g=json.loads((ROOT/'build/oracle/pirate-modes/extra-threshold-chain/trace.json').read_text())
    r=Use();events={};shots={e['tick']:e for e in g['diagnostic_shots']}
    for e in g['inputs']:events.setdefault(e['tick'],[]).append(e)
    while r.tick<3940:
        for e in events.get(r.tick,[]):r.inputs.append(e);r.apply_input(r.m,e)
        if r.tick in shots:
            e=shots[r.tick];r.shots.append(e);r.m.shot(e['layer'],e['x'],e['y'],e.get('ball',0))
        r.step();assert r.states[-1]==g['states'][r.tick]
        for key in KEYS[1:]+['magnasaver_state']:assert r.samples[-1][key]==g[key][r.tick-1]
    r.milestones=json.loads(json.dumps(g['milestones']));r.mark('two_credits_ready')
    for i in range(1,4):
        r.shot('real_drain_'+str(i),0,160,590)
        while r.m.get(0x46c6ac)!=1:r.step();assert r.tick<11000
        r.mark(f'drain_{i}_settled')
        if i<3:
            while r.m.get(0x46c1b4,2)!=2:
                if r.tick%200==0:r.key('enter',True);r.key('enter',False)
                r.step();assert r.tick<11000
    t=r.finish('extra-credit-use');t.update(prefix_steps=3940,prefix_fixture_sha256=digest(fpath.read_bytes()));summary=contracts(t)
    (ROOT/'build/oracle/pirate-modes/extra-credit-use/trace.json').write_bytes(compact(t)+b'\n')
    p=ROOT/'analysis/traces/pirate-extra-credit-use.json';f=json.loads(p.read_text());f.pop('magnasaver_state');f.update(prefix_steps=3940,prefix_fixture_sha256=t['prefix_fixture_sha256'],magnasaver_state_sha256=digest(compact(t['magnasaver_state'])));p.write_text(json.dumps(f,indent=2)+'\n')
    print(t['tick_count'],summary,flush=True)
if __name__=='__main__':main()
