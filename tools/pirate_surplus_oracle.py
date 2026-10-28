#!/usr/bin/env python3
"""Actual five-Cave-lock cap and surplus jackpots across all four multiballs.

No rule/score/timer/ball-state injections. Waypoints move only canonical free
balls on real DAT layers. A watchpoint observes46e556; it never arms it.
"""
import json
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBP,UC_X86_REG_EIP
from pirate_multiball_campaign_oracle import Campaign
from pirate_adventure_oracle import ROOT,BUILD_SHA,compact,digest

CASE='multiball-surplus'
STAGES=[('crocodile',1),('storm',2),('battle',3),('mutiny',4)]

class Surplus(Campaign):
    def shot(self,label,layer,x,y,ball=0):
        # Existing retained CFG already covers these families. Observe actual
        # event steps only; broad per-instruction call hooks cost~130x.
        trace=label not in ('parking','last_ball_parking','multiball_free_flight','spawn_return_lane')
        if trace:self.m.track_calls()
        super().shot(label,layer,x,y,ball)
        if trace:self.m.pause_calls()

    def wait(self,predicate,limit=5000,park=False):
        start=self.tick
        while not predicate():
            self.wait_step(park=park,exclude=-1)
            assert self.tick-start<limit,('wait',self.mark('blocked'))

    def mark(self,label):
        row=super().mark(label)
        if row:row.update(field_4659a0=self.m.get(0x4659a0))
        return row


def main():
    r=Surplus(0);r.initial();m=r.m;m.pause_calls();g=m.get;r.compactions=[];writes=[]
    def copied(u,pc,size,_):
        index=u.reg_read(UC_X86_REG_EAX);count=u.reg_read(UC_X86_REG_EBP)
        source=bytes(u.mem_read(0x46c15c+100*count,100));dest=bytes(u.mem_read(0x46c15c+100*index,100))
        assert source==dest
        r.compactions.append(dict(tick=r.tick+1,stage=r.stage,index=index,old_count=count+1,new_count=count,
            source_sha256=digest(source),destination_sha256=digest(dest)))
    def watch(u,access,address,size,value,_):
        writes.append(dict(tick=r.tick,stage=r.stage,pc=hex(u.reg_read(UC_X86_REG_EIP)),
            address=hex(address),size=size,value=value))
    m.u.hook_add(UC_HOOK_CODE,copied,begin=0x4086c1,end=0x4086c1)
    m.u.hook_add(UC_HOOK_MEM_WRITE,watch,begin=0x46e556,end=0x46e557)
    m.u.ctl_remove_cache(0x400000,0x452000)
    for name,ordinal in STAGES:
        r.stage=name;r.mark('prepare')
        assert g(0x46e2bc,2)==0 and g(0x46e2be,2)==ordinal-1
        for i in range(5):r.cave(f'lock_{i+1}')
        assert g(0x46e2bc,2)==5
        r.cave('sixth_lock_guard');r.mark('cap_guard')
        assert g(0x46e2bc,2)==5
        result=r.cannon();assert result['phase']==4 and result['played_multiballs']==ordinal
        r.mark('mode_entered');start=r.tick
        while g(0x46e55e,2) or g(0x46c67c)<5 or any(g(0x46c15c+100*i+0x58,2)!=2 for i in range(g(0x46c67c))):
            r.wait_step(park=True,exclude=-1);assert r.tick-start<9000,('spawn',r.mark('blocked_spawn'))
        r.mark('all_balls_released');assert g(0x46c67c)==5
        expected={1:12500000,2:15000000,3:17500000,4:20000000}[ordinal]
        assert g(0x46e2a0)==expected
        r.ramp('first_jackpot',0);r.mark('first_jackpot_awarded')
        r.ramp('duplicate_jackpot',0);r.mark('duplicate_guard')
        r.mark('before_growth');r.cave('jackpot_growth');r.mark('after_growth')
        assert g(0x46e2a0)==expected+1000000
        r.ramp('raised_jackpot',1);r.mark('raised_jackpot_awarded')
        for i in [2,3,4,0,1]:r.ramp('cycle_'+str(i),i)
        r.mark('cycle_complete')
        if ordinal==3:
            assert g(0x46e556,2)==0
            r.wait(lambda:g(0x465a50)>=0x80000000,park=True)
            r.mark('before_unarmed_top_trap');r.shot('unarmed_top_trap',0,86,10);r.free();r.mark('after_unarmed_top_trap')
            assert g(0x46e556,2)==0
        r.drain();assert g(0x46e2bc,2)==0
    trace=r.finish(CASE)
    trace.update(compactions=r.compactions,super_jackpot_writes=writes,
        scope=__doc__,prefix_case=None,
        call_edge_coverage='Selected actual event steps only; waits/parking unhooked. Full state independently replayed from reset.')
    folder=ROOT/'build/oracle/pirate-modes'/CASE;(folder/'trace.json').write_bytes(compact(trace)+b'\n')
    path=ROOT/f'analysis/traces/pirate-{CASE}.json';fixture=json.loads(path.read_text())
    for key in ['compactions','super_jackpot_writes','scope','prefix_case','call_edge_coverage']:fixture[key]=trace[key]
    path.write_text(json.dumps(fixture,indent=2)+'\n')
    (ROOT/'analysis/pirate-surplus-boundary.json').write_text(json.dumps(dict(build_sha256=BUILD_SHA,
        gameplay_stubs=[],executed_call_edges=trace['executed_call_edges'],scope=__doc__),indent=2)+'\n')

if __name__=='__main__':main()
