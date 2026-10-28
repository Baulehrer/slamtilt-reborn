#!/usr/bin/env python3
"""Actual left-ramp combo chain, natural expiry and last accepted contact."""
import json
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX
from pirate_campaign_magnets_oracle import Combined
from pirate_adventure_oracle import ROOT,BUILD_SHA,compact,digest
from pirate_combo_contracts import contracts
class Combo(Combined):
    def __init__(self):
        super().__init__();self.combo_pays=[];self.combo_checks=[]
        def paid(u,a,s,d):self.combo_pays.append(dict(tick=self.tick+1,amount=u.reg_read(UC_X86_REG_EAX)))
        def checked(u,a,s,d):self.combo_checks.append(dict(tick=self.tick+1,window=self.m.get(0x46e550,2)))
        self.m.u.hook_add(UC_HOOK_CODE,paid,begin=0x4367ec,end=0x4367ec)
        self.m.u.hook_add(UC_HOOK_CODE,checked,begin=0x438a37,end=0x438a37)
    def mark(self,label):
        row=super().mark(label);g=self.m.get
        row.update(combo_count=g(g(0x46b758)+12,2),combo_window=g(0x46e550,2),combo_value=g(0x46e2a4),paid_count=len(self.combo_pays));return row
    def initial(self):
        super().initial()
        while self.m.get(0x46e53a,2)<32768:self.park()
        self.idle();assert self.tick==1112

def generate(case):
    r=Combo();r.initial();r.ramp('first_left_ramp_arms',1);r.mark('armed');assert r.tick==1115
    if case=='chain':
        for i in range(4):r.ramp('paid_'+str(i+1),1)
        r.mark('four_paid')
        while r.m.get(0x46e550,2)<32768:r.park()
        r.mark('expired');r.ramp('fresh_arm_after_expiry',1);r.mark('fresh_arm_after_expiry');r.idle()
    else:
        while r.tick<(1913 if case=='last-tick'else 1914):r.park()
        r.ramp('boundary_contact',1);r.mark('boundary_result');r.idle()
    name='combo-'+case;t=r.finish(name);dispatch=[e for e in r.m.dispatch if e['target']==0x42f44c]
    t.update(combo_case=case,combo_pays=r.combo_pays,combo_checks=r.combo_checks,combo_dispatches=dispatch);summary=contracts(t)
    (ROOT/f'build/oracle/pirate-modes/{name}/trace.json').write_bytes(compact(t)+b'\n')
    p=ROOT/f'analysis/traces/pirate-{name}.json';f=json.loads(p.read_text());f.pop('magnasaver_state');f.update(combo_case=case,combo_pays=r.combo_pays,combo_checks=r.combo_checks,combo_dispatches=dispatch,magnasaver_state_sha256=digest(compact(t['magnasaver_state'])));p.write_text(json.dumps(f,indent=2)+'\n')
    print(name,t['tick_count'],summary,flush=True);return dict(case=name,steps=t['tick_count'],contract=summary)
if __name__=='__main__':
    rows=[generate(case)for case in ['chain','last-tick','expired']]
    (ROOT/'analysis/pirate-combo-chain.json').write_text(json.dumps(dict(schema=1,build_sha256=BUILD_SHA,cases=rows,scope='Actual left-ramp DAT contacts and naturally elapsed timer, no field writes; not key-only whole game.',addresses=dict(window='0x46e550',value='0x46e2a4',pay='0x4367ec',count_increment='0x436832',guard='0x438a37',clock='0x435481')),indent=2)+'\n')
