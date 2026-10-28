#!/usr/bin/env python3
"""Pinned original/native/reset/SDL Plank success, duplicate and timeout proof."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[1]


def sha(data):return hashlib.sha256(data).hexdigest()
def jsha(value):return sha(json.dumps(value,separators=(',',':')).encode())
def read(path):return json.loads(path.read_text())
def score(row):return int(row['score_bcd'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe')
    parser.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview')
    args=parser.parse_args()
    prepared=ROOT/'build/oracle/pirate-full-tick'
    dat=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT'
    environment=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
    reports=[]
    for outcome in ['success','timeout']:
        directory=ROOT/'build/oracle/pirate-adventure'/outcome
        replay=directory/'trace.json';original=read(replay)
        fixture=read(ROOT/f'analysis/traces/pirate-plank-{outcome}.json')
        assert original['deterministic_original_replay'] and original['gameplay_stubs']==[]
        assert fixture['build_sha256']==original['build_sha256']
        assert fixture['dat_sha256']==original['dat_sha256']==sha(dat.read_bytes())
        count=fixture['tick_count'];assert count==original['tick_count'] and count%4==0
        for key in ['inputs','diagnostic_shots','milestones']:assert fixture[key]==original[key]
        assert sha(bytes(v for s in original['states']for v in s))==fixture['states_sha256']
        for key in ['timing','lifecycle']:assert jsha(original[key])==fixture[f'{key}_sha256']
        sequences=['dmd_sha256','highscore_sha256','lamp_sha256','rule_sha256']
        for key in sequences:
            assert len(original[key])==count
            assert sha(''.join(original[key]).encode())==fixture[key.replace('_sha256','_sequence_sha256')]
        milestones={m['label']:m for m in original['milestones']}
        started=milestones['plank_started_and_released']
        assert started['phase']==5 and started['adventure']==0 and started['targets']==[1]*5
        if outcome=='success':
            first=milestones['rope_4'];duplicate=milestones['duplicate_rope_4']
            assert first['targets']==duplicate['targets'] and score(duplicate)-score(first)==250000
            ready=milestones['five_ropes_super_jackpot_lit'];result=milestones['super_jackpot_and_return']
            assert ready['targets']==[0]*5 and ready['super_jackpot']==1
            assert result['phase']==2 and result['adventure']==1 and result['ball_state']==2
            assert score(result)-score(ready)==30500000 #30M Super Jackpot + original500k trap award.
        else:
            result=milestones['plank_timeout_return']
            assert result['phase']==2 and result['timer']==65535
            assert result['targets']==[1]*5 and score(result)==score(started)
        native=directory/'native-verified.json';rendered=directory/'rendered-verified.json'
        subprocess.run([args.native,prepared,dat,native,str(count),'--full','--lamps',
                        '--replay',replay,'--diagnostic-shots',replay],check=True)
        screenshot=directory/'native-verified.bmp'
        subprocess.run([args.viewer,dat,'--pirate-play',prepared,'--frames',str(count//4),
                        '--replay',replay,'--diagnostic-shots',replay,'--trace-output',rendered,
                        '--capture',screenshot],env=environment,check=True)
        for name,path in [('native/reset',native),('SDL',rendered)]:
            actual=read(path);assert actual['tick_count']==count
            assert actual.get('error','')==''
            for key in ['states','timing','lifecycle',*sequences]:
                assert len(actual[key])==len(original[key]),(name,key,'count')
                for tick,(a,b)in enumerate(zip(actual[key],original[key])):
                    assert a==b,(outcome,name,key,tick)
        assert screenshot.read_bytes()[:2]==b'BM'
        reports.append(dict(outcome=outcome,steps=count,status='VERIFIED',
            native_reset_sdl_exact=True,gameplay_stubs=[],result=result,
            scope='Diagnostic free-ball waypoints; no human-input trajectory or all-Adventures proof'))
    # Directed shots must never overwrite a captured ball or the user's profile.
    with tempfile.TemporaryDirectory(prefix='slam-pirate-shot-guards-') as temporary:
        temporary=Path(temporary)
        source=read(ROOT/'build/oracle/pirate-adventure/success/trace.json')
        held=temporary/'held.json'
        held.write_text(json.dumps(dict(inputs=source['inputs'],diagnostic_shots=[
            *source['diagnostic_shots'][:2],dict(tick=650,layer=0,x=160,y=400)])))
        result=subprocess.run([args.native,prepared,dat,temporary/'rejected.json','700',
            '--full','--lamps','--replay',held,'--diagnostic-shots',held],capture_output=True,text=True)
        assert result.returncode!=0 and 'free canonical Pirate ball' in result.stderr
        profile=temporary/'private-profile.json';profile.write_bytes(b'profile must remain untouched')
        result=subprocess.run([args.viewer,dat,'--pirate-play',prepared,'--frames','1',
            '--diagnostic-shots',held,'--highscore-file',profile],env=environment,capture_output=True,text=True)
        assert result.returncode!=0 and 'no persistent highscore profile' in result.stderr
        assert profile.read_bytes()==b'profile must remain untouched'
    (ROOT/'build/oracle/pirate-adventure/verification.json').write_text(json.dumps(reports,indent=2)+'\n')
    print('Plank success/duplicate/30M Super Jackpot/return and timeout: original/native/reset/SDL exact')


if __name__=='__main__':main()
