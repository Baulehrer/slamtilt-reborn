#!/usr/bin/env python3
"""Frozen cap12 ladder followed by actual free-ball drain and original payout."""
import json
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP
from pirate_multiplier_ladder_oracle import Ladder
from pirate_adventure_oracle import ROOT,BUILD_SHA,DAT_SHA,compact,digest
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity
from pirate_multiplier_payout_contracts import contracts
CASE='bonus-multiplier-payout'
SCOPE=('Unchanged8524step actualSkull/righttrap cap12prefix,then onefreeball layer0 drainpoint160,590; no multiplier/bonus/score/timer/phase/callback writes. '
       'Actual original phase3 payouts andnextball reset. Diagnostic waypoint trajectory,not legal-key-only game.')
class Payout(Ladder):
    def mark(self,label):
        row=super().mark(label);g=self.m.get;player=g(0x46b758)
        row.update(bonus_base=g(player+8),ball_number=g(player+14,2),score_number=int(row['score_bcd']))
        return row

def main():
    path=ROOT/'analysis/traces/pirate-bonus-multiplier-ladder.json';f=json.loads(path.read_text())
    source=json.loads((ROOT/'build/oracle/pirate-modes/bonus-multiplier-ladder/trace.json').read_text())
    assert integrity(source,f,BUILD_SHA,DAT_SHA)==8524
    r=Payout();events={};shots={s['tick']:s for s in source['diagnostic_shots']}
    for e in source['inputs']:events.setdefault(e['tick'],[]).append(e)
    while r.tick<8524:
        for e in events.get(r.tick,[]):r.inputs.append(e);r.apply_input(r.m,e)
        if r.tick in shots:
            s=shots[r.tick];r.shots.append(s);r.m.shot(s['layer'],s['x'],s['y'])
        r.step();assert r.states[-1]==source['states'][r.tick]
        for key in KEYS[1:]+['magnasaver_state']:assert r.samples[-1][key]==source[key][r.tick-1],('prefix',r.tick,key)
    r.milestones=json.loads(json.dumps(source['milestones']));r.mark('before_cap12_drain');calls=[]
    def paid(u,pc,size,data):
        if r.m.get(0x46c6ac)==3:
            calls.append(dict(tick=r.tick+1,amount=u.reg_read(UC_X86_REG_EAX),phase=3,
                return_address=hex(r.m.get(u.reg_read(UC_X86_REG_ESP)))))
    r.m.u.hook_add(UC_HOOK_CODE,paid,begin=0x405fac,end=0x405fac)
    r.shot('cap12_drain',0,160,590)
    entered=False
    while r.m.get(0x46c6ac)!=1:
        r.step()
        if r.m.get(0x46c6ac)==3 and not entered:r.mark('bonus_entered');entered=True
        assert r.tick<12524
    assert entered;r.mark('next_ball_ready')
    trace=r.finish(CASE);trace.update(bonus_score_calls=calls,prefix_steps=8524,prefix_fixture_sha256=digest(path.read_bytes()),
        last_diagnostic_shot_tick=8524,scope=SCOPE)
    summary=contracts(trace)
    full_path=ROOT/f'build/oracle/pirate-modes/{CASE}/trace.json';full_path.write_bytes(compact(trace)+b'\n')
    public_path=ROOT/f'analysis/traces/pirate-{CASE}.json';public=json.loads(public_path.read_text());public.pop('magnasaver_state')
    public.update(bonus_score_calls=calls,prefix_steps=8524,prefix_fixture_sha256=digest(path.read_bytes()),last_diagnostic_shot_tick=8524,scope=SCOPE,
        magnasaver_state_sha256=digest(compact(trace['magnasaver_state'])))
    public_path.write_text(json.dumps(public,indent=2)+'\n')
    (ROOT/'analysis/pirate-multiplier-payout.json').write_text(json.dumps(dict(schema=1,case=CASE,status='ORIGINAL/FRESH RESET VERIFIED; native pending',
        build_sha256=BUILD_SHA,dat_sha256=DAT_SHA,steps=trace['tick_count'],prefix_steps=8524,scope=SCOPE,contract=summary,
        bonus_score_calls=calls,source_fields=dict(bonus_base='[0x46b758]+0x08',multiplier='[0x46b758]+0x12'),
        fixture=str(public_path.relative_to(ROOT)),fixture_sha256=digest(public_path.read_bytes()),
        unknown='Additional7M component observed atoriginal405fac; no invented semantic label assigned.'),indent=2)+'\n')
    print(CASE,trace['tick_count'],'original/reset10vectors',summary,calls,flush=True)
if __name__=='__main__':main()
