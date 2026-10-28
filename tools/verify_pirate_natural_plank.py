#!/usr/bin/env python3
"""Check natural ramp/Plank/drain, finite game and independent reset/SDL."""
import argparse,json,os,subprocess
from pathlib import Path
from verify_pirate_modes import ROOT,read,sha,score
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity
CASE='natural-plank-game'

def contract(t):
    m={v['label']:v for v in t['milestones']}
    expected={'natural_adventure_armed':1750,'plank_entered':4104,'plank_free_ball':4932,
        'plank_return':6093,'initials_admitted':9776,'game_over':10240,
        'game_over_stable':10304,'new_game':10304,'second_game_running':11519}
    assert {k:m[k]['tick']for k in expected}==expected
    arm=m['natural_adventure_armed'];assert arm['phase']==2 and arm['arm']==65535
    assert arm['adventure']==4 # Original bumper selection later cycles to Plank.
    entry=m['plank_entered'];free=m['plank_free_ball'];drain=m['plank_return']
    assert entry['phase']==free['phase']==5 and entry['adventure']==free['adventure']==0
    assert entry['played']==[1,0,0,0,0,0] and entry['timer']==12828
    assert entry['ropes']==free['ropes']==[1]*5 and free['timer']==12000
    assert free['ball_state']==2 and drain['phase']==3 and drain['timer']==10839
    assert drain['ropes']==[1]*5 and t['natural_ropes']==[] # Drain, no rope/timeout claim.
    end=m['game_over'];new=m['new_game'];assert end['phase']==0 and score(end)==6084150
    assert bytes.fromhex(end['highscore_hex'])[6:9]==b'ABC'
    assert new['phase']==1 and new['played']==[0]*6 and new['locks']==0 and score(new)==0
    assert new['highscore_hex']==end['highscore_hex']
    assert m['second_game_running']['phase']==2 and m['second_game_running']['ball_state']==2
    return dict(milestones=expected,score=6084150,mode_exit='natural drain, timer still positive')

def rope_contract(t):
    m={v['label']:v for v in t['milestones']}
    two=t['case']in ['natural-plank-two-ropes','natural-plank-nudge']
    expected={'natural_adventure_armed':1750,'plank_entered':4104,'plank_free_ball':4932,
        'natural_rope_4':6763,'plank_return':7185,'initials_admitted':10976,
        'game_over':11440,'game_over_stable':11504,'new_game':11504,'second_game_running':12719}
    if two:expected.update(natural_rope_3=7298,plank_return=7859,initials_admitted=11580,
        game_over=12044,game_over_stable=12108,new_game=12108,second_game_running=13319)
    if t['case']=='natural-plank-nudge':expected['plank_return']=7852
    assert {k:m[k]['tick']for k in expected}==expected
    hit=m['natural_rope_4'];assert len(t['natural_ropes'])==(2 if two else 1) and hit['rope']==4
    assert hit['phase']==5 and hit['ropes']==[1,1,1,1,0] and score(hit)==14034150
    flags=[1,1,1,0,0]if two else[1,1,1,1,0]
    if two:
        hit=m['natural_rope_3'];assert hit['phase']==5 and hit['rope']==3 and hit['ropes']==flags and score(hit)==24284150
    for hit in t['natural_ropes']:
        tick=hit['tick'];before=int(bytes(t['lifecycle'][tick-2][8:14]).hex())
        after=int(bytes(t['lifecycle'][tick-1][8:14]).hex())
        assert after-before==10250000 #10Mrope award plus250kbase ramp award.
    assert m['natural_rope_4']['timer']==10569 #12000 minus1831steps plus400.
    assert m['plank_return']['phase']==3 and m['plank_return']['ropes']==flags
    final_score=28184150 if two else 17534150
    end=m['game_over'];new=m['new_game'];assert end['phase']==0 and score(end)==final_score
    assert bytes.fromhex(end['highscore_hex'])[6:9]==b'ABC'
    assert new['played']==[0]*6 and new['locks']==0 and score(new)==0
    assert new['highscore_hex']==end['highscore_hex']
    assert m['second_game_running']['phase']==2 and m['second_game_running']['ball_state']==2
    return dict(milestones=expected,score=final_score,natural_ropes=[4,3]if two else[4],mode_exit='natural drain; partial rope completion')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe');p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview');a=p.parse_args()
    run(a,CASE)
    for case in ['natural-plank-rope','natural-plank-two-ropes','natural-plank-nudge']:
        if (ROOT/f'analysis/traces/pirate-{case}.json').exists():run(a,case)

def run(a,case):
    game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT';dat=game/'DAT/PIRATE.DAT';prepared=ROOT/'build/oracle/pirate-full-tick';folder=ROOT/f'build/oracle/pirate-modes/{case}'
    path=folder/'trace.json';t=read(path);f=read(ROOT/f'analysis/traces/pirate-{case}.json');n=integrity(t,f,sha((game/'SLAMTILT.EXE').read_bytes()),sha(dat.read_bytes()))
    assert t['diagnostic_shots']==f['diagnostic_shots']==[] and t['key_only']and f['key_only']
    for k in ['natural_ropes','source_policy','candidate_sha256']:assert t[k]==f[k]
    source='pirate-natural-plank'if case==CASE else'pirate-plank-natural-rope'
    if case=='natural-plank-two-ropes':source='pirate-plank-natural-two-ropes'
    if case=='natural-plank-nudge':source='pirate-plank-nudge-recovery'
    assert t['candidate_sha256']==sha((ROOT/f'build/oracle/{source}/frozen-candidate.json').read_bytes())
    result=contract(t)if case==CASE else rope_contract(t)
    if case!=CASE:
        prefix=read(ROOT/f'build/oracle/pirate-modes/{CASE}/trace.json')
        for key in KEYS:assert t[key][:5600+(key=='states')]==prefix[key][:5600+(key=='states')],key
    native=folder/'native-verified.json';rendered=folder/'rendered-verified.json';capture=folder/'verified.bmp'
    subprocess.run([a.native,prepared,dat,native,str(n),'--full','--lamps','--full-state-trace','--replay',path],check=True)
    subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames',str(n//4),'--replay',path,'--full-state-trace','--trace-output',rendered,'--capture',capture],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
    for label,file in [('native/reset',native),('SDL',rendered)]:
        v=read(file);assert v['tick_count']==n and v.get('error','')==''
        for key in KEYS:assert v[key]==t[key],(label,key,next((i for i,(x,y)in enumerate(zip(v[key],t[key]))if x!=y),None))
        if 'nudge_window'in t:
            w=t['nudge_window'];assert w==f['nudge_window']
            start=w['start_tick']-1;assert v['nudge'][start:start+len(w['states'])]==w['states'],(label,'original18-field nudge window')
    assert capture.read_bytes()[:2]==b'BM'
    result.update(status='VERIFIED original/native/reset/SDL key-only Plank finite game',tick_count=n,diagnostic_shots=[],scope='Natural admission, release, retained rope hits, drain and finite game; no complete five-rope/super jackpot or natural timeout proof.')
    (folder/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(case,n,'original/native/reset/SDL steps exact;',result)
if __name__=='__main__':main()
