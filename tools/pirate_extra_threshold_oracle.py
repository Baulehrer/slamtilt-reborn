#!/usr/bin/env python3
"""Actual combo counts25/50 -> pending extra balls -> right trap redemption."""
import json
from unicorn import UC_HOOK_CODE
from pirate_campaign_magnets_oracle import Combined
from pirate_adventure_oracle import ROOT,BUILD_SHA,DAT_SHA,compact,digest
from pirate_extra_threshold_contracts import contracts
CASE='extra-threshold-chain'
SCOPE='Original free-ball DAT left-ramp/right-trap contacts; no count/threshold/credit/score/phase/timer/callback writes. Not a legal-key-only game.'
class Extra(Combined):
    def __init__(self):
        super().__init__();self.earns=[];self.redemptions=[]
        def earn(u,pc,size,data):
            self.earns.append(dict(tick=self.tick+1,count=self.m.get(self.m.get(0x46b758)+12,2),old_threshold=self.m.get(0x46e2da,2)))
        def redeem(u,pc,size,data):self.redemptions.append(dict(tick=self.tick+1,pending_before=self.m.get(0x46e2d8,2)))
        self.m.u.hook_add(UC_HOOK_CODE,earn,begin=0x43534a,end=0x43534a)
        self.m.u.hook_add(UC_HOOK_CODE,redeem,begin=0x43739b,end=0x43739b)
    def mark(self,label):
        row=super().mark(label);g=self.m.get
        row.update(combo_count=g(g(0x46b758)+12,2),extra_credits=g(g(0x46b758)+16,2))
        return row
    def wait(self,n=8):
        for _ in range(n):self.park()

def main():
    r=Extra();r.initial();r.mark('initial');g=r.m.get;player=g(0x46b758)
    attempts=0
    while g(player+12,2)<50:
        attempts+=1;r.ramp('left_combo_ramp_'+str(attempts),1);count=g(player+12,2)
        if count in [24,25,49,50]:r.wait();r.mark('count_'+str(count))
        assert attempts<60 and r.tick<12000
    r.wait();assert g(0x46e2d8,2)==2;r.mark('two_pending')
    for i in range(3):
        r.wait(60);r.ramp('right_trap_'+str(i+1),0);r.free();r.mark('redemption_'+str(i+1))
    t=r.finish(CASE);t.update(threshold_events=r.earns,redemption_events=r.redemptions,scope=SCOPE)
    summary=contracts(t)
    (ROOT/f'build/oracle/pirate-modes/{CASE}/trace.json').write_bytes(compact(t)+b'\n')
    path=ROOT/f'analysis/traces/pirate-{CASE}.json';f=json.loads(path.read_text());f.pop('magnasaver_state')
    f.update(threshold_events=r.earns,redemption_events=r.redemptions,scope=SCOPE,magnasaver_state_sha256=digest(compact(t['magnasaver_state'])))
    path.write_text(json.dumps(f,indent=2)+'\n')
    (ROOT/'analysis/pirate-extra-threshold-chain.json').write_text(json.dumps(dict(schema=1,case=CASE,status='ORIGINAL/FRESH RESET VERIFIED; native pending',build_sha256=BUILD_SHA,dat_sha256=DAT_SHA,steps=t['tick_count'],contract=summary,scope=SCOPE,
        fields=dict(combo_count='[46b758]+0c',threshold='46e2da',pending='46e2d8',credits='[46b758]+10'),
        earn='43531c/43534a/435366',redemption='43739b/4373bf/4373c9',fixture=str(path.relative_to(ROOT)),fixture_sha256=digest(path.read_bytes())),indent=2)+'\n')
    print(CASE,t['tick_count'],summary,flush=True)
if __name__=='__main__':main()
