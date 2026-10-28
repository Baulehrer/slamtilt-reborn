#!/usr/bin/env python3
"""Earn Magna eligibility flags through original gameplay, then observe fallbacks.

Diagnostic canonical free-ball waypoints; no rule/RNG/score/timer injection.
Delay search runs cloned original contexts; every published schedule independently
replays from initial reset. Selected-event call traces only; complete step states.
"""
import argparse,json
from unicorn import UC_HOOK_CODE
from pirate_magna_oracle import Magna
from pirate_multiball_campaign_oracle import Campaign
from pirate_adventure_oracle import Original,ROOT,BUILD_SHA,compact

CASES=['magna-mode-lit','magna-bonus-held','magna-kickback-lit','magna-all-played']

def raw_values(seed):return [(seed>>(8*n))&127 for n in range(3)]
def nominal(raw):
    for threshold,ident in [(1,0),(3,1),(15,2),(30,3),(40,4),(55,5),(65,6),(75,7),(90,8),(100,9),(110,10)]:
        if raw<threshold:return ident
    return 11

class Eligibility(Magna,Campaign):
    def __init__(self):
        super().__init__(0);self.source_values=[]
        def source(u,pc,size,_):self.source_values.append(self.m.get(self.m.get(0x46e2b0)+0x3c))
        self.m.u.hook_add(UC_HOOK_CODE,source,begin=0x431e77,end=0x431e77)
    def mark(self,label):
        row=super().mark(label)
        if row and self.source_values:
            row.update(source_value=self.source_values[-1],raw_candidates=raw_values(self.source_values[-1]))
        return row
    def shot(self,label,layer,x,y,ball=0):
        traced=label not in ('parking','last_ball_parking','multiball_free_flight','spawn_return_lane')
        if traced:self.m.track_calls()
        super().shot(label,layer,x,y,ball)
        if traced:self.m.pause_calls()
    def parked_step(self):
        if self.tick%40==0 and self.m.get(0x46c1b4,2)==2:self.shot('parking',0,160,400)
        else:self.step()
    def wait(self,predicate,limit=5000,park=False):
        start=self.tick
        while not predicate():
            if park:self.wait_step(park=True,exclude=-1)
            else:self.step()
            assert self.tick-start<limit,('wait',self.mark('blocked'))
    def magna(self,label,wanted,nominal_id=None,first_slot=False):
        self.stage=label;g=self.m.get;assert g(0x46e2dc,2)!=0 and g(0x46c1b4,2)==2
        self.mark('eligible_before_entry')
        trial=Original(ROOT/'build/oracle/pirate-full-tick');captured=[]
        trial.u.hook_add(UC_HOOK_CODE,lambda u,pc,size,_:captured.append(trial.get(trial.get(0x46e2b0)+0x3c)),begin=0x431e77,end=0x431e77)
        # Clone complete mutable VM ranges, never overwrite live gameplay state.
        for attempt in range(768):
            if g(0x46c1b4,2)!=2:self.step();continue
            for address,length in [(0x400000,0x100000),(0x1000000,0x400000),(0x2000000,0x10000)]:
                trial.u.mem_write(address,bytes(self.m.u.mem_read(address,length)))
            trial.u.context_restore(self.m.u.context_save());captured.clear()
            trial.shot(0,34,468);trial.step(self.tick)
            trial.shot(0,86,10);trial.step(self.tick+1)
            n=self.tick+2
            while not trial.get(0x46e542,2) and n<self.tick+1000:trial.step(n);n+=1
            assert captured and trial.get(0x46e542,2),'Magna admission failed'
            raw=raw_values(captured[-1]);candidates=[trial.get(0x46e240+4*i)for i in range(3)]
            found=[i for i in range(1 if first_slot else 3)if candidates[i]==wanted and (nominal_id is None or nominal(raw[i])==nominal_id)]
            if found:slot=found[0];break
            self.parked_step()
        else:raise AssertionError(('No candidate',wanted,nominal_id))
        self.mark('delay_selected');self.shot('left_lane_arm',0,34,468);self.shot('top_trap',0,86,10)
        self.wait(lambda:g(0x46e542,2)!=0);init=self.mark('initialized')
        assert init['candidates']==candidates and init['raw_candidates']==raw
        self.key('left',True);self.key('right',True);self.wait(lambda:g(0x46c1b4,2)==2)
        self.key('left',False);self.key('right',False);self.step();self.mark('field_released')
        start=self.tick
        while g(0x4659b8)!=slot:
            self.parked_step();assert self.tick-start<400
        self.mark('before_award');self.shot('award_capture',1,120,14);self.mark('award_applied')
        assert g(0x46c1b4,2)==3 and g(0x46c1b6,2)==6
        self.wait(lambda:g(0x46c1b4,2)==2);self.mark('normal_return');self.shot('return_lane',2,70,340)
        return wanted

