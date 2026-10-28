#!/usr/bin/env python3
"""Earn Pirate's finale after a frozen four-multiball prefix and six Adventures."""
import argparse
import json
from pirate_multiball_campaign_oracle import Campaign
from pirate_adventure_oracle import ROOT,BUILD_SHA,compact

SCOPE=('Integer-only original four-multiball prefix -> six actual Adventures -> '
       'Treasure Island; diagnostic canonical free-ball waypoints, real inputs, '
       'no rule/score/timer/capture/completion writes. Excludes post-prefix x87 '
       'render XY/visibility/sorting; not a legal-key-only full game.')


class Final(Campaign):
    events_active=False

    def mark(self,label):
        row=super().mark(label)
        if not row:return row
        g=self.m.get;row.update(mode_gate=g(0x4659c0),video=g(0x46c6c0),
            pending_balls=g(0x46e55e,2),extra_ball_lit=g(0x46e2d8,2),
            field_46e53e=g(0x46e53e,2),aggregate=g(0x46e28c),last_award=g(0x46e2ac))
        return row

    def wait_step(self,park=False,exclude=0):
        g=self.m.get
        if self.events_active and park and g(0x46c6ac)==4 and g(0x46e560,2):
            free=[i for i in range(g(0x46c67c)) if i!=exclude and g(0x46c15c+100*i+0x58,2)==2]
            if free:
                self.shot('shared_gate_return_lane',2,70,340,free[-1]);return
        super().wait_step(park=park,exclude=exclude)

    def wait(self,predicate,limit=5000,park=False):
        start=self.tick
        while not predicate():
            self.wait_step(park=park,exclude=-1)
            assert self.tick-start<limit,('wait',self.mark('blocked'))

    def adventure(self,mode,stage=None,multiballs=4):
        self.stage=stage or ['plank','sword','dive','monkey','shark','knife'][mode]
        g=self.m.get
        self.mark('prepare')
        for n in range(7):
            if g(0x46e2c0,2)==mode:break
            self.shot(f'select_{n}',0,169,38)
        assert g(0x46e2c0,2)==mode
        self.shot('right_ramp_arm',1,225,45)
        self.shot('upper_left_entry',0,24,60)
        self.wait(lambda:g(0x46c6ac)in (4,5))
        assert g(0x46c6ac)==5,('premature final',self.mark('unexpected_final'))
        self.mark('entered')
        if mode==5:
            assert g(0x46c6c0)==1
            self.wait(lambda:g(0x46c6c0)==0,limit=16000)
            self.mark('video_result')
        self.free();self.shot('return_lane',2,70,340)
        if mode==0:
            for ident in [4,2,3,1,0]:self.ramp('rope_'+str(ident),ident)
            assert g(0x46e556,2)==1
            self.shot('super_jackpot',0,86,10);self.free()
        elif mode==1:
            self.ramp('jackpot',4)
            # Original expiry, not a timer write. Existing original callback
            # family already covered in the separate Sword fixture.
            self.m.pause_calls();start=self.tick
            while g(0x46c6ac)==5:
                if g(0x46e546,2)<=8:self.m.track_calls()
                self.wait_step(park=True,exclude=-1)
                assert self.tick-start<16000
        elif mode==2:
            self.shot('rate_boost',0,169,38)
            for n in range(12):
                if g(0x46e54a,2)>=100:break
                self.ramp('depth_'+str(n),4)
            assert g(0x46e54a,2)==100
            self.shot('super_jackpot',0,86,10);self.free()
        elif mode==3:
            for ident in [1,2,3,4,0]:self.ramp('map_'+str(ident),ident)
        elif mode==4:
            self.ramp('speed_1',4);self.shot('bumper_speed',0,169,38)
            self.shot('target_speed',0,145,234)
            self.ramp('speed_2',2);self.ramp('speed_3',3)
            self.wait(lambda:g(0x46c6ac)!=5,limit=1000,park=True)
        assert g(0x46c6ac)==2 and g(0x46e2be,2)==multiballs
        self.free();self.mark('normal_return')
        self.shot('return_lane_after_mode',2,70,340)


