#!/usr/bin/env python3
"""Five-lock caps/surplus jackpot campaign: original/native/reset/SDL."""
import argparse,json,os,subprocess
from pathlib import Path
from verify_pirate_modes import ROOT,read,sha,score
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity

CASE='multiball-surplus'
STAGES=[('crocodile',1,12500000),('storm',2,15000000),('battle',3,17500000),('mutiny',4,20000000)]

def contracts(trace):
    summaries=[];marks={r['label']:r for r in trace['milestones']}
    for name,ordinal,jp in STAGES:
        def mark(label):
            key=name+':'+label
            assert sum(r['label']==key for r in trace['milestones'])==1,(key,'unique milestone')
            return marks[key]
        prepare=mark('prepare');assert prepare['phase']==2 and prepare['played_multiballs']==ordinal-1 and prepare['locks']==0
        for n in range(1,6):
            row=mark(f'lock_{n}_released');assert row['locks']==n and row['ball_count']==1 and row['ball_state']==2
        cap=mark('cap_guard');assert cap['locks']==5 and cap['ball_count']==1
        entered=mark('mode_entered');released=mark('all_balls_released');returned=mark('normal_return')
        assert entered['phase']==4 and entered['locks']==0 and entered['played_multiballs']==ordinal
        assert entered['jackpot']==released['jackpot']==jp
        assert released['ball_count']==5 and released['ball_states']==[2]*5
        assert mark('after_growth')['jackpot']==mark('before_growth')['jackpot']+1000000==jp+1000000
        assert returned['phase']==2 and returned['ball_states']==[2]and returned['ball_count']==1 and returned['locks']==0
        begin=mark('cannon_ready_intro')['tick'];end=mark('cannon_result')['tick']
        assert not any(begin<=e['tick']<end for e in trace['diagnostic_shots']),'Cannon must use original keys/physics'
        copies=[c for c in trace['compactions']if c['stage']==name]
        assert [(c['old_count'],c['new_count'])for c in copies]==[(5,4),(4,3),(3,2),(2,1)],(name,'compaction')
        assert all(c['index']==0 and c['source_sha256']==c['destination_sha256']for c in copies)
        summaries.append(dict(mode=name,initial_jackpot=jp,grown_jackpot=jp+1000000,balls=5,
            entered_tick=entered['tick'],returned_tick=returned['tick'],compactions=len(copies)))
    before=marks['battle:before_unarmed_top_trap'];after=marks['battle:after_unarmed_top_trap']
    assert before['super_jackpot']==after['super_jackpot']==0
    assert before['jackpot']==after['jackpot']
    assert before['collected']==after['collected'] and score(after)-score(before)==500000
    return summaries

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe')
    p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview');a=p.parse_args()
    folder=ROOT/'build/oracle/pirate-modes'/CASE;path=folder/'trace.json';t=read(path)
    f=read(ROOT/f'analysis/traces/pirate-{CASE}.json')
    game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    dat=game/'DAT/PIRATE.DAT';prepared=ROOT/'build/oracle/pirate-full-tick'
    count=integrity(t,f,sha((game/'SLAMTILT.EXE').read_bytes()),sha(dat.read_bytes()))
    for key in ['scope','compactions','super_jackpot_writes']:assert t[key]==f[key]
    stages=contracts(t)
    native=folder/'native-verified.json';rendered=folder/'rendered-verified.json';screenshot=folder/'verified.bmp'
    subprocess.run([a.native,prepared,dat,native,str(count),'--full','--lamps','--replay',path,'--diagnostic-shots',path],check=True)
    subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames',str(count//4),'--replay',path,
        '--diagnostic-shots',path,'--trace-output',rendered,'--capture',screenshot],check=True,
        env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
    for label,out in [('native/reset',native),('SDL',rendered)]:
        value=read(out);assert value['tick_count']==count and value.get('error','')==''
        for key in KEYS:
            assert len(value[key])==len(t[key]),(label,key)
            for tick,(x,y)in enumerate(zip(value[key],t[key])):assert x==y,(label,key,tick)
    assert screenshot.read_bytes()[:2]==b'BM'
    report=dict(status='VERIFIED bounded diagnostic original/native/reset/SDL campaign',tick_count=count,
        stages=stages,compactions=16,super_jackpot_writes=t['super_jackpot_writes'],
        battle_triple_jackpot='Admission remains UNKNOWN; no flag injection, observed unarmed gate only.',
        scope=t['scope'])
    (folder/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(count,'original/native/reset/SDL surplus steps exact; four five-ball modes,16 compactions')
if __name__=='__main__':main()