def prefix(r):
    t=json.loads((ROOT/'build/oracle/pirate-modes/final-campaign/trace.json').read_text())
    count=next(m['tick']for m in t['milestones']if m['label']=='final:earned_ready')
    keys={};shots={s['tick']:s for s in t['diagnostic_shots']if s['tick']<count}
    for e in t['inputs']:
        if e['tick']<count:keys.setdefault(e['tick'],[]).append(e)
    for tick in range(count):
        for e in keys.get(tick,[]):r.apply_input(r.m,e)
        if tick in shots:
            s=shots[tick];r.m.shot(s['layer'],s['x'],s['y'],s.get('ball',0))
        r.step()
        assert r.states[-1]==t['states'][tick+1]and r.samples[-1]=={k:t[k][tick]for k in r.samples[-1]},('prefix',tick)
    r.inputs=[e for e in t['inputs']if e['tick']<count];r.shots=[e for e in t['diagnostic_shots']if e['tick']<count]
    # Keep the complete frozen vectors, but only add new Magna landmarks here.
    r.stage='earned_prefix';r.mark('all_six_played')
    assert list(r.m.u.mem_read(0x46e2c2,6))==[1]*6 and r.m.get(0x46e2de,2)==0
    return count

def generate(case):
    r=Eligibility();g=r.m.get;prefix_ticks=0
    if case=='magna-all-played':prefix_ticks=prefix(r)
    else:r.initial();r.m.pause_calls()
    r.stage='setup';r.cave('first_lock')
    if case=='magna-mode-lit':
        r.shot('right_ramp_arm',1,225,45);assert g(0x46e2de,2)!=0
        r.magna('fallback',3,2)
    elif case=='magna-all-played':r.magna('fallback',3,2,first_slot=True)
    else:
        reward={'magna-bonus-held':4,'magna-kickback-lit':10}[case]
        r.magna('earned',reward)
        r.stage='reenable';r.cave('second_lock');assert g(0x46e2bc,2)==2
        r.cannon();r.wait(lambda:g(0x46c67c)==2 and all(g(0x46c15c+100*i+0x58,2)==2 for i in range(2)),park=True)
        r.mark('multiball_released');r.drain();r.cave('new_first_lock')
        assert (g(g(0x46b758)+20,2)!=0)if reward==4 else g(0x46e534,2)!=0
        r.magna('fallback',5 if reward==4 else 11,reward)
    trace=r.finish(case);trace.update(scope=__doc__,prefix_ticks=prefix_ticks,call_edge_coverage='Selected new event steps only; prefix/waits unhooked; complete state replay from reset.')
    folder=ROOT/'build/oracle/pirate-modes'/case;(folder/'trace.json').write_bytes(compact(trace)+b'\n')
    path=ROOT/f'analysis/traces/pirate-{case}.json';f=json.loads(path.read_text())
    for key in ['scope','prefix_ticks','call_edge_coverage']:f[key]=trace[key]
    path.write_text(json.dumps(f,indent=2)+'\n')
    return trace

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cases',nargs='+',choices=CASES,default=CASES);a=p.parse_args()
    for case in a.cases:generate(case)
    edges={}
    for case in CASES:
        path=ROOT/'build/oracle/pirate-modes'/case/'trace.json'
        if not path.exists():continue
        for e in json.loads(path.read_text())['executed_call_edges']:edges[(e['callsite'],e['target'])]=e
    (ROOT/'analysis/pirate-magna-eligibility-boundary.json').write_text(json.dumps(dict(build_sha256=BUILD_SHA,gameplay_stubs=[],executed_call_edges=list(edges.values())),indent=2)+'\n')
if __name__=='__main__':main()
