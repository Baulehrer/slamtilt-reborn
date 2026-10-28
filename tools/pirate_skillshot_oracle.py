#!/usr/bin/env python3
"""Original real-left-ramp skillshot/window/rearm; no rule/timer writes."""
import json
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX
from pirate_campaign_magnets_oracle import Combined
from pirate_adventure_oracle import ROOT,BUILD_SHA,DAT_SHA,compact,digest
from pirate_skillshot_contracts import contracts
CASES=['success-rearm','wrong-route','last-tick','expired']
class Skillshot(Combined):
    def __init__(self):
        super().__init__();self.skillshot_pay_calls=[];self.skillshot_consumer_checks=[]
        def checked(u,a,s,d):self.skillshot_consumer_checks.append(dict(tick=self.tick+1,window=self.m.get(0x46e53a,2),guard_46e558=self.m.get(0x46e558,2)))
        def paid(u,a,s,d):self.skillshot_pay_calls.append(dict(tick=self.tick+1,amount=u.reg_read(UC_X86_REG_EAX)))
        self.m.u.hook_add(UC_HOOK_CODE,checked,begin=0x4389c8,end=0x4389c8)
        self.m.u.hook_add(UC_HOOK_CODE,paid,begin=0x4389eb,end=0x4389eb)
    def mark(self,label):
        r=super().mark(label);g=self.m.get
        r.update(window=g(0x46e53a,2),guard_46e558=g(0x46e558,2),paid_count=len(self.skillshot_pay_calls),ball_number=g(g(0x46b758)+14,2))
        return r
    def initial(self):
        while self.tick<600:
            if self.tick in [200,201]:self.key('enter',self.tick==200)
            self.step()
        assert self.m.get(0x46c6ac)==2;self.mark('window_open')

def generate(case):
    r=Skillshot();r.initial()
    if case=='wrong-route':
        r.ramp('other_ramp',2);r.mark('other_ramp_no_skillshot')
        r.ramp('left_ramp_skillshot',1);r.idle()
    elif case in ['last-tick','expired']:
        while r.tick<(1109 if case=='last-tick'else 1110):r.park()
        r.ramp('left_ramp_boundary',1);r.idle()
    else:
        r.ramp('first_skillshot',1);r.idle()
        r.ramp('duplicate_left_ramp',1);r.mark('duplicate_after_consumption');r.idle()
        r.shot('physical_drain',0,160,590)
        while r.m.get(0x46c6ac)!=1:
            r.step();assert r.tick<6500,'nextball readiness'
        r.key('enter',True);r.key('enter',False)
        while r.m.get(0x46c1b4,2)!=2:
            if r.m.get(0x46c6ac)==1 and r.tick%200==0:r.key('enter',True);r.key('enter',False)
            r.step();assert r.tick<7000,'nextball launch'
        r.mark('next_ball_window');r.ramp('second_ball_left_ramp',1);r.mark('second_ball_skillshot');r.idle()
    name='skillshot-'+case;t=r.finish(name)
    dispatch=[e for e in r.m.dispatch if e['target']==0x42dd00]
    t.update(skillshot_case=case,skillshot_pay_calls=r.skillshot_pay_calls,skillshot_consumer_checks=r.skillshot_consumer_checks,skillshot_dispatches=dispatch)
    summary=contracts(t);(ROOT/f'build/oracle/pirate-modes/{name}/trace.json').write_bytes(compact(t)+b'\n')
    p=ROOT/f'analysis/traces/pirate-{name}.json';f=json.loads(p.read_text());f.pop('magnasaver_state')
    f.update(skillshot_case=case,skillshot_pay_calls=r.skillshot_pay_calls,skillshot_consumer_checks=r.skillshot_consumer_checks,skillshot_dispatches=dispatch,magnasaver_state_sha256=digest(compact(t['magnasaver_state'])))
    p.write_text(json.dumps(f,indent=2)+'\n');print(name,t['tick_count'],summary,flush=True)
    return dict(case=name,steps=t['tick_count'],contract=summary,fixture_sha256=digest(p.read_bytes()))
def main():
    cases=[generate(c)for c in CASES]
    (ROOT/'analysis/pirate-skillshot-chain.json').write_text(json.dumps(dict(schema=1,status='ORIGINAL/FRESH RESET VERIFIED; native pending',build_sha256=BUILD_SHA,dat_sha256=DAT_SHA,cases=cases,
        addresses=dict(arm='0x4385a6:200',clock='0x43545f:50Hz decrement',consumer='0x43898c',window='0x46e53a signedWORD',pay='0x4389eb',callback='0x42dd00'),
        physical_route=[[0,160,400],[0,41,162],[2,91,44]],
        historical_label_correction='Existing helper calls route1 Skull, but actualSkillshot route1 differs from multiplierSkull route4; physical route/consumers authoritative.',
        scope='Original Enter plus declaredfreeball physicalDAT waypoints; timer elapses naturally. No rule/score/timer/phase/callback writes. Not key-only trajectory or full original raster.'),indent=2)+'\n')
if __name__=='__main__':main()
