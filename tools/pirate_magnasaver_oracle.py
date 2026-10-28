#!/usr/bin/env python3
"""Standalone Pirate Magnasaver: actual earned input, force, expiry and Tilt.

Only explicit free-ball DAT waypoints and real keyboard handlers drive play.
No force, rule, timer, Tilt, capture or callback writes are injected.
"""
import argparse
from collections import Counter
import json
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EBX, UC_X86_REG_ESI
from pirate_final_feedback_a_oracle import RemainingFeedback
from pirate_adventure_oracle import ROOT, BUILD_SHA, DAT_SHA, compact

CASES=['force-off','force-on','retrigger','rearm','tilt-armed','tilt-active','save-return']
FIELDS=[(0x46e536,2),(0x46e552,2),(0x46584c,2),(0x46e450,1),(0x46b764,4)]


class Magnasaver(RemainingFeedback):
    @staticmethod
    def fresh_original():
        m=RemainingFeedback.fresh_original()
        original_sample=m.sample
        m.sample=lambda:dict(original_sample(),magnasaver_state=[m.get(a,n)for a,n in FIELDS])
        return m

    @staticmethod
    def apply_input(m,e):
        scans=dict(enter=0x1c,left=0x2a,right=0x36,special_left=0x1d,
            nudge_left=0x38,nudge_right=0xb8,nudge_up=0x39)
        m.run(0x40404c,0 if e['down']else 1,scans[e['action']])

    def __init__(self):
        super().__init__()
        self.force_applications=[]
        self.pending_force=None
        def before(u,pc,size,data):
            if u.reg_read(UC_X86_REG_ESI)==0x465848 and self.m.get(0x46584c,2)==65535:
                ball=u.reg_read(UC_X86_REG_EBX)
                self.pending_force=(ball,[self.m.get(ball+offset)for offset in [0,4,20,24]])
        def after(u,pc,size,data):
            if u.reg_read(UC_X86_REG_ESI)==0x465848 and self.pending_force:
                ball,state=self.pending_force
                self.force_applications.append(dict(tick=self.tick+1,ball=hex(ball),
                    before=state,after_velocity=[self.m.get(ball+20),self.m.get(ball+24)]))
                self.pending_force=None
        self.m.u.hook_add(UC_HOOK_CODE,before,begin=0x40ada6,end=0x40ada6)
        self.m.u.hook_add(UC_HOOK_CODE,after,begin=0x40aeb9,end=0x40aeb9)

    def mark(self,label):
        row=super().mark(label)
        row['magnasaver_state']=[self.m.get(a,n)for a,n in FIELDS]
        row['force_applications']=len(self.force_applications)
        return row

    def until(self,end,park=False,launch=False):
        while self.tick<end:
            if launch and self.tick%200==0 and self.m.get(0x46c6ac)==1:
                self.key('enter',True);self.key('enter',False)
            if park:self.park()
            else:self.step()

    def earn(self):
        self.shot('left_target_earns_pair',0,92,144)
        self.shot('right_target_earns_pair',0,232,141)
        assert self.m.get(0x46e53c,2)==65535
        self.ramp('right_trap_collects_magnasaver',0)
        self.shot('return_lane',2,70,340)
        assert self.m.get(0x46e536,2)==65535
        self.mark('earned_'+str(self.tick))

    def activate(self):
        self.key('special_left',True)
        self.key('special_left',False)
        self.mark('key_'+str(self.tick))


