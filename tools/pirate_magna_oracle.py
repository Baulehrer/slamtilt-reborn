#!/usr/bin/env python3
"""Original MagnaTable: real admission, key controls, rewards and normal return.

Diagnostic shots affect only a canonical free ball; no rules/timers/score writes.
All frozen schedules are independently replayed without hooks by Recorder.
"""
import argparse
from collections import Counter
import json
from pirate_multiball_oracle import Multiball
from pirate_adventure_oracle import ROOT, BUILD_SHA, compact

from pirate_magna_cases import AWARDS,CASES,SCOPE


class Magna(Multiball):
    def mark(self,label):
        row=super().mark(label);g=self.m.get;player=g(0x46b758)
        row.update(enabled=g(0x46e2dc,2),window=g(0x46e540,2),active=g(0x46e542,2),
            intro=g(0x4659b4),selected=g(0x4659b8),slot_countdown=g(0x4659bc),
            candidates=[g(0x46e240+4*i)for i in range(3)],
            magnets=[g(0x465864,2),g(0x465858,2)],
            held=[g(0x46c6d0),g(0x46c6d4)],mermaid=g(0x46e2d4),
            bonus_hold=g(player+20,2),extra_credits=g(player+16,2),
            extra_ball_lit=g(0x46e2d8,2),mode_lit=g(0x46e2de,2),kickback=g(0x46e534,2),
            capture=g(0x46c1b6,2),capture_wait=g(0x465a6c),
            x=g(0x46c15c),y=g(0x46c160),vx=g(0x46c170),vy=g(0x46c174))
        return row

    def wait(self,predicate,limit=5000):
        start=self.tick
        while not predicate():
            self.step();assert self.tick-start<limit,('wait',self.mark('blocked'))

    def parked_step(self):
        if self.tick%40==0 and self.m.get(0x46c1b4,2)==2:
            self.shot('parking',0,160,400)
        else:self.step()


def generate(case):
    r=Magna(0);r.initial();g=r.m.get
    r.shot('no_lock_lane_guard',0,34,468);assert g(0x46e540,2)==65535
    r.mark('no_lock_guard');r.cave('first_lock')
    r.mark('enabled_by_lock')
    award=int(case.rsplit('-',1)[1]) if case.startswith('magna-award-') else None
    delay,target=AWARDS[award] if award is not None else (0,int(case[-1]) if case.startswith('magna-slot-') else 0)
    until=r.tick+delay
    while r.tick<until:r.parked_step()
    r.shot('left_lane_arm',0,34,468);r.mark('armed')
    assert g(0x46e540,2)==400
    if case=='magna-expired':
        while g(0x46e540,2)!=65535:r.parked_step()
        r.mark('window_expired');r.shot('expired_top_trap',0,86,10)
        r.free();assert g(0x46e542,2)==0;r.mark('expired_normal_return')
    else:
        r.shot('top_trap',0,86,10)
        r.wait(lambda:g(0x46e542,2)!=0);initialized=r.mark('initialized')
        if award is not None:assert initialized['candidates'][target]==award,(case,initialized)
        natural=case.startswith('magna-natural-')
        if case!='magna-idle':
            r.key('left',True);r.key('right',True);r.mark('both_pressed')
        r.wait(lambda:g(0x46c1b4,2)==2)
        r.mark('field_released')
        if natural:
            if case.endswith('left'):r.key('right',False)
            until=r.tick+1800
            while r.tick<until:r.step()
            r.mark('magnet_flight')
            assert g(0x46e542,2)!=0 and g(0x46c1b4,2)==2
            r.key('left',False)
            if not case.endswith('left'):r.key('right',False)
            r.step();r.mark('flight_keys_released')
        elif case!='magna-idle':
            # Independent legal edges exercise both magnet fields.
            r.key('right',False);r.step();r.mark('left_only')
            r.key('left',False);r.key('right',True);r.step();r.mark('right_only')
            r.key('right',False);r.step();r.mark('both_released')
        if case in ('magna-escape','magna-idle') or natural:
            r.shot('field_exit',1,120,81);r.mark('exit_no_award')
            r.wait(lambda:g(0x46c1b4,2)==2);r.mark('normal_return')
        else:
            start=r.tick
            while g(0x4659b8)!=target:
                # Keep the original ball free; explicit waypoints bound this proof.
                r.parked_step();assert r.tick-start<400
            r.mark('before_award');r.shot('award_capture',1,120,14)
            r.mark('award_applied');assert g(0x46c1b4,2)==3 and g(0x46c1b6,2)==6
            r.wait(lambda:g(0x46c1b4,2)==2);r.mark('normal_return')
            assert g(0x46e542,2)==0
        r.shot('return_lane',2,70,340)
    trace=r.finish(case);trace['scope']=SCOPE
    (ROOT/'build/oracle/pirate-modes'/case/'trace.json').write_bytes(compact(trace)+b'\n')
    path=ROOT/f'analysis/traces/pirate-{case}.json';fixture=json.loads(path.read_text())
    fixture['scope']=SCOPE;path.write_text(json.dumps(fixture,indent=2)+'\n')
    return trace


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases',nargs='+',choices=CASES,default=CASES)
    args=parser.parse_args()
    for case in args.cases:generate(case)
    edges=Counter();included=[]
    for case in CASES:
        path=ROOT/'build/oracle/pirate-modes'/case/'trace.json'
        if not path.exists():continue
        t=json.loads(path.read_text());assert t['build_sha256']==BUILD_SHA;included.append(case)
        for e in t['executed_call_edges']:edges[(e['callsite'],e['target'])]+=e['count']
    (ROOT/'analysis/pirate-magna-boundary.json').write_text(json.dumps(dict(
        build_sha256=BUILD_SHA,cases=included,gameplay_stubs=[],scope=SCOPE,
        executed_call_edges=[dict(callsite=a,target=b,count=n)for(a,b),n in sorted(edges.items())]),indent=2)+'\n')


if __name__=='__main__':main()
