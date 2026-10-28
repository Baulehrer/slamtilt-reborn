#!/usr/bin/env python3
"""Original/native/reset/SDL Pirate Cave, cannon and Crocodile contracts."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
from verify_pirate_modes import ROOT, read, sha, jsha

CASES=['crocodile','cannon-miss']
KEYS=['states','timing','lifecycle','dmd_sha256','highscore_sha256','lamp_sha256',
      'rule_sha256','video_sha256','ball_pool_sha256']


def contract(case,t):
    marks={m['label']:m for m in t['milestones']}
    for index in (1,2):
        released=marks[f'initial_lock_{index}_released']
        assert released['locks']==index and released['ball_count']==1
        assert released['played_multiballs']==0 and released['ball_state']==2
    assert marks['cannon_ready_intro']['phase']==6
    assert marks['early_fire_ignored']['phase']==6
    assert marks['cannon_fired']['phase']==2
    result=marks['cannon_result']
    assert not any(marks['cannon_ready_intro']['tick']<=s['tick']<result['tick']
                   for s in t['diagnostic_shots']), 'No diagnostic placement during cannon aiming/flight'
    if case=='cannon-miss':
        assert result['phase']==2 and result['played_multiballs']==0
        assert result['locks']==1 and result['ball_count']==1
        assert result['jackpot']==0 and result['collected']==0
        end=marks['miss_normal_return']
        assert end['phase']==2 and end['ball_state']==2 and end['ball_count']==1
    else:
        assert result['phase']==4 and result['played_multiballs']==1 and result['locks']==0
        assert result['jackpot']==5000000
        released=marks['crocodile_balls_released']
        assert released['phase']==4 and released['ball_count']==2 and released['ball_states']==[2,2]
        wrong=marks['wrong_jackpot_guard'];first=marks['first_jackpot_awarded']
        grown=marks['jackpot_grown'];raised=marks['raised_jackpot_awarded']
        assert wrong['collected']==released['collected']
        assert first['collected']-wrong['collected']==5000000
        assert first['jackpot']==5000000
        assert grown['jackpot']==6000000 and grown['locks']==0
        assert grown['collected']==first['collected']
        assert raised['collected']-grown['collected']==6000000
        assert raised['jackpot']==6000000
        end=marks['crocodile_normal_return']
        assert end['phase']==2 and end['ball_count']==1 and end['ball_states']==[2]
    return end


def rejected_ball_indices(native,prepared,dat,source):
    # Freeze the same legal input/diagnostic prefix; the only change is the
    # selected ball in a new waypoint before any multiball release.
    with tempfile.TemporaryDirectory(prefix='slam-pirate-ball-guards-') as temporary:
        temporary=Path(temporary)
        for index,message in [(8,'Invalid diagnostic ball index'),(1,'free canonical Pirate ball')]:
            path=temporary/f'ball-{index}.json'
            path.write_text(json.dumps(dict(inputs=[e for e in source['inputs']if e['tick']<600],
                diagnostic_shots=[*[s for s in source['diagnostic_shots']if s['tick']<600],
                    dict(tick=600,layer=0,x=160,y=400,ball=index)])))
            result=subprocess.run([native,prepared,dat,temporary/f'rejected-{index}.json','601',
                '--full','--lamps','--replay',path,'--diagnostic-shots',path],capture_output=True,text=True)
            assert result.returncode!=0 and message in result.stderr,(index,result.returncode,result.stderr)
    return ['out_of_range_ball_8','inactive_ball_1']


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe')
    p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview')
    p.add_argument('--cases',nargs='+',choices=CASES,default=CASES)
    a=p.parse_args();reports=[]
    prepared=ROOT/'build/oracle/pirate-full-tick'
    game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    dat=game/'DAT/PIRATE.DAT';build_sha=sha((game/'SLAMTILT.EXE').read_bytes())
    dat_sha=sha(dat.read_bytes());env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
    for case in a.cases:
        folder=ROOT/'build/oracle/pirate-modes'/case;path=folder/'trace.json';t=read(path)
        f=read(ROOT/f'analysis/traces/pirate-{case}.json');count=f['tick_count']
        assert count==t['tick_count'] and count%4==0 and t['gameplay_stubs']==[]
        assert t['deterministic_original_replay'] and f['build_sha256']==t['build_sha256']==build_sha
        assert f['dat_sha256']==t['dat_sha256']==dat_sha
        for k in ['inputs','diagnostic_shots','milestones']:assert f[k]==t[k]
        assert sha(bytes(v for s in t['states']for v in s))==f['states_sha256']
        for k in ['timing','lifecycle']:assert jsha(t[k])==f[k+'_sha256']
        for k in KEYS[3:]:assert sha(''.join(t[k]).encode())==f[k.replace('_sha256','_sequence_sha256')]
        end=contract(case,t)
        native=folder/'native-verified.json';rendered=folder/'rendered-verified.json'
        subprocess.run([a.native,prepared,dat,native,str(count),'--full','--lamps','--replay',path,'--diagnostic-shots',path],check=True)
        screenshot=folder/'native-verified.bmp'
        subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames',str(count//4),'--replay',path,
            '--diagnostic-shots',path,'--trace-output',rendered,'--capture',screenshot],env=env,check=True)
        for label,result in [('native/reset',read(native)),('SDL',read(rendered))]:
            assert result['tick_count']==count and result.get('error','')==''
            for k in KEYS:
                assert len(t[k])==len(result[k]),(case,label,k,'length')
                for tick,(x,y)in enumerate(zip(t[k],result[k])):assert x==y,(case,label,k,tick)
        assert screenshot.read_bytes()[:2]==b'BM'
        reports.append(dict(case=case,ticks=count,status='VERIFIED',native_reset_sdl_exact=True,
            result=end,ball_bytes=100,ball_pool_bytes=800,rule_bytes=864,video_bytes=892,gameplay_stubs=[],
            scope='Diagnostic free-ball table waypoints; original cannon inputs; no rule/score/timer injection'))
        print(case,count,'original/native/reset/SDL exact, eight-ball pool',flush=True)
    guards=rejected_ball_indices(a.native,prepared,dat,t)
    (ROOT/'build/oracle/pirate-modes/multiball-verification.json').write_text(json.dumps(
        dict(cases=reports,guards=guards),indent=2)+'\n')
    print('Cave/cannon/Crocodile multiball and ball-index guards PASS',flush=True)


if __name__=='__main__':main()
