#!/usr/bin/env python3
"""Bounded original Mermaid-bank event discovery; no gameplay field writes."""
import json
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP
from pirate_campaign_magnets_oracle import Combined
from pirate_adventure_oracle import ROOT
class Mermaid(Combined):
    def __init__(self):
        super().__init__();self.payments=[]
        def paid(u,a,s,d):
            self.payments.append(dict(tick=self.tick+1,phase=self.m.get(0x46c6ac),amount=u.reg_read(UC_X86_REG_EAX),return_address=hex(self.m.get(u.reg_read(UC_X86_REG_ESP)))))
        self.m.u.hook_add(UC_HOOK_CODE,paid,begin=0x405fac,end=0x405fac)
    def mark(self,label):
        row=super().mark(label);g=self.m.get;p=g(0x46b758)
        row.update(mermaid_bank=g(0x46e2d4),mermaid_targets=list(self.m.u.mem_read(0x46e2cc,3)),bonus_base=g(p+8),bonus_multiplier=g(p+18,2),bonus_hold=g(p+20,2),ball_number=g(p+14,2),field_player_0a=g(p+10,2),held=[g(0x46c6d0),g(0x46c6d4)],kickback=g(0x46e534,2),tilt=g(0x46b764))
        print(self.tick,label,{k:row[k] for k in ['mermaid_bank','mermaid_targets','bonus_base','bonus_multiplier','bonus_hold','ball_number','held','kickback']},flush=True);return row
    def drain(self,label):
        self.free();self.mark(label+'_before');self.shot(label,0,160,590)
        start=self.tick;entered=False
        while self.m.get(0x46c6ac)!=1:
            self.step();assert self.tick-start<4000
            if self.m.get(0x46c6ac)==3 and not entered:self.mark(label+'_bonus_entered');entered=True
        self.mark(label+'_settled')
    def launch(self):
        start=self.tick
        while self.m.get(0x46c1b4,2)!=2:
            if self.tick%200==0:self.key('enter',True);self.key('enter',False)
            self.step();assert self.tick-start<2000
        self.mark('launched')

def main():
    r=Mermaid();r.initial();r.mark('initial')
    for repeat in range(2):
        for name,x,y in [('left',60,321),('right',96,305),('middle',85,315)]:
            r.shot(f'bank_{repeat}_{name}',0,x,y);r.mark(f'hit_{repeat}_{name}');r.idle()
    r.ramp('right_trap',0);r.free();r.mark('right_trap_return');r.idle()
    r.drain('first_drain');r.launch();r.drain('second_drain')
    (ROOT/'build/oracle/pirate-mermaid-probe.json').write_text(json.dumps(dict(milestones=r.milestones,payments=r.payments,ticks=r.tick),indent=2)+'\n')
if __name__=='__main__':main()
