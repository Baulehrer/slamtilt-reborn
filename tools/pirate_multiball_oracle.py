#!/usr/bin/env python3
"""Pirate Cave/cannon/multiball chains using real switches and legal keys.

Diagnostic waypoints affect only active free balls, never rules or timers.
Every frozen schedule is independently replayed in a fresh original instance.
"""
import argparse
from collections import Counter
import json
from pirate_modes_oracle import Recorder
from pirate_adventure_oracle import ROOT, BUILD_SHA


class Multiball(Recorder):
    @staticmethod
    def fresh_original():
        m=Recorder.fresh_original();m.put(0x46c5dc,0x2a);m.put(0x46c5e0,0x36)
        return m

    def key(self,action,down):
        event=dict(tick=self.tick,action=action,down=down)
        self.apply_input(self.m,event);self.inputs.append(event)

    def mark(self,label):
        row=super().mark(label);g=self.m.get
        row.update(ball_count=g(0x46c67c),locks=g(0x46e2bc,2),played_multiballs=g(0x46e2be,2),
            jackpot=g(0x46e2a0),collected=g(0x46e298),target=g(0x46e538,2),
            field_46e554=g(0x46e554,2),field_46e55e=g(0x46e55e,2),
            field_465a40=g(0x465a40),cannon_wait=g(0x465974),cannon_angle=g(0x465970)&4095,
            ball_states=[g(0x46c15c+100*i+0x58,2)for i in range(g(0x46c67c))])
        print(label,self.tick,'phase',row['phase'],'balls',row['ball_count'],'locks',row['locks'],
            'played_multiballs',row['played_multiballs'],'JP',row['jackpot'],'target',row['target'],flush=True)
        return row

    def wait_step(self,park=False,exclude=0):
        if park and self.tick%40==0:
            for i in reversed(range(self.m.get(0x46c67c))):
                if i!=exclude and i<self.m.get(0x46c67c) and self.m.get(0x46c15c+100*i+0x58,2)==2:
                    self.shot('multiball_free_flight',0,160,400,i)
                    return
        self.step()

    def free(self):
        start=self.tick
        while self.m.get(0x46c1b4,2)!=2:
            self.wait_step(park=True);assert self.tick-start<5000,('held',self.mark('blocked'))

    def cave(self,label):
        self.shot(label,0,43,198);assert self.m.get(0x46c1b4,2)==3
        self.free();self.mark(label+'_released')
        self.shot(label+'_return_lane',2,70,340)
        while self.m.get(0x465a44)<0x80000000:self.wait_step(park=True)

    def initial(self):
        while self.tick<600:
            if self.tick in(200,201):self.key('enter',self.tick==200)
            self.step()
        self.m.track_calls();self.mark('normal_start')

    def cannon(self,miss=False):
        self.shot('cannon_top_trap',0,86,10)
        start=self.tick
        while self.m.get(0x46c6ac)!=6:
            self.step();assert self.tick-start<1000
        self.mark('cannon_ready_intro')
        # Genuine early key does not bypass the original ready gate.
        self.key('left',True);self.step();self.key('left',False);self.step()
        assert self.m.get(0x46c6ac)==6;self.mark('early_fire_ignored')
        while self.m.get(0x465974)<0x80000000:self.step()
        if not miss:
            for _ in range(400):
                angle=self.m.get(0x465970)&4095
                sine=int.from_bytes(self.m.u.mem_read(self.m.get(0x46b778)+angle*2,2),'little',signed=True)
                if abs(sine)<1000:break
                self.step()
            else:raise AssertionError('No central aim')
        self.mark('cannon_aim')
        self.key('left',True);self.step();self.key('left',False)
        self.mark('cannon_fired')
        start=self.tick
        while self.m.get(0x46c6ac)!=4 and self.m.get(0x46e2bc,2)>=2:
            self.step();assert self.tick-start<2500
        return self.mark('cannon_result')


def generate(case):
    r=Multiball(0);r.initial();m=r.m
    for i in range(2):r.cave(f'initial_lock_{i+1}')
    assert m.get(0x46e2bc,2)==2
    result=r.cannon(miss=case=='cannon-miss')
    if case=='cannon-miss':
        assert result['phase']==2 and result['locks']==1 and result['played_multiballs']==0
        r.free();r.mark('miss_normal_return')
    else:
        assert result['phase']==4 and result['played_multiballs']==1 and result['locks']==0
        start=r.tick
        while m.get(0x46c67c)<2 or any(m.get(0x46c15c+100*i+0x58,2)!=2 for i in range(m.get(0x46c67c))):
            r.wait_step(park=True,exclude=-1);assert r.tick-start<5000
        r.mark('crocodile_balls_released')
        # The original target selector controls which real DAT trigger pays.
        target=m.get(0x46e538,2)
        r.ramp('wrong_jackpot',(target+2)%5);r.mark('wrong_jackpot_guard')
        target=m.get(0x46e538,2)
        r.ramp('first_jackpot',target);r.mark('first_jackpot_awarded')
        r.cave('jackpot_growth');r.mark('jackpot_grown')
        target=m.get(0x46e538,2)
        r.ramp('raised_jackpot',target);r.mark('raised_jackpot_awarded')
        # Actual drain processing/rescue grace, while protecting the last ball
        # only with explicit free-ball diagnostic positions, not timer writes.
        start=r.tick;last_drain=-1000
        while m.get(0x46c6ac)==4:
            count=m.get(0x46c67c)
            if count>1 and m.get(0x46c15c+100*(count-1)+0x58,2)==2 and r.tick-last_drain>=300:
                r.shot('multiball_drain',0,160,599,count-1)
                last_drain=r.tick
            elif r.tick%40==20 and m.get(0x46c1b4,2)==2:r.shot('last_ball_free_flight',0,160,400)
            else:r.step()
            assert r.tick-start<12000,('drain',r.mark('blocked_drain'))
        assert m.get(0x46c67c)==1 and m.get(0x46c6ac)==2
        r.mark('crocodile_normal_return')
    return r.finish(case)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cases',nargs='+',choices=['crocodile','cannon-miss'],default=['crocodile','cannon-miss'])
    args=p.parse_args()
    for case in args.cases:generate(case)
    edges=Counter();included=[]
    for case in ['crocodile','cannon-miss']:
        path=ROOT/'build/oracle/pirate-modes'/case/'trace.json'
        if not path.exists():continue
        t=json.loads(path.read_text());assert t['build_sha256']==BUILD_SHA;included.append(case)
        for e in t['executed_call_edges']:edges[(e['callsite'],e['target'])]+=e['count']
    (ROOT/'analysis/pirate-multiball-boundary.json').write_text(json.dumps(dict(
        build_sha256=BUILD_SHA,cases=included,gameplay_stubs=[],
        executed_call_edges=[dict(callsite=a,target=b,count=n)for(a,b),n in sorted(edges.items())],
        scope='Original Cave locks/cannon aiming/Crocodile jackpot/growth/drain and miss'),indent=2)+'\n')


if __name__=='__main__':main()
