#!/usr/bin/env python3
"""Original/native/reset/SDL contracts for four Pirate Adventures."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
CASES=['sword','dive-success','dive-timeout','monkey-success','monkey-timeout','shark-success','shark-timeout']
def sha(data):return hashlib.sha256(data).hexdigest()
def jsha(value):return sha(json.dumps(value,separators=(',',':')).encode())
def read(path):return json.loads(path.read_text())
def score(row):return int(row['score_bcd'])


def contract(case,trace):
    marks={m['label']:m for m in trace['milestones']};mode=trace['mode']
    start=marks['started_and_released']
    assert start['phase']==5 and start['adventure']==mode and start['ball_state']==2
    assert start['played']==[int(i==mode)for i in range(6)]
    # Selection is earned by real bumper collisions, never a field assignment.
    assert [marks[f'bumper_select_{i+1}']['adventure']for i in range(mode)]==list(range(1,mode+1))
    if case=='sword':
        assert start['field_46e2a8']==5000000
        first=marks['initial_jackpot_settled'];repeat=marks['repeated_jackpot_settled']
        assert score(first)-score(start)==5250000
        assert score(repeat)-score(first)==5250000 # Same lit ramp pays again.
        bumper=marks['bumper_growth'];assert bumper['field_46e2a8']==5250000
        assert score(bumper)-score(repeat)==1240
        raised=marks['raised_jackpot_settled'];assert score(raised)-score(bumper)==5500000
        target=marks['target_growth'];assert target['field_46e2a8']==5500000
        top=marks['after_top_trap'];assert top['field_46e2a8']==6000000
        final_hit=marks['trap_raised_jackpot_settled']
        assert score(final_hit)-score(top)==6250000
        end=marks['timeout_return'];assert score(end)==score(final_hit)==41017480
    elif case=='dive-success':
        assert start['field_46e54c']==10 and start['field_46e54a']==0
        assert marks['bumper_descent_rate']['field_46e54c']==11
        assert [marks[f'dive_{i}_settled']['field_46e54a']for i in range(10)]==[11,22,33,44,55,66,77,88,99,100]
        bottom=marks['bottom_reached'];assert bottom['super_jackpot']==1 and bottom['timer']==3000
        duplicate=marks['duplicate_after_bottom_settled']
        assert duplicate['field_46e54a']==100 and score(duplicate)-score(bottom)==250000
        end=marks['super_jackpot_return']
        assert score(end)-score(duplicate)==30500000 and score(end)==84253720
    elif case=='monkey-success':
        assert start['field_46e544']==1
        wrong=marks['wrong_target_settled']
        assert wrong['field_46e544']==1 and score(wrong)-score(start)==250000
        previous=wrong
        for ident in [1,2,3,4,0]:
            row=marks[f'map_piece_{ident}_settled']
            assert row['field_46e544']==(ident+1)%5
            assert score(row)-score(previous)==(30250000 if ident==0 else 10250000)
            previous=row
        end=marks['map_complete_return'];assert end['field_4659a8']==5 and score(end)==72503720
    elif case=='shark-success':
        ramp=marks['ramp_speed_1_settled'];bumper=marks['bumper_speed'];target=marks['target_speed']
        assert ramp['field_46e55a']==150
        assert bumper['field_46e55a']==ramp['field_46e55a']-1+20
        assert target['field_46e55a']==bumper['field_46e55a']-1+25
        end=marks['shark_escape_return']
        assert 0x1b3a<=end['timer']<=0x1b40
        assert score(end)-score(marks['ramp_speed_3_settled'])==50000000
    else:
        end=marks['timeout_return']
        assert score(end)==score(start) and end['timer']==65535 and end['super_jackpot']==0
    assert end['phase']==2 and end['adventure']==mode+1 and end['ball_state']==2
    return end


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe')
    p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview')
    p.add_argument('--cases',nargs='+',choices=CASES,default=CASES)
    args=p.parse_args()
    prepared=ROOT/'build/oracle/pirate-full-tick'
    dat=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT'
    env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy');reports=[]
    keys=['states','timing','lifecycle','dmd_sha256','highscore_sha256','lamp_sha256','rule_sha256']
    for case in args.cases:
        folder=ROOT/'build/oracle/pirate-modes'/case;path=folder/'trace.json';t=read(path)
        f=read(ROOT/f'analysis/traces/pirate-{case}.json');count=f['tick_count']
        assert count==t['tick_count'] and count%4==0 and t['gameplay_stubs']==[]
        assert t['deterministic_original_replay'] and f['build_sha256']==t['build_sha256']
        assert f['dat_sha256']==t['dat_sha256']==sha(dat.read_bytes())
        for key in ['inputs','diagnostic_shots','milestones']:assert t[key]==f[key]
        assert sha(bytes(v for s in t['states']for v in s))==f['states_sha256']
        for key in ['timing','lifecycle']:assert jsha(t[key])==f[key+'_sha256']
        for key in keys[3:]:assert sha(''.join(t[key]).encode())==f[key.replace('_sha256','_sequence_sha256')]
        end=contract(case,t)
        native=folder/'native-verified.json';rendered=folder/'rendered-verified.json'
        subprocess.run([args.native,prepared,dat,native,str(count),'--full','--lamps','--replay',path,'--diagnostic-shots',path],check=True)
        screenshot=folder/'native-verified.bmp'
        subprocess.run([args.viewer,dat,'--pirate-play',prepared,'--frames',str(count//4),'--replay',path,
                        '--diagnostic-shots',path,'--trace-output',rendered,'--capture',screenshot],env=env,check=True)
        for label,result in [('native/reset',read(native)),('SDL',read(rendered))]:
            assert result['tick_count']==count and result.get('error','')==''
            for key in keys:
                assert len(t[key])==len(result[key]),(case,label,key,'length')
                for tick,(a,b)in enumerate(zip(t[key],result[key])):assert a==b,(case,label,key,tick)
        assert screenshot.read_bytes()[:2]==b'BM'
        reports.append(dict(case=case,ticks=count,status='VERIFIED',native_reset_sdl_exact=True,
            result=end,ball_bytes=100,rule_bytes=864,gameplay_stubs=[],
            scope='Directed diagnostic waypoints on actual original DAT triggers; not legal-key-only trajectories'))
        print(case,count,'original/native/reset/SDL exact',flush=True)
    (ROOT/'build/oracle/pirate-modes/verification.json').write_text(json.dumps(reports,indent=2)+'\n')
    print(len(reports),'Adventure contracts PASS')


if __name__=='__main__':main()
