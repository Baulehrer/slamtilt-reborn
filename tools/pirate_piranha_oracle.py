#!/usr/bin/env python3
"""Actual DAT Piranha targets -> ten2M bumper additions -> rearm, original/reset."""
import json
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX
from pirate_campaign_magnets_oracle import Combined
from pirate_adventure_oracle import ROOT,BUILD_SHA,DAT_SHA,compact,digest
from pirate_piranha_contracts import contracts

CASE='piranha-chain'
SCOPE=('Diagnostic physical layer0 waypoints on actual originalDAT contacts; no rule/score/timer/phase/credit/callback writes. '
       'Paired Piranha targets earn ten paid bumper additions,11thnormal,partialrearm. Not a key-only game or full original raster proof.')

class Piranha(Combined):
    def __init__(self):
        super().__init__();self.paid_events=[]
        def paid(u,pc,size,data):
            amount=u.reg_read(UC_X86_REG_EAX)
            assert amount==2000000
            self.paid_events.append(dict(tick=self.tick+1,amount=amount,remaining=self.m.get(0x46e2ca,2)))
        self.m.u.hook_add(UC_HOOK_CODE,paid,begin=0x4394e9,end=0x4394e9)
    def mark(self,label):
        row=super().mark(label)
        row.update(pair_flags=list(self.m.u.mem_read(0x46e2c8,2)),pops_remaining=self.m.get(0x46e2ca,2),
            paid_calls=len(self.paid_events),score_number=int(row['score_bcd']))
        return row
    def rest(self,count=28):
        for _ in range(count):self.park()
    def hit(self,label,x,y):
        self.rest();self.shot(label,0,x,y)
    def bumper(self,label):
        self.rest();self.mark(label+'_before');self.shot(label+'_after',0,169,38)


def main():
    r=Piranha();r.initial();r.idle()
    r.hit('left_only',139,225);r.hit('same_left_again',139,225)
    r.hit('pair_earned',151,260);r.idle()
    assert r.m.get(0x46e2ca,2)==10
    for i in range(1,11):
        r.bumper(f'paid_{i}')
        if i==1:r.idle()
    r.bumper('eleventh')
    r.hit('second_left',139,225);r.hit('second_pair_earned',151,260)
    for i in range(3):r.bumper(f'partial_{i+1}')
    r.mark('partial_spent')
    r.hit('partial_left',139,225);r.hit('partial_same_left_again',139,225)
    r.hit('partial_rearmed',151,260);r.bumper('rearm');r.mark('after_rearm_paid')
    r.idle();trace=r.finish(CASE)
    dispatches=[e for e in r.m.dispatch if e['target']in [0x42cf8c,0x42dc64]]
    trace.update(paid_events=r.paid_events,piranha_dispatches=dispatches,scope=SCOPE)
    summary=contracts(trace)
    path=ROOT/f'build/oracle/pirate-modes/{CASE}/trace.json';path.write_bytes(compact(trace)+b'\n')
    public_path=ROOT/f'analysis/traces/pirate-{CASE}.json';public=json.loads(public_path.read_text());public.pop('magnasaver_state')
    public.update(paid_events=r.paid_events,piranha_dispatches=dispatches,scope=SCOPE,
        magnasaver_state_sha256=digest(compact(trace['magnasaver_state'])))
    public_path.write_text(json.dumps(public,indent=2)+'\n')
    evidence=dict(schema=1,build_sha256=BUILD_SHA,dat_sha256=DAT_SHA,status='ORIGINAL/FRESH RESET VERIFIED; native pending',
        case=CASE,steps=trace['tick_count'],scope=SCOPE,contract=summary,handbook=dict(source='build/manual-rules/pirate.txt',lines='47..53',printed_page=14),
        addresses=dict(left='0x43926d',right='0x439427',earn='0x439608',remaining='0x46e2ca',paired_flags=['0x46e2c8','0x46e2c9'],paid_bumper='0x4394c4',paid_call='0x4394e9'),
        physical_points=dict(left=[139,225],right=[151,260],bumper=[169,38]),
        difference='Pinned Windows adds2M at4394e9 on top of ordinary velocity-dependent bumper score; not asserted as total2M replacement.',
        fixture=str(public_path.relative_to(ROOT)),fixture_sha256=digest(public_path.read_bytes()),
        original_inputs_only=trace['inputs'],paid_events=r.paid_events)
    (ROOT/'analysis/pirate-piranha-chain.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(CASE,trace['tick_count'],'original/reset10vectors',summary,flush=True)
if __name__=='__main__':main()
