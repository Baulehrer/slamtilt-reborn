#!/usr/bin/env python3
"""Original/native/reset/SDL Knife Throwing outcome and input contracts."""
import argparse
import os
from pathlib import Path
import subprocess
import json
from verify_pirate_modes import ROOT, read, sha, jsha, score

CASES=['knife-success','knife-failure']
KEYS=['states','timing','lifecycle','dmd_sha256','highscore_sha256','lamp_sha256','rule_sha256','video_sha256']


def contract(case,t):
    marks={m['label']:m for m in t['milestones']}
    start=marks['video_initialized'];active=marks['video_active'];end=marks['video_result']
    assert start['phase']==5 and start['ball_state']==3 and start['video']==1
    assert start['adventure']==5 and start['played']==[0,0,0,0,0,1]
    assert start['player_x']==48 and start['remaining']==24 and start['award_flag']==0
    assert active['intro']==364 and active['video']==1
    assert [marks[f'bumper_select_{i+1}']['adventure']for i in range(5)]==list(range(1,6))
    assert end['video']==0 and end['phase']==5 and end['ball_state']==3
    if case=='knife-success':
        kills=[m for m in t['milestones']if m['label'].startswith('kill_')]
        assert len(kills)==25
        assert [k['remaining']for k in kills]==list(range(23,-1,-1))+[0xffffffff]
        assert [k['kill_score']for k in kills]==[3000000*i for i in range(1,26)]
        assert [k['spawn_period']for k in kills]==[100-3*i for i in range(1,26)]
        assert end['award_flag']==1 and end['kill_score']==75000000
        assert score(end)-score(active)==75000000
        actions=[e for e in t['inputs']if e['tick']>=active['tick']]
        assert all(any(e['action']==action and e['down']for e in actions)for action in ['left','right','enter'])
        assert min(k['player_x']for k in kills)<48<max(k['player_x']for k in kills)
        guard=marks['upper_trap_does_not_collect'];collected=marks['extra_ball_collected']
        assert guard['award_flag']==1 and guard['extra_credits']==0
        assert collected['award_flag']==0 and collected['extra_credits']==1
        assert collected['phase']==2 and collected['ball_state']==2
    else:
        assert end['award_flag']==0 and end['remaining']==24 and end['kill_score']==0
        assert score(end)==score(active)
        assert all(e['tick']<active['tick']for e in t['inputs'])
    returned=marks['normal_play_return']
    assert returned['phase']==2 and returned['ball_state']==2 and returned['video']==0 and returned['adventure']==0
    # No diagnostic coordinate change while the video simulation is active.
    assert not any(start['tick']<=s['tick']<returned['tick']for s in t['diagnostic_shots'])
    return returned


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe')
    p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview')
    p.add_argument('--cases',nargs='+',choices=CASES,default=CASES)
    a=p.parse_args();reports=[]
    prepared=ROOT/'build/oracle/pirate-full-tick'
    dat=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT'
    env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
    for case in a.cases:
        folder=ROOT/'build/oracle/pirate-modes'/case;path=folder/'trace.json';t=read(path)
        f=read(ROOT/f'analysis/traces/pirate-{case}.json');count=f['tick_count']
        assert count==t['tick_count'] and count%4==0 and t['gameplay_stubs']==[]
        assert t['deterministic_original_replay'] and f['build_sha256']==t['build_sha256']
        assert f['dat_sha256']==t['dat_sha256']==sha(dat.read_bytes())
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
            result=end,ball_bytes=100,rule_bytes=864,video_bytes=892,gameplay_stubs=[],
            scope='Diagnostic table entry; exclusively legal original keys during video mode'))
        print(case,count,'original/native/reset/SDL exact',flush=True)
    (ROOT/'build/oracle/pirate-modes/knife-verification.json').write_text(json.dumps(reports,indent=2)+'\n')
    print('Knife Throwing contracts PASS',flush=True)


if __name__=='__main__':main()
