#!/usr/bin/env python3
"""Actual MagnaTable trigger/admission/cooldown/Tilt events vs native/reset/SDL."""
import argparse,json,os,subprocess
from pathlib import Path
from verify_pirate_modes import ROOT,read,sha
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity

CASES=['trigger-edge','exit-edge','cooldown','tilt-free','tilt-held','admit-last','admit-late']


def contracts(case,t):
    marks={m['label']:m for m in t['milestones']}
    def m(label):return marks[label]
    def score(label):return int(m(label)['score_bcd'])
    def route(label):
        matches=[r for r in t['capture_routes']if r['tick']==m(label)['tick']]
        assert len(matches)==1,(case,label,matches)
        return matches[0]
    base=m('frozen_prefix')
    if case.startswith('admit-'):
        onset=2760 if case=='admit-last' else 2761
        obs=t['initializer_observations'];assert obs==[dict(tick=onset+52,window=0 if case=='admit-last' else 65535)]
        assert m('before_top_trap')['tick']==onset and m('before_top_trap')['window']==12
        assert m('admission_result')['active']==(65535 if case=='admit-last' else 0)
        assert m('normal_return')['ball_state']==2 and m('normal_return')['active']==0
    elif case=='trigger-edge':
        outside=m('outside_capture_bitmap');inside=m('capture_admitted')
        assert outside['active']==65535 and outside['ball_state']==2
        assert outside['route_count']==base['route_count']
        assert inside['ball_state']==3 and inside['capture']==6 and inside['capture_wait']==150
        assert inside['active']==0 and inside['magnets']==[0,0]
        assert score('capture_admitted')-score('outside_capture_bitmap')==5000000
        assert route('inside_capture_bitmap')['y']==17*65536
    elif case=='exit-edge':
        outside=m('outside_exit_bitmap');inside=m('exit_admitted')
        assert outside['route_count']==base['route_count']and outside['active']==65535
        assert inside['ball_state']==7 and inside['active']==0 and inside['magnets']==[0,0]
        assert score('exit_admitted')==score('outside_exit_bitmap')
        assert route('inside_exit_bitmap')['y']==81*65536
    elif case=='cooldown':
        release=m('first_release');assert release['cooldown']==10 and release['capture_wait']==0
        for label,value in [('cooldown_ten_rejected',10),('cooldown_zero_rejected',0)]:
            row=m(label);assert row['ball_state']==2 and row['cooldown']==value
            assert score(label)==score('first_release')
        assert route('cooldown_ten_rejects')['cooldown']==10
        assert route('cooldown_zero_rejects')['cooldown']==0
        ready=m('cooldown_negative_ready')
        assert ready['cooldown']==0xffffffff and ready['tick']==(release['tick']//4+11)*4
        recapture=m('second_capture_admitted');assert recapture['ball_state']==3 and recapture['capture_wait']==150
        assert route('cooldown_negative_admits')['cooldown']==0xffffffff
        # This is a diagnostic re-placement in the released layer, not a claimed
        # normal second Magna entry. Original routing has no active-flag guard.
        assert route('cooldown_negative_admits')['active']==0
        assert score('second_capture_admitted')-score('first_release')==5000000
    elif case=='tilt-free':
        blocked=m('tilted_capture_guard');exited=m('tilted_exit_clears_field')
        assert blocked['tilt']!=0 and blocked['active']==65535 and blocked['ball_state']==2
        assert route('tilted_capture_rejected')['tilt']!=0
        assert exited['active']==0 and exited['ball_state']==7 and exited['magnets']==[0,0]
        assert score('tilted_exit_clears_field')==score('frozen_prefix')
    else:
        before=m('captured_before_tilt');released=m('tilt_bypasses_hold_without_cooldown')
        assert before['ball_state']==3 and before['capture_wait']==150
        assert released['tilt']!=0 and released['ball_state']==2
        assert 0<released['capture_wait']<150 and released['cooldown']==0xffffffff
        assert released['tick']-before['tick']<150
        assert score('tilt_bypasses_hold_without_cooldown')==score('captured_before_tilt')
    return dict(case=case,steps=t['tick_count'],prefix_case=t['prefix_case'],prefix_steps=t['prefix_steps'])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe')
    p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview')
    p.add_argument('--original-only',action='store_true');a=p.parse_args()
    game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    dat=game/'DAT/PIRATE.DAT';prepared=ROOT/'build/oracle/pirate-full-tick'
    bsha,dsha=sha((game/'SLAMTILT.EXE').read_bytes()),sha(dat.read_bytes())
    boundary=read(ROOT/'analysis/pirate-magna-capture-boundary.json')
    assert boundary['cases']==['magna-capture-'+c for c in CASES]and not boundary['gameplay_stubs']
    reports=[];traces={}
    for case in CASES:
        folder=ROOT/f'build/oracle/pirate-modes/magna-capture-{case}';path=folder/'trace.json'
        t=read(path);f=read(ROOT/f'analysis/traces/pirate-magna-capture-{case}.json')
        n=integrity(t,f,bsha,dsha)
        for key in ['capture_routes','initializer_observations','prefix_case','prefix_steps']:assert t[key]==f[key]
        source=read(ROOT/f'build/oracle/pirate-modes/{t["prefix_case"]}/trace.json')
        source_fixture=read(ROOT/f'analysis/traces/pirate-{t["prefix_case"]}.json')
        integrity(source,source_fixture,bsha,dsha)
        for key in KEYS:
            length=t['prefix_steps']+(key=='states');assert t[key][:length]==source[key][:length],(case,'frozen prefix',key)
        reports.append(contracts(case,t));traces[case]=t
        if a.original_only:continue
        native=folder/'native-verified.json';rendered=folder/'rendered-verified.json'
        subprocess.run([a.native,prepared,dat,native,str(n),'--full','--lamps','--replay',path,'--diagnostic-shots',path],check=True)
        subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames',str(n//4),'--no-audio',
            '--replay',path,'--diagnostic-shots',path,'--trace-output',rendered],check=True,
            env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
        for label,out in [('native/reset',read(native)),('SDL',read(rendered))]:
            assert out['tick_count']==n and out.get('error','')==''
            for key in KEYS:assert out[key]==t[key],(case,label,key)
        print(case,n,'original/native/reset/SDL9vectors exact',flush=True)
    # Both trap-boundary schedules remain identical until the earlier shot.
    for key in KEYS:
        length=2760+(key=='states');assert traces['admit-last'][key][:length]==traces['admit-late'][key][:length],('paired admission prefix',key)
    result=dict(status='ORIGINAL VERIFIED'if a.original_only else'VERIFIED',cases=reports,
        total_steps=sum(r['steps']for r in reports),build_sha256=bsha,dat_sha256=dsha,
        scope='Original DAT switch events after physics, declared free-ball waypoints only. Rectangle boundaries are not all directly bitmap-reachable. Diagnostic re-placement after cooldown does not prove normal repeated-mode entry. Occupied-capture predicate is independently covered by real-context leaf tests; no fabricated balls or flag/callback/timer writes.')
    (ROOT/'build/oracle/pirate-magna-capture-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(len(reports),'cases;',result['total_steps'],'steps;',result['status'])


if __name__=='__main__':main()
