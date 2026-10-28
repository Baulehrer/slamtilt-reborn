#!/usr/bin/env python3
"""Actual five ropes -> upper trap -> register-pushed30M Plank feedback."""
import json
from pirate_campaign_magnets_oracle import Combined
from pirate_adventure_oracle import ROOT,BUILD_SHA,compact,digest

def main():
    r=Combined();r.events=[];r.enter();r.idle()
    for ident in [4,2,3,1,0]:
        r.ramp('rope_'+str(ident),ident);r.free();r.idle()
    assert r.m.get(0x46e556,2)==1 and list(r.m.u.mem_read(0x46e564,5))==[0]*5
    r.mark('five_ropes_super_lit')
    r.admit('plank_30m_super',0x42eb6c,lambda:(r.shot('upper_trap',0,86,10),r.free()))
    r.free();r.mark('returned');assert r.m.get(0x46c6ac)==2 and r.m.get(0x46e2c0,2)==1
    t=r.finish('plank-super-feedback');t.update(feedback_events=r.events)
    (ROOT/'build/oracle/pirate-modes/plank-super-feedback/trace.json').write_bytes(compact(t)+b'\n')
    p=ROOT/'analysis/traces/pirate-plank-super-feedback.json';f=json.loads(p.read_text());f.pop('magnasaver_state');f.update(feedback_events=r.events,magnasaver_state_sha256=digest(compact(t['magnasaver_state'])));p.write_text(json.dumps(f,indent=2)+'\n')
    boundary=dict(schema=1,build_sha256=BUILD_SHA,cases=['plank-super-feedback'],gameplay_stubs=[],
        executed_call_edges=[dict(callsite=hex(a),target=hex(b),count=n)for(a,b),n in sorted(r.m.calls.items())],
        scope='Actual DAT five ropes/upper trap,407c09 original30M callback; declaredfreeballwaypoints only,no score/rule/priority/timer writes. Registerdefinition432388,push432390,request4323c8.')
    (ROOT/'analysis/pirate-plank-super-feedback-boundary.json').write_text(json.dumps(boundary,indent=2)+'\n')
    print('plank-super-feedback',t['tick_count'],r.events,flush=True)
if __name__=='__main__':main()
