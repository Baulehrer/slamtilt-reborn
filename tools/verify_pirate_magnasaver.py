#!/usr/bin/env python3
"""Paired force/control, expiry/rearm and Tilt/next-ball original/native/SDL."""
import argparse,json,os,subprocess
from pathlib import Path
from verify_pirate_modes import ROOT,read,sha
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity

CASES=['force-off','force-on','retrigger','rearm','tilt-armed','tilt-active','save-return']


def contracts(case,t,f):
    n=t['tick_count'];values=t['magnasaver_state']
    assert values==f['magnasaver_state'] and len(values)==n
    assert all(len(v)==5 for v in values)
    assert t['force_observations']==f['force_observations']
    marks={m['label']:m for m in t['milestones']}
    def state(label):return marks[label]['magnasaver_state']
    if case=='force-off':
        assert t['force_observations']['count']==0
        assert values[1200][:3]==[65535,65535,0]
        # Control ball crosses the bottom before it is rescued by other rules.
        assert max(int.from_bytes(bytes(s[4:8]),'little',signed=True)for s in t['states'][1201:1402])>=600*65536
    elif case in ['force-on','save-return']:
        assert t['force_observations']['count']==804
        assert values[1200][:3]==[0,200,65535]
        y=int.from_bytes(bytes(t['states'][1400][4:8]),'little',signed=True)/65536
        assert y<417,('actual upward return',y)
        assert all(values[tick-1][2]==65535 for tick in range(1201,2004))
        assert state('original_expiry')[:3]==[0,65535,0]
        if case=='save-return':
            assert all(int.from_bytes(bytes(s[0x58:0x5a]),'little')==2 for s in t['states'][1201:2801])
            assert min(int.from_bytes(bytes(s[4:8]),'little',signed=True)for s in t['states'][2201:2801])<400*65536
            assert marks['flipper_returns_saved_ball_to_play']['phase']==2
            assert not any(s['tick']>1200 for s in t['diagnostic_shots'])
        else:assert state('following_ball')==[0,65535,0,0,0]
    elif case=='retrigger':
        assert 0<state('unearned_retrigger_did_not_extend')[1]<200
        assert marks['unextended_original_expiry']['tick']==2004
        assert state('unextended_original_expiry')[:3]==[0,65535,0]
    elif case=='rearm':
        assert state('reearned_while_active')[0]==65535
        assert state('reearned_while_active')[2]==65535
        assert state('rearm_reloaded_200')[:3]==[0,200,65535]
        start=marks['rearm_reloaded_200']['tick']
        assert marks['rearmed_original_expiry']['tick']==(start//4+201)*4
        assert state('rearmed_original_expiry')[:3]==[0,65535,0]
    else:
        start=marks['tilt_reached']['tick'];stop=marks['tilted_window_frozen']['tick']
        frozen=state('tilt_reached')
        assert frozen[4]!=0 and frozen[:3]==state('tilted_window_frozen')[:3]
        assert frozen[0]==(65535 if case=='tilt-armed' else 0)
        assert frozen[2]==(0 if case=='tilt-armed' else 65535)
        assert all(v[1]==frozen[1] and v[4]!=0 for v in values[start-1:stop])
        reset=next(i for i in range(stop,n)if values[i][4]==0)
        assert values[reset][:3]==[0,65535,0]
        assert t['lifecycle'][reset][0]==1,('actual next-ball reset',reset+1)
        assert state('next_ball_clears_tilt_and_magnasaver')==[0,65535,0,0,0]
        if case=='tilt-armed':assert t['force_observations']['count']==0
        else:assert t['force_observations']['last'][0]['tick']<=start
    return dict(case=case,steps=n,force=t['force_observations'],milestones=t['milestones'])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe')
    p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview')
    p.add_argument('--original-only',action='store_true');a=p.parse_args()
    game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    dat=game/'DAT/PIRATE.DAT';prepared=ROOT/'build/oracle/pirate-full-tick'
    bsha,dsha=sha((game/'SLAMTILT.EXE').read_bytes()),sha(dat.read_bytes())
    boundary=read(ROOT/'analysis/pirate-magnasaver-boundary.json')
    assert boundary['cases']==['magnasaver-'+c for c in CASES]and not boundary['gameplay_stubs']
    reports=[];traces={}
    for case in CASES:
        folder=ROOT/f'build/oracle/pirate-modes/magnasaver-{case}';path=folder/'trace.json'
        t=read(path);f=read(ROOT/f'analysis/traces/pirate-magnasaver-{case}.json')
        n=integrity(t,f,bsha,dsha);reports.append(contracts(case,t,f));traces[case]=t
        if a.original_only:continue
        native=folder/'native-verified.json';rendered=folder/'rendered-verified.json'
        subprocess.run([a.native,prepared,dat,native,str(n),'--full','--lamps','--replay',path,'--diagnostic-shots',path],check=True)
        subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames',str(n//4),'--no-audio',
            '--replay',path,'--diagnostic-shots',path,'--trace-output',rendered],check=True,
            env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
        for label,out in [('native/reset',read(native)),('SDL',read(rendered))]:
            assert out['tick_count']==n and out.get('error','')==''
            for key in KEYS+['magnasaver_state']:assert out[key]==t[key],(case,label,key)
        print(case,n,'original/native/reset/SDL10vectors exact',flush=True)
    off,on=traces['force-off'],traces['force-on']
    for key in KEYS:
        count=1200+(key=='states');assert off[key][:count]==on[key][:count],('paired prefix',key)
    assert [s for s in off['diagnostic_shots']if s['tick']<=1200]==[s for s in on['diagnostic_shots']if s['tick']<=1200]
    assert off['states'][1201]!=on['states'][1201]
    for key in KEYS+['magnasaver_state']:
        count=2004+(key=='states');assert traces['save-return'][key][:count]==on[key][:count],('frozen force-on prefix',key)
    result=dict(status='ORIGINAL VERIFIED'if a.original_only else'VERIFIED',cases=reports,
        total_steps=sum(r['steps']for r in reports),build_sha256=bsha,dat_sha256=dsha,
        scope='Free-ball diagnostic entry and actual keyboard events only; paired identical1200-step prefix/outlane state. Save-return preserves force-on prefix through2004 then LeftShift2200..2320 returns the ball aboveY400, free through2800, no post1200waypoint. Bounded save, not a legal-key-only all-table game. Original full reset and all10observed vectors; no force/rule/timer/Tilt injection.')
    (ROOT/'build/oracle/pirate-magnasaver-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(len(reports),'cases;',result['total_steps'],'steps;',result['status'])


if __name__=='__main__':main()
