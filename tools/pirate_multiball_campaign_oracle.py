#!/usr/bin/env python3
"""Earn Storm/Battle/Mutiny from the verified Crocodile prefix, no rule writes."""
from collections import Counter
import json
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBP
from pirate_multiball_oracle import Multiball
from pirate_adventure_oracle import ROOT, BUILD_SHA, compact


class Campaign(Multiball):
    stage=''

    def qualified(self,label):
        return label if not self.stage or label.startswith(self.stage+':')else self.stage+':'+label

    def mark(self,label):
        label=self.qualified(label)
        if label.split(':')[-1]in ['parking','last_ball_parking','multiball_free_flight']:return {}
        row=super().mark(label);g=self.m.get
        row.update(jackpot_flags=list(self.m.u.mem_read(0x46e569,5)),
            field_46e560=g(0x46e560,2),field_46e562=g(0x46e562,2))
        return row

    def shot(self,label,layer,x,y,ball=0):
        super().shot(self.qualified(label),layer,x,y,ball)

    def wait_step(self,park=False,exclude=0):
        g=self.m.get;count=g(0x46c67c)
        free=[i for i in range(count)if i!=exclude and g(0x46c15c+100*i+0x58,2)==2]
        if park and free:
            if g(0x46e562,2)==2 and g(0x46e560,2):
                # Actual return-lane switch permits the next original ball release.
                self.shot('spawn_return_lane',2,70,340,free[-1]);return
            if self.tick%16==0:
                i=free[(self.tick//16)%len(free)]
                self.shot('parking',0,160,400,i);return
        self.step()

    @classmethod
    def resume(cls,prefix='crocodile'):
        r=cls(0);t=json.loads((ROOT/'build/oracle/pirate-modes'/prefix/'trace.json').read_text())
        assert t['build_sha256']==BUILD_SHA and t['deterministic_original_replay']
        keys={};shots={s['tick']:s for s in t['diagnostic_shots']}
        for e in t['inputs']:keys.setdefault(e['tick'],[]).append(e)
        for tick in range(t['tick_count']):
            for e in keys.get(tick,[]):r.apply_input(r.m,e)
            if tick in shots:
                s=shots[tick];r.m.shot(s['layer'],s['x'],s['y'],s.get('ball',0))
            r.step()
            assert r.states[-1]==t['states'][tick+1] and r.samples[-1]=={k:t[k][tick]for k in r.samples[-1]},('prefix',tick)
        r.inputs=t['inputs'];r.shots=t['diagnostic_shots'];r.milestones=t['milestones']
        r.m.calls=Counter({(int(e['callsite'],16),int(e['target'],16)):e['count']for e in t['executed_call_edges']})
        r.m.track_calls();r.compactions=[]
        def copied(u,pc,size,_):
            index=u.reg_read(UC_X86_REG_EAX);count=u.reg_read(UC_X86_REG_EBP)
            from pirate_adventure_oracle import digest
            source=bytes(u.mem_read(0x46c15c+100*count,100));dest=bytes(u.mem_read(0x46c15c+100*index,100))
            assert source==dest
            r.compactions.append(dict(tick=r.tick+1,stage=r.stage,index=index,old_count=count+1,new_count=count,
                source_sha256=digest(source),destination_sha256=digest(dest)))
        r.m.u.hook_add(UC_HOOK_CODE,copied,begin=0x4086c1,end=0x4086c1)
        r.m.u.ctl_remove_cache(0x400000,0x452000)
        return r

    def drain(self):
        g=self.m.get;start=self.tick;last=-1000
        while g(0x46c6ac)==4:
            if g(0x46c67c)>1 and g(0x46c1b4,2)==2 and self.tick-last>=300:
                self.shot('first_slot_drain',0,160,599);last=self.tick
            elif self.tick%16==0:
                free=[i for i in range(g(0x46c67c))if g(0x46c15c+100*i+0x58,2)==2 and (i!=0 or g(0x46c67c)==1)]
                if free:
                    i=free[(self.tick//16)%len(free)];self.shot('last_ball_parking',0,160,400,i)
                else:self.step()
            else:self.step()
            assert self.tick-start<14000,('drain',self.mark('blocked'))
        assert g(0x46c67c)==1 and g(0x46c6ac)==2
        self.mark('normal_return')


def play(r,name,ordinal):
    r.stage=name;g=r.m.get;r.mark('prepare')
    assert g(0x46e2be,2)==ordinal-1 and g(0x46e2bc,2)==0
    for i in range(ordinal+1):r.cave(f'lock_{i+1}')
    assert g(0x46e2bc,2)==ordinal+1
    result=r.cannon()
    assert result['phase']==4 and result['played_multiballs']==ordinal
    r.mark('mode_entered');start=r.tick
    expected=ordinal+1
    while g(0x46c67c)<expected or any(g(0x46c15c+100*i+0x58,2)!=2 for i in range(g(0x46c67c))):
        r.wait_step(park=True,exclude=-1);assert r.tick-start<6500,('spawn',r.mark('blocked_spawn'))
    assert g(0x46c67c)==expected;r.mark('all_balls_released')
    # Storm starts only target0 lit; an unlit2 still lights3.
    if ordinal==2:
        r.ramp('unlit_target',2);r.mark('unlit_target_guard')
        r.ramp('first_jackpot',3)
        r.ramp('duplicate_jackpot',3);r.mark('duplicate_guard')
        next_target=4
    else:
        r.ramp('first_jackpot',0)
        r.ramp('duplicate_jackpot',0);r.mark('duplicate_guard')
        next_target=1
    r.mark('before_growth');r.cave('jackpot_growth');r.mark('after_growth')
    r.ramp('raised_jackpot',next_target);r.mark('raised_jackpot_awarded')
    # A complete wrap proves the common clockwise next-target transition.
    for n in range(1,6):r.ramp(f'cycle_{n}',(next_target+n)%5)
    r.mark('cycle_complete');r.drain()


def main():
    r=Campaign.resume()
    for name,ordinal in [('storm',2),('battle',3),('mutiny',4)]:play(r,name,ordinal)
    t=r.finish('multiball-campaign')
    t.update(compactions=r.compactions,prefix_case='crocodile',
        scope='Integer-only original four-multiball campaign from reset via diagnostic free-ball events; keys only during cannon aiming/flight; no rules/timers/score/capture writes. Excludes original post-prefix x87 render XY/visibility/sorting; not full original raster or legal-key-only trajectory equivalence.')
    folder=ROOT/'build/oracle/pirate-modes/multiball-campaign'
    (folder/'trace.json').write_bytes(compact(t)+b'\n')
    path=ROOT/'analysis/traces/pirate-multiball-campaign.json';f=json.loads(path.read_text())
    for key in ['compactions','prefix_case','scope']:f[key]=t[key]
    path.write_text(json.dumps(f,indent=2)+'\n')
    (ROOT/'analysis/pirate-multiball-campaign-boundary.json').write_text(json.dumps(dict(
        build_sha256=BUILD_SHA,gameplay_stubs=[],
        executed_call_edges=t['executed_call_edges'],scope=t['scope']),indent=2)+'\n')


if __name__=='__main__':main()