def generate(case):
    r=Magnasaver();r.initial();r.earn();r.until(1200,park=True)
    g=r.m.get
    if case!='force-off' and case!='tilt-armed':r.activate()
    if case in ['force-off','force-on','save-return']:
        r.shot('same_left_outlane_initial_state',0,25,530)
        r.until(1400);r.mark('paired_200_steps')
        r.until(1800);r.mark('paired_600_steps')
        if case in ['force-on','save-return']:
            r.until(2004);assert g(0x46584c,2)==0 and g(0x46e552,2)==65535
            r.mark('original_expiry')
            if case=='save-return':
                r.until(2200);r.key('left',True)
                r.until(2320);r.key('left',False)
                r.until(2800);r.mark('flipper_returns_saved_ball_to_play')
            else:
                r.until(3600,launch=True);r.mark('following_ball')
        else:
            assert not r.force_applications
    elif case=='retrigger':
        r.until(1280,park=True)
        window=g(0x46e552,2);r.activate()
        assert g(0x46e552,2)==window and g(0x46e536,2)==0
        r.mark('unearned_retrigger_did_not_extend')
        r.until(2004,park=True)
        assert g(0x46584c,2)==0 and g(0x46e552,2)==65535
        r.mark('unextended_original_expiry')
        r.until(2080,park=True)
    elif case=='rearm':
        r.until(1280,park=True);r.earn()
        assert g(0x46584c,2)==65535 and 0<g(0x46e552,2)<200
        r.mark('reearned_while_active');r.activate()
        assert g(0x46e536,2)==0 and g(0x46e552,2)==200
        r.mark('rearm_reloaded_200')
        r.shot('rearmed_left_outlane',0,25,530)
        start=r.tick
        while g(0x46584c,2):
            r.step();assert r.tick-start<810
        assert g(0x46e552,2)==65535
        r.mark('rearmed_original_expiry')
    else:
        r.shot('left_outlane_before_tilt',0,25,530)
        r.until(1248)
        for action in ['nudge_left','nudge_right','nudge_up']:
            r.key(action,True);r.key(action,False);r.until(r.tick+4)
        assert g(0x46b764)!=0
        r.mark('tilt_reached');window=g(0x46e552,2)
        r.activate()
        r.until(r.tick+200);r.mark('tilted_window_frozen')
        assert g(0x46e552,2)==window
        assert g(0x46584c,2)==(65535 if case=='tilt-active' else 0)
        tilted_tick=next(m['tick']for m in r.milestones if m['label']=='tilt_reached')
        assert not any(e['tick']>tilted_tick for e in r.force_applications)
        r.until(4400,launch=True)
        assert g(0x46b764)==0 and g(0x46584c,2)==0
        assert g(0x46e552,2)==65535 and g(0x46e536,2)==0
        r.mark('next_ball_clears_tilt_and_magnasaver')
    name='magnasaver-'+case
    trace=r.finish(name)
    force=dict(count=len(r.force_applications),first=r.force_applications[:1],
        last=r.force_applications[-1:])
    trace.update(force_observations=force,scope=__doc__)
    (ROOT/f'build/oracle/pirate-modes/{name}/trace.json').write_bytes(compact(trace)+b'\n')
    path=ROOT/f'analysis/traces/pirate-{name}.json';f=json.loads(path.read_text())
    f.update(force_observations=force,scope=__doc__);path.write_text(json.dumps(f,indent=2)+'\n')
    return trace


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cases',nargs='+',choices=CASES,default=CASES);a=p.parse_args()
    for case in a.cases:generate(case)
    edges=Counter();cases=[]
    for case in CASES:
        name='magnasaver-'+case;path=ROOT/f'build/oracle/pirate-modes/{name}/trace.json'
        if not path.exists():continue
        t=json.loads(path.read_text());assert t['build_sha256']==BUILD_SHA;cases.append(name)
        for e in t['executed_call_edges']:edges[e['callsite'],e['target']]+=e['count']
    (ROOT/'analysis/pirate-magnasaver-boundary.json').write_text(json.dumps(dict(
        schema=1,build_sha256=BUILD_SHA,dat_sha256=DAT_SHA,cases=cases,gameplay_stubs=[],
        executed_call_edges=[dict(callsite=a,target=b,count=n)for(a,b),n in sorted(edges.items())],
        fields=[dict(address=hex(a),bytes=n)for a,n in FIELDS],scope=__doc__),indent=2)+'\n')


if __name__=='__main__':main()
