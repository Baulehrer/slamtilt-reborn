#!/usr/bin/env python3
"""Actual Skull ramps/right trap earn original1/2/4/6/8/10/12 ladder, nofield writes."""
import json
from pirate_final_feedback_b_oracle import FinalFeedbackB
from pirate_campaign_magnets_oracle import Combined
from pirate_adventure_oracle import ROOT,BUILD_SHA,DAT_SHA,compact,digest
from pirate_multiplier_ladder_contracts import contracts

CASE='bonus-multiplier-ladder'
SCOPE=('Original free-ball DAT Skull/right-trap contacts only; no multiplier/progress/score/phase/timer/callback writes. '
       'Full ladder and capped-repeat/unlit-trap guard. Not a legal-key-only game; bonus-drain payout excluded to keep bounded under10000steps.')
class Ladder(FinalFeedbackB):
    fresh_original=staticmethod(Combined.fresh_original)
    def mark(self,label):
        row=super().mark(label);g=self.m.get;player=g(0x46b758)
        row.update(pending_extra=g(0x46e2d8,2),extra_credits=g(player+16,2))
        return row
    def cooldown(self):
        # A real elapsed interval, not capture-clock injection. Repeated immediate
        # right-trap entry after release is correctly inhibited by original code.
        for _ in range(60):self.park()

def main():
    r=Ladder();r.initial();rows=[]
    for stage in range(6):
        before=r.fields()['multiplier'];hits=0
        while r.m.get(0x46e54e,2)!=65535:
            hits+=1;r.ramp(f'stage_{stage}_skull_{hits}',4);r.free();r.mark(f'stage_{stage}_skull_{hits}_settled')
            assert hits<=8 and r.tick<9000
        r.mark(f'stage_{stage}_armed');r.cooldown();r.ramp(f'stage_{stage}_right_trap',0);r.free();r.mark(f'stage_{stage}_collected')
        after=r.fields()['multiplier'];assert after>before
        rows.append(dict(stage=stage,before=before,after=after,skull_hits=hits,tick=r.tick))
    assert r.fields()['multiplier']==12
    for n in range(1,18):
        r.ramp(f'capped_skull_{n}',4);r.free();r.mark(f'capped_skull_{n}_settled')
    r.cooldown();before=len([e for e in r.registrations if e['address']=='0x437247'])
    r.ramp('unlit_cap_trap',0);r.free();r.mark('unlit_cap_trap_collected')
    delta=len([e for e in r.registrations if e['address']=='0x437247'])-before
    trace=r.finish(CASE);trace.update(ladder_stages=rows,cap_trap_registration_delta=delta,scope=SCOPE)
    summary=contracts(trace)
    path=ROOT/f'build/oracle/pirate-modes/{CASE}/trace.json';path.write_bytes(compact(trace)+b'\n')
    public_path=ROOT/f'analysis/traces/pirate-{CASE}.json';public=json.loads(public_path.read_text());public.pop('magnasaver_state')
    public.update(ladder_stages=rows,cap_trap_registration_delta=delta,scope=SCOPE,magnasaver_state_sha256=digest(compact(trace['magnasaver_state'])))
    public_path.write_text(json.dumps(public,indent=2)+'\n')
    (ROOT/'analysis/pirate-multiplier-ladder.json').write_text(json.dumps(dict(schema=1,case=CASE,status='ORIGINAL/FRESH RESET VERIFIED; native pending',
        build_sha256=BUILD_SHA,dat_sha256=DAT_SHA,steps=trace['tick_count'],contract=summary,scope=SCOPE,
        handbook=dict(source='build/manual-rules/pirate.txt',lines='27..34',printed_page=14),
        original_fields=dict(multiplier='[0x46b758]+0x12',armed='46e54e',skull_progress='46e526'),
        collection='437214..437225 table465c3c computes next multiplier; no forced successiveintegers',
        fixture=str(public_path.relative_to(ROOT)),fixture_sha256=digest(public_path.read_bytes()),stages=rows),indent=2)+'\n')
    print(CASE,trace['tick_count'],'original/reset10vectors',summary,flush=True)
if __name__=='__main__':main()