def earn():
    r=Final.resume('multiball-campaign');g=r.m.get;r.stage='prefix';r.mark('four_multiballs_retained')
    for mode in [5,0,1,2,3,4]:r.adventure(mode)
    r.stage='final';r.mark('earned_ready')
    assert list(r.m.u.mem_read(0x46e2c2,6))==[1]*6 and g(0x46e2be,2)==4
    assert g(0x4659c0)!=0
    r.shot('upper_left_entry',0,24,60)
    r.wait(lambda:g(0x46c6ac)==4);r.mark('entered')
    r.wait(lambda:g(0x46c67c)>=4,limit=10000,park=True)
    r.mark('release_progress')
    r.wait(lambda:g(0x46e55e,2)==0 and all(g(0x46c15c+100*i+0x58,2)==2 for i in range(g(0x46c67c))),limit=10000,park=True)
    r.mark('all_balls_released')
    return r


def publish(r,case):
    trace=r.finish(case)
    trace.update(prefix_case='multiball-campaign',compactions=r.compactions,scope=SCOPE,
        call_edge_coverage='Observed indirect edges; Sword wait hooks paused; complete step state independently replayed without hooks.')
    folder=ROOT/'build/oracle/pirate-modes'/case;(folder/'trace.json').write_bytes(compact(trace)+b'\n')
    path=ROOT/f'analysis/traces/pirate-{case}.json';fixture=json.loads(path.read_text())
    for key in ['prefix_case','compactions','scope','call_edge_coverage']:fixture[key]=trace[key]
    path.write_text(json.dumps(fixture,indent=2)+'\n')
    return trace


def events(r):
    r.events_active=True
    r.stage='final';g=r.m.get
    assert g(0x46c67c)==8 and all(g(0x46c15c+100*i+0x58,2)==2 for i in range(8))
    def trap(label):
        # Same original shared cooldown as a real ball would encounter.
        r.wait(lambda:g(0x465a50)>=0x80000000,park=True)
        r.shot(label,0,86,10)
        assert g(0x46c1b4,2)==3,('top trap rejected',r.mark('blocked_trap'))
        r.free()
    trap('unarmed_top_trap');r.mark('unarmed_trap_guard')
    assert g(0x46e556,2)==0 and g(0x46e298)==0
    r.shot('other_ball_target',1,81,228,1);r.mark('other_ball_jackpot')
    trap('guard_super_trap');r.mark('guard_super_return')
    r.ramp('first_jackpot',4)
    r.ramp('duplicate_jackpot',4);r.mark('duplicate_guard')
    r.mark('before_growth');r.cave('jackpot_growth');r.mark('after_growth')
    r.ramp('raised_jackpot',2)
    trap('super_jackpot_trap');r.mark('super_jackpot_return')
    for ident in range(5):r.ramp('sweep_'+str(ident),ident)
    r.mark('all_targets_cleared')
    trap('second_super_trap');r.mark('second_super_return')
    r.drain()
    publish(r,'final-return')


def next_cycle(r):
    r.stage='final'
    r.shot('post_final_return_lane',2,70,340)
    # Prove that entry's progress reset admits a new actual Adventure cycle.
    r.adventure(0,stage='next_plank',multiballs=0)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--resume-entry',action='store_true',help='Replay the independently frozen private entry prefix')
    p.add_argument('--resume-return',action='store_true',help='Replay the independently frozen final-return checkpoint')
    args=p.parse_args()
    if args.resume_return:
        r=Final.resume('final-return')
        r.compactions=json.loads((ROOT/'build/oracle/pirate-modes/final-return/trace.json').read_text())['compactions']
    elif args.resume_entry:r=Final.resume('final-entry')
    else:
        r=earn();publish(r,'final-entry')
    if not args.resume_return:events(r)
    next_cycle(r);trace=publish(r,'final-campaign')
    (ROOT/'analysis/pirate-final-boundary.json').write_text(json.dumps(dict(build_sha256=BUILD_SHA,
        gameplay_stubs=[],scope=SCOPE,call_edge_coverage=trace['call_edge_coverage'],executed_call_edges=trace['executed_call_edges']),indent=2)+'\n')


if __name__=='__main__':main()
