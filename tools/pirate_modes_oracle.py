#!/usr/bin/env python3
"""Four Pirate Adventures through original physical events, no rule-state writes.

Reuses the Plank oracle and diagnostic free-ball waypoints. Native generation
consumes only observed original callback targets. All full traces remain private.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
from pirate_adventure_oracle import Original, ROOT, BUILD_SHA, DAT_SHA, TIMING, compact, digest


class Recorder:
    @staticmethod
    def fresh_original():
        return Original(ROOT/'build/oracle/pirate-full-tick')

    @staticmethod
    def apply_input(m,event):
        scan={'enter':0x1c,'left':0x2a,'right':0x36}[event['action']]
        m.run(0x40404c,0 if event['down']else 1,scan)

    def __init__(self, mode):
        self.m=self.fresh_original()
        self.mode=mode;self.tick=0;self.states=[self.m.ball()]
        self.samples=[];self.inputs=[];self.shots=[];self.milestones=[]

    def step(self):
        self.m.step(self.tick);self.tick+=1
        self.states.append(self.m.ball());self.samples.append(self.m.sample())

    def mark(self,label):
        value=self.m.milestone(self.tick,label)
        value.update(field_46e2a8=self.m.get(0x46e2a8),field_46e54a=self.m.get(0x46e54a,2),
            field_46e54c=self.m.get(0x46e54c,2),field_46e544=self.m.get(0x46e544,2),
            field_46e55a=self.m.get(0x46e55a,2),field_4659a8=self.m.get(0x4659a8))
        self.milestones.append(value);return value

    def shot(self,label,layer,x,y,ball=0):
        event=dict(tick=self.tick,label=label,layer=layer,x=x,y=y)
        if ball:event['ball']=ball
        self.shots.append(event)
        self.m.shot(layer,x,y,ball);self.step()
        if label!='timeout_free_flight':self.mark(label)

    def free(self):
        start=self.tick
        while self.m.get(0x46c1b4,2)!=2:
            self.step();assert self.tick-start<4000,('held ball',self.mark('blocked'))

    def enter(self,release=True):
        while self.tick<600:
            if self.tick in (200,201):
                self.m.run(0x40404c,0 if self.tick==200 else 1,0x1c)
                self.inputs.append(dict(tick=self.tick,action='enter',down=self.tick==200))
            self.step()
        self.m.track_calls()
        for n in range(self.mode):self.shot(f'bumper_select_{n+1}',0,169,38)
        assert self.m.get(0x46e2c0,2)==self.mode
        self.shot('right_ramp_arm',1,225,45)
        self.shot('upper_left_entry',0,24,60)
        while self.m.get(0x46c6ac)!=5:
            self.step();assert self.tick<1100
        if not release:
            assert self.m.get(0x46c6c0) and self.mode==5
            self.mark('video_initialized');return
        self.free()
        assert self.m.get(0x46e2c0,2)==self.mode
        self.mark('started_and_released')
        self.shot('return_lane',2,70,340)

    def ramp(self,label,ident):
        if ident==0:
            self.shot(label,0,302,185);self.free()
        elif ident==1:
            self.shot(label+'_clear',0,160,400)
            self.shot(label+'_guide',0,41,162)
            self.shot(label,2,91,44)
        else:
            layer,x,y={2:(1,49,74),3:(1,225,45),4:(1,81,228)}[ident]
            self.shot(label,layer,x,y)
        self.mark(label+'_settled')

    def timeout(self):
        self.m.pause_calls()
        start=self.tick
        while self.m.get(0x46c6ac)==5:
            if self.m.get(0x46e546,2)<=8:self.m.track_calls()
            if self.tick%40==0:self.shot('timeout_free_flight',0,160,400)
            else:self.step()
            assert self.tick-start<16000
        assert self.m.get(0x46c6ac)==2
        self.mark('timeout_return')

    def finish(self,case):
        for _ in range(80):self.step()
        while self.tick%4:self.step()
        trace=dict(schema=1,build_sha256=BUILD_SHA,dat_sha256=DAT_SHA,mode=self.mode,
            case=case,tick_count=self.tick,inputs=self.inputs,diagnostic_shots=self.shots,
            milestones=self.milestones,states=self.states,timing_fields=TIMING,
            **{k:[s[k]for s in self.samples]for k in self.samples[0]},
            executed_call_edges=[dict(callsite=hex(a),target=hex(b),count=n)
                for(a,b),n in sorted(self.m.calls.items())],gameplay_stubs=[],
            scope='Directed free-ball waypoints on actual DAT triggers; no rule/score/timer/capture injection; not a legal-key-only trajectory')
        # Independent fresh original replay of frozen actions, no trace hooks.
        m=self.fresh_original()
        keys={};shots={s['tick']:s for s in self.shots}
        for event in self.inputs:keys.setdefault(event['tick'],[]).append(event)
        for tick in range(self.tick):
            for event in keys.get(tick,[]):self.apply_input(m,event)
            if tick in shots:
                s=shots[tick];m.shot(s['layer'],s['x'],s['y'],s.get('ball',0))
            m.step(tick)
            assert m.ball()==self.states[tick+1],(case,tick,'ball')
            assert m.sample()==self.samples[tick],(case,tick,'rules/clock/display')
        trace['deterministic_original_replay']=True
        folder=ROOT/'build/oracle/pirate-modes'/case;folder.mkdir(parents=True,exist_ok=True)
        (folder/'trace.json').write_bytes(compact(trace)+b'\n')
        sequences=['dmd_sha256','highscore_sha256','lamp_sha256','rule_sha256','video_sha256','ball_pool_sha256']
        fixture={k:v for k,v in trace.items()if k not in ['states','timing','lifecycle','executed_call_edges',*sequences]}
        fixture.update(states_sha256=digest(bytes(v for s in self.states for v in s)),
            timing_sha256=digest(compact(trace['timing'])),lifecycle_sha256=digest(compact(trace['lifecycle'])))
        for key in sequences:fixture[key.replace('_sha256','_sequence_sha256')]=digest(''.join(trace[key]).encode())
        (ROOT/f'analysis/traces/pirate-{case}.json').write_text(json.dumps(fixture,indent=2)+'\n')
        print(case,self.tick,'steps',self.milestones[-1],flush=True)
        return trace


def generate(case):
    mode={'sword':1,'dive':2,'monkey':3,'shark':4}[case.split('-')[0]]
    r=Recorder(mode);r.enter()
    if case=='sword':
        r.ramp('initial_jackpot',4);r.ramp('repeated_jackpot',4)
        r.shot('bumper_growth',0,169,38)
        r.ramp('raised_jackpot',2)
        r.shot('target_growth',0,145,234)
        r.ramp('target_raised_jackpot',3)
        r.ramp('skull_jackpot',1);r.ramp('right_trap_jackpot',0)
        r.shot('top_trap_growth',0,86,10);r.free();r.mark('after_top_trap')
        r.shot('return_lane_again',2,70,340)
        r.ramp('trap_raised_jackpot',4)
        r.timeout()
    elif case=='dive-success':
        r.shot('bumper_descent_rate',0,169,38)
        n=0
        while r.m.get(0x46e54a,2)<100:
            r.ramp(f'dive_{n}',4);n+=1;assert n<12
        r.mark('bottom_reached')
        r.ramp('duplicate_after_bottom',4)
        r.shot('super_jackpot_trap',0,86,10);r.free()
        assert r.m.get(0x46c6ac)==2;r.mark('super_jackpot_return')
    elif case=='monkey-success':
        r.ramp('wrong_target',4)
        for ident in [1,2,3,4,0]:r.ramp(f'map_piece_{ident}',ident)
        assert r.m.get(0x46c6ac)==2;r.mark('map_complete_return')
    elif case=='shark-success':
        r.ramp('ramp_speed_1',4);r.shot('bumper_speed',0,169,38)
        r.shot('target_speed',0,145,234)
        r.ramp('ramp_speed_2',2);r.ramp('ramp_speed_3',3)
        start=r.tick
        while r.m.get(0x46c6ac)==5:
            if r.tick%40==0:r.shot('timeout_free_flight',0,160,400)
            else:r.step()
            assert r.tick-start<1000
        r.mark('shark_escape_return')
    else:r.timeout()
    return r.finish(case)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    cases=['sword','dive-success','dive-timeout','monkey-success','monkey-timeout','shark-success','shark-timeout']
    parser.add_argument('--cases',nargs='+',choices=cases,default=cases)
    args=parser.parse_args()
    for case in args.cases:generate(case)
    # Merge retained independent runs, never overwrite a previous case's targets.
    edges=Counter();included=[]
    for case in cases:
        path=ROOT/'build/oracle/pirate-modes'/case/'trace.json'
        if not path.exists():continue
        trace=json.loads(path.read_text());assert trace['build_sha256']==BUILD_SHA
        included.append(case)
        for edge in trace['executed_call_edges']:edges[(edge['callsite'],edge['target'])]+=edge['count']
    (ROOT/'analysis/pirate-modes-boundary.json').write_text(json.dumps(dict(
        build_sha256=BUILD_SHA,cases=included,gameplay_stubs=[],
        executed_call_edges=[dict(callsite=a,target=b,count=n)for(a,b),n in sorted(edges.items())],
        scope='Observed original indirect callbacks in four Adventure diagnostic trajectories'),indent=2)+'\n')


if __name__=='__main__':main()
