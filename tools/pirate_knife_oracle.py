#!/usr/bin/env python3
"""Original Knife Throwing: diagnostic table entry, then only legal keys.

No enemy/score/timer/award writes. Automatic aiming generates a frozen keyboard
schedule, independently replayed in a fresh original instance by Recorder.
"""
import argparse
from collections import Counter
import json
from pirate_modes_oracle import Recorder
from pirate_adventure_oracle import ROOT, BUILD_SHA


class Knife(Recorder):
    @staticmethod
    def fresh_original():
        m=Recorder.fresh_original()
        # Original configurable keyboard scan-code bindings, not gameplay state.
        m.put(0x46c5dc,0x2a);m.put(0x46c5e0,0x36)
        return m

    def key(self,action,down):
        event=dict(tick=self.tick,action=action,down=down)
        self.apply_input(self.m,event);self.inputs.append(event)

    def mark(self,label):
        row=super().mark(label);g=self.m.get
        row.update(video=g(0x46c6c0),intro=g(0x46e24c),player_x=g(0x46e29c),
            direction=g(0x46e294),remaining=g(0x46e230),award_flag=g(0x46e2d8,2),
            kill_score=g(0x46e298),spawn_period=g(0x46e238),
            enemies=[g(0x46e278+4*i)for i in range(5)],
            enemy_projectiles=[g(0x46e264+4*i)for i in range(5)],
            extra_credits=g(g(0x46b758)+16,2))
        return row


def generate(case):
    r=Knife(5);r.enter(release=False);m=r.m;held=0;last=24
    while m.get(0x46e24c)<364:r.step()
    r.mark('video_active')
    while m.get(0x46c6c0):
        if case=='knife-success' and r.tick%4==0:
            x=m.get(0x46e29c)
            active=[i for i in range(5)if m.get(0x46e278+4*i)<0x80000000]
            target=max(active,key=lambda i:m.get(0x46e278+4*i))if active else None
            goal=m.get(0x46e250+4*target)-48 if target is not None else x
            threats=[(m.get(0x46e264+4*i),m.get(0x46e250+4*i)-48)
                     for i in range(5)if m.get(0x46e264+4*i)<40]
            for age,bx in sorted(threats,reverse=True):
                if age>=24 and abs(x-bx)<=11:
                    goal=bx-12 if x<bx else bx+12
                    if goal<0:goal=bx+12
                    if goal>96:goal=bx-12
                    break
            desired=-1 if x>goal else 1 if x<goal else 0
            if desired!=held:
                if held:r.key('left'if held<0 else 'right',False)
                if desired:r.key('left'if desired<0 else 'right',True)
                held=desired
            if target is not None and abs(x-goal)<=3 and r.tick%20==0:
                r.key('enter',True);r.key('enter',False)
        r.step()
        remaining=m.get(0x46e230)
        if remaining!=last:r.mark('kill_'+str(25 if remaining==0xffffffff else 24-remaining));last=remaining
        assert r.tick<15000,'Knife did not finish'
    if held:r.key('left'if held<0 else 'right',False)
    end=r.mark('video_result')
    assert end['award_flag']==int(case=='knife-success')
    if case=='knife-success':assert last==0xffffffff and end['kill_score']==75000000
    else:assert last==24 and end['kill_score']==0
    # Actual result animation/return/capture release; no synthetic completion.
    r.free();r.mark('normal_play_return')
    r.shot('return_lane',2,70,340)
    # Prove earned Extra Ball is collected by the original normal-play chain.
    if case=='knife-success':
        r.shot('upper_trap_guard',0,86,10);r.free()
        guard=r.mark('upper_trap_does_not_collect')
        assert guard['award_flag']==1 and guard['extra_credits']==0
        r.ramp('extra_ball_right_trap',0)
        collected=r.mark('extra_ball_collected')
        assert collected['award_flag']==0 and collected['extra_credits']==1
    trace=r.finish(case)
    return trace


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cases',nargs='+',choices=['knife-success','knife-failure'],default=['knife-success','knife-failure'])
    args=p.parse_args()
    for case in args.cases:generate(case)
    edges=Counter();included=[]
    for case in ['knife-success','knife-failure']:
        path=ROOT/'build/oracle/pirate-modes'/case/'trace.json'
        if not path.exists():continue
        t=json.loads(path.read_text());assert t['build_sha256']==BUILD_SHA;included.append(case)
        for edge in t['executed_call_edges']:edges[(edge['callsite'],edge['target'])]+=edge['count']
    (ROOT/'analysis/pirate-knife-boundary.json').write_text(json.dumps(dict(
        build_sha256=BUILD_SHA,cases=included,gameplay_stubs=[],
        executed_call_edges=[dict(callsite=a,target=b,count=n)for(a,b),n in sorted(edges.items())],
        scope='Actual Knife input/video/result callbacks; diagnostic table entry and post-video trap'),indent=2)+'\n')


if __name__=='__main__':main()
