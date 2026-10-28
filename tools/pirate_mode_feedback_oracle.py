#!/usr/bin/env python3
"""Real Adventure events admitted after prior DMD completion; no priority writes."""
import argparse,json
from collections import Counter
from unicorn import UC_HOOK_CODE
from pirate_modes_oracle import Recorder
from pirate_adventure_oracle import Original,ROOT,BUILD_SHA,compact

TARGETS={'sword':[0x42f0cc,0x42f130],'dive':[0x42f3e8,0x4300b4],'monkey':[0x42f6ec,0x42f800]}

class Feedback(Recorder):
    @staticmethod
    def fresh_original():
        m=Original(ROOT/'build/oracle/pirate-full-tick')
        # Existing entry helpers request broad tracking; a single actual dispatcher
        # hook suffices here and does not slow physics/park waits.
        m.track_calls=lambda:None;m.pause_calls=lambda:None
        m.dispatch=[];m.dispatch_tick=0
        def dispatch(u,address,size,_):
            target=m.get(0x46c69c);m.calls[(address,target)]+=1
            m.dispatch.append(dict(target=target,tick=m.dispatch_tick))
        m.dispatch_hook=m.u.hook_add(UC_HOOK_CODE,dispatch,begin=0x407c09,end=0x407c09)
        return m

    def step(self):
        self.m.dispatch_tick=self.tick+1
        super().step()

    def park(self):
        if self.m.get(0x46c1b4,2)==2 and self.tick%40==0:
            self.shot('timeout_free_flight',0,160,400)
        else:self.step()

    def idle(self):
        start=self.tick
        while self.m.get(0x46c68c)!=0:
            self.park();assert self.tick-start<2400,('display not idle',self.tick,hex(self.m.get(0x46c69c)),self.m.get(0x46c690))
        self.mark('display_idle')

    def admit(self,label,target,event):
        self.idle();start=len(self.m.dispatch);tick=self.tick
        event()
        for _ in range(40):
            if any(row['target']==target for row in self.m.dispatch[start:]):break
            self.park()
        assert any(row['target']==target for row in self.m.dispatch[start:]),('callback not admitted',label,self.tick,hex(self.m.get(0x46c69c)),self.m.get(0x46c68c),self.m.get(0x46c694),self.m.get(0x46c6bc))
        self.mark('dispatch_'+hex(target))
        self.idle()
        calls=[row for row in self.m.dispatch[start:]if row['target']==target]
        self.events.append(dict(label=label,event_tick=tick,target=hex(target),
            first_dispatch_tick=calls[0]['tick'],last_dispatch_tick=calls[-1]['tick'],
            dispatch_count=len(calls),idle_after_tick=self.tick,
            distinct_dmd_frames=len({row['dmd_sha256']for row in self.samples[tick:self.tick]})))


def generate(case):
    r=Feedback({'sword':1,'dive':2,'monkey':3}[case]);r.events=[];r.enter()
    if case=='sword':
        r.admit('sword_jackpot_increase',0x42f0cc,lambda:r.shot('bumper_growth',0,169,38))
        r.admit('sword_jackpot_collect',0x42f130,lambda:r.ramp('raised_jackpot',4))
    elif case=='dive':
        r.admit('dive_rate_increase',0x42f3e8,lambda:r.shot('bumper_descent_rate',0,169,38))
        r.admit('dive_progress',0x4300b4,lambda:r.ramp('dive_ramp',4))
    else:
        r.admit('monkey_first_piece',0x42f6ec,lambda:r.ramp('map_piece_1',1))
        for ident in [2,3,4]:
            r.admit('monkey_piece_'+str(ident),0x42f6ec,lambda ident=ident:r.ramp('map_piece_'+str(ident),ident))
        r.admit('monkey_final_piece',0x42f800,lambda:r.ramp('map_piece_0',0))
    name='feedback-'+case;trace=r.finish(name);trace['feedback_events']=r.events
    folder=ROOT/'build/oracle/pirate-modes'/name;(folder/'trace.json').write_bytes(compact(trace)+b'\n')
    path=ROOT/'analysis/traces'/('pirate-'+name+'.json');fixture=json.loads(path.read_text());fixture['feedback_events']=r.events;path.write_text(json.dumps(fixture,indent=2)+'\n')
    return trace


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cases',nargs='+',choices=list(TARGETS),default=list(TARGETS));a=p.parse_args()
    for case in a.cases:generate(case)
    edges=Counter();included=[]
    for case in TARGETS:
        path=ROOT/'build/oracle/pirate-modes'/('feedback-'+case)/'trace.json'
        if not path.exists():continue
        t=json.loads(path.read_text());assert t['build_sha256']==BUILD_SHA;included.append('feedback-'+case)
        for e in t['executed_call_edges']:edges[e['callsite'],e['target']]+=e['count']
    (ROOT/'analysis/pirate-mode-feedback-boundary.json').write_text(json.dumps(dict(build_sha256=BUILD_SHA,cases=included,gameplay_stubs=[],
        executed_call_edges=[dict(callsite=a,target=b,count=n)for(a,b),n in sorted(edges.items())],
        scope='Actual407c09 dispatch after original Adventure events admitted following previous DMD completion; diagnostic free-ball waypoints only.'),indent=2)+'\n')

if __name__=='__main__':main()
