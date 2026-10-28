#!/usr/bin/env python3
"""MagnaTable genuine bitmap triggers, admission/capture clocks and Tilt.

Only original keyboard events and explicit free-ball DAT waypoints; no
rule, timer, phase, force, capture-state, callback or occupied-ball injection.
"""
import argparse,json
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX
from pirate_magna_oracle import Magna
from pirate_mode_feedback_oracle import Feedback
from pirate_adventure_oracle import ROOT,BUILD_SHA,DAT_SHA,compact

CASES=['trigger-edge','exit-edge','cooldown','tilt-free','tilt-held','admit-last','admit-late']


class Capture(Magna):
    @staticmethod
    def fresh_original():
        m=Feedback.fresh_original();m.run(0x40df1e,until=0x40df5f)
        return m

    @staticmethod
    def apply_input(m,e):
        scan=dict(enter=0x1c,left=0x2a,right=0x36,
            nudge_left=0x38,nudge_right=0xb8,nudge_up=0x39)[e['action']]
        m.run(0x40404c,0 if e['down']else 1,scan)

    def __init__(self):
        super().__init__(0);self.routes=[];self.initializers=[]
        def route(u,pc,size,data):
            ball=u.reg_read(UC_X86_REG_EAX)
            self.routes.append(dict(tick=self.tick+1,ball=hex(ball),
                x=self.m.get(ball),y=self.m.get(ball+4),
                active=self.m.get(0x46e542,2),cooldown=self.m.get(0x465a68),
                tilt=self.m.get(0x46b764)))
        def init(u,pc,size,data):
            self.initializers.append(dict(tick=self.tick+1,window=self.m.get(0x46e540,2)))
        self.m.u.hook_add(UC_HOOK_CODE,route,begin=0x43810c,end=0x43810c)
        self.m.u.hook_add(UC_HOOK_CODE,init,begin=0x431d95,end=0x431d95)

    def seed(self,armed=False):
        self.prefix_case='magna-expired'if armed else'magna-slot-0'
        self.prefix_steps=1209 if armed else 1355
        f=json.loads((ROOT/f'analysis/traces/pirate-{self.prefix_case}.json').read_text())
        inputs={};shots={s['tick']:s for s in f['diagnostic_shots']}
        for e in f['inputs']:inputs.setdefault(e['tick'],[]).append(e)
        while self.tick<self.prefix_steps:
            for e in inputs.get(self.tick,[]):
                self.inputs.append(e);self.apply_input(self.m,e)
            if self.tick in shots:
                s=shots[self.tick];self.shots.append(s);self.m.shot(s['layer'],s['x'],s['y'],s.get('ball',0))
            self.step()
        self.mark('frozen_prefix')

    def mark(self,label):
        row=super().mark(label)
        row.update(cooldown=self.m.get(0x465a68),tilt=self.m.get(0x46b764),
            route_count=len(self.routes),initializer_count=len(self.initializers))
        return row

    def until(self,end,park=False):
        while self.tick<end:
            if park:self.parked_step()
            else:self.step()

    def tilt(self):
        for a in ['nudge_left','nudge_right','nudge_up']:
            self.key(a,True);self.key(a,False);self.until(self.tick+4)
        assert self.m.get(0x46b764)!=0
        self.mark('tilt_reached')


