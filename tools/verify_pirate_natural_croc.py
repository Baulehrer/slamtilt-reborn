#!/usr/bin/env python3
"""Verify an earned key-only Crocodile jackpot, finite game and reset."""
import argparse,json,os,subprocess
from pathlib import Path
from verify_pirate_modes import ROOT,read,sha,score
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity
CASE='natural-crocodile-game'

def contract(t):
    m={v['label']:v for v in t['milestones']}
    expected={'natural_lock_1':1317,'natural_lock_2':4517,'cannon_entered':5805,
        'crocodile_entered':6351,'two_free_balls':7090,'natural_jackpot_1':7623,
        'single_ball_compacted':9432,'normal_return':11112,'game_over':14240,
        'game_over_stable':14304,'new_game':14304,'second_game_running':15519}
    assert {k:m[k]['tick']for k in expected}==expected
    assert m['natural_lock_2']['locks']==2 and m['cannon_entered']['phase']==6
    assert m['crocodile_entered']['played_multiballs']==1 and m['crocodile_entered']['jackpot']==5000000
    assert m['two_free_balls']['phase']==4 and m['two_free_balls']['ball_states']==[2,2]
    jp=m['natural_jackpot_1'];assert len(t['natural_jackpots'])==1 and jp['collected_delta']==jp['collected']==5000000
    assert m['single_ball_compacted']['ball_count']==1 and m['normal_return']['phase']==2
    assert m['normal_return']['played_multiballs']==1
    end=m['game_over'];new=m['new_game'];assert end['phase']==0 and score(end)==15830000
    assert bytes.fromhex(end['highscore_hex'])[6:9]==b'ABC'
    assert new['phase']==1 and new['locks']==new['played_multiballs']==0 and score(new)==0
    assert end['highscore_hex']==new['highscore_hex']
    assert m['second_game_running']['phase']==2 and m['second_game_running']['ball_state']==2
    keys=[(v['tick'],v['action'],v['down'])for v in t['inputs']if 5400<=v['tick']<=6169]
    assert keys==[(5400,'left',False),(5574,'left',True),(5574,'right',True),(5582,'left',False),(5582,'right',False),(6168,'left',True),(6169,'left',False)]
    return dict(milestones=expected,jackpot=5000000,score=15830000,legal_keys=keys)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe');p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview');a=p.parse_args()
    game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT';dat=game/'DAT/PIRATE.DAT';prepared=ROOT/'build/oracle/pirate-full-tick';folder=ROOT/f'build/oracle/pirate-modes/{CASE}'
    path=folder/'trace.json';t=read(path);f=read(ROOT/f'analysis/traces/pirate-{CASE}.json');n=integrity(t,f,sha((game/'SLAMTILT.EXE').read_bytes()),sha(dat.read_bytes()))
    assert t['diagnostic_shots']==f['diagnostic_shots']==[] and t['key_only']and f['key_only']
    for k in ['natural_jackpots','source_policy','candidate_sha256','prefix_ticks','prefix_case']:assert t[k]==f[k]
    assert t['candidate_sha256']==sha((ROOT/'build/oracle/pirate-natural-croc/frozen-candidate.json').read_bytes())
    prefix=read(ROOT/'build/oracle/pirate-modes/legal-cave-game/trace.json')
    for key in KEYS:assert t[key][:5400+(key=='states')]==prefix[key][:5400+(key=='states')],key
    result=contract(t);native=folder/'native-verified.json';rendered=folder/'rendered-verified.json';capture=folder/'verified.bmp'
    subprocess.run([a.native,prepared,dat,native,str(n),'--full','--lamps','--full-state-trace','--replay',path],check=True)
    subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames',str(n//4),'--replay',path,'--full-state-trace','--trace-output',rendered,'--capture',capture],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
    for label,file in [('native/reset',native),('SDL',rendered)]:
        v=read(file);assert v['tick_count']==n and v.get('error','')==''
        for key in KEYS:
            assert v[key]==t[key],(label,key,next((i for i,(x,y)in enumerate(zip(v[key],t[key]))if x!=y),None))
    assert capture.read_bytes()[:2]==b'BM'
    result.update(status='VERIFIED original/native/reset/SDL key-only Crocodile game',tick_count=n,diagnostic_shots=[],scope='Frozen earned-input route; no checkpoints or gameplay injection during verification. Not a legal all-mode complete table claim.')
    (folder/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(n,'original/native/reset/SDL steps exact; earned Cave/cannon/two balls/5M JP/15.83M finite game/ABC/F1')
if __name__=='__main__':main()