def generate(case):
    r=Capture();r.seed(armed=case.startswith('admit-'));g=r.m.get
    if case.startswith('admit-'):
        onset=2760 if case=='admit-last'else 2761
        r.until(onset,park=True);r.mark('before_top_trap')
        r.shot('late_top_trap',0,86,10)
        r.until(onset+80);r.mark('admission_result')
        expected=65535 if case=='admit-last'else 0
        assert g(0x46e542,2)==expected
        assert r.initializers==[dict(tick=onset+52,window=0 if expected else 65535)]
        if expected:
            r.key('left',True);r.key('right',True)
            r.wait(lambda:g(0x46c1b4,2)==2)
            r.key('left',False);r.key('right',False)
            r.shot('admitted_normal_exit',1,120,81)
        r.free();r.mark('normal_return')
    elif case=='trigger-edge':
        n=len(r.routes);r.shot('outside_capture_bitmap',1,120,18)
        assert len(r.routes)==n and g(0x46e542,2)==65535
        r.shot('inside_capture_bitmap',1,120,17)
        assert g(0x46c1b4,2)==3 and g(0x46c1b6,2)==6
        r.mark('capture_admitted');r.free();r.mark('normal_return')
    elif case=='exit-edge':
        n=len(r.routes);r.shot('outside_exit_bitmap',1,120,80)
        assert len(r.routes)==n and g(0x46e542,2)==65535
        r.shot('inside_exit_bitmap',1,120,81)
        assert g(0x46e542,2)==0 and g(0x46c1b4,2)==7
        r.mark('exit_admitted');r.free();r.mark('normal_return')
    elif case=='cooldown':
        r.shot('first_reward_capture',1,120,14)
        assert g(0x465a6c)==150;r.free();r.mark('first_release')
        assert g(0x465a68)==10
        r.shot('cooldown_ten_rejects',1,120,14)
        assert g(0x46c1b4,2)==2;r.mark('cooldown_ten_rejected')
        while g(0x465a68)!=0:
            r.parked_step();assert r.tick<1700
        r.shot('cooldown_zero_rejects',1,120,14)
        assert g(0x46c1b4,2)==2;r.mark('cooldown_zero_rejected')
        while g(0x465a68)!=0xffffffff:r.parked_step()
        r.mark('cooldown_negative_ready')
        r.shot('cooldown_negative_admits',1,120,14)
        assert g(0x46c1b4,2)==3 and g(0x46c1b6,2)==6
        r.mark('second_capture_admitted');r.free();r.mark('normal_return')
    elif case=='tilt-free':
        r.tilt();n=len(r.routes)
        r.shot('tilted_capture_rejected',1,120,14)
        assert len(r.routes)==n+1 and g(0x46c1b4,2)==2 and g(0x46e542,2)==65535
        r.mark('tilted_capture_guard')
        r.shot('tilted_no_award_exit',1,120,81)
        assert g(0x46e542,2)==0 and g(0x465864,2)==g(0x465858,2)==0
        r.mark('tilted_exit_clears_field');r.free();r.mark('normal_return')
    else:
        r.shot('reward_capture_before_tilt',1,120,14)
        r.mark('captured_before_tilt');assert g(0x465a6c)==150
        r.tilt();r.wait(lambda:g(0x46c1b4,2)==2)
        assert g(0x465a68)==0xffffffff and g(0x465a6c)>0
        r.mark('tilt_bypasses_hold_without_cooldown')
    trace=r.finish('magna-capture-'+case)
    extra=dict(prefix_case=r.prefix_case,prefix_steps=r.prefix_steps,
        capture_routes=r.routes,initializer_observations=r.initializers,scope=__doc__)
    trace.update(extra)
    name=trace['case'];(ROOT/f'build/oracle/pirate-modes/{name}/trace.json').write_bytes(compact(trace)+b'\n')
    path=ROOT/f'analysis/traces/pirate-{name}.json';f=json.loads(path.read_text());f.update(extra)
    path.write_text(json.dumps(f,indent=2)+'\n');return trace


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cases',nargs='+',choices=CASES,default=CASES);a=p.parse_args()
    for c in a.cases:generate(c)
    edges=Counter();cases=[]
    for c in CASES:
        name='magna-capture-'+c;path=ROOT/f'build/oracle/pirate-modes/{name}/trace.json'
        if not path.exists():continue
        t=json.loads(path.read_text());assert t['build_sha256']==BUILD_SHA;cases.append(name)
        for e in t['executed_call_edges']:edges[e['callsite'],e['target']]+=e['count']
    (ROOT/'analysis/pirate-magna-capture-boundary.json').write_text(json.dumps(dict(
        build_sha256=BUILD_SHA,dat_sha256=DAT_SHA,cases=cases,gameplay_stubs=[],
        executed_call_edges=[dict(callsite=a,target=b,count=n)for(a,b),n in sorted(edges.items())],scope=__doc__),indent=2)+'\n')


if __name__=='__main__':main()
