#!/usr/bin/env python3
"""Complete the ten retained Pirate multiball lock/ball-count contracts."""
import argparse,json,os,subprocess
from pathlib import Path
from verify_pirate_modes import ROOT,read,sha,score
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity
CASES=[('locks-crocodile-3',1,3,7500000),('locks-crocodile-4',1,4,10000000),('locks-storm-4',2,4,12500000)]

def contract(t,case,ordinal,locks,jp):
    marks={m['label'].split(':')[-1]:m for m in t['milestones']if m['label'].startswith(case+':')}
    assert t['ordinal']==ordinal and t['lock_count']==locks and t['initial_jackpot']==jp
    for i in range(1,locks+1):
        m=marks[f'lock_{i}_released'];assert m['locks']==i and m['played_multiballs']==ordinal-1 and m['ball_count']==1 and m['ball_state']==2
    before=marks['prepare'];assert before['phase']==2 and before['played_multiballs']==ordinal-1 and before['locks']==0
    entered=marks['mode_entered'];released=marks['all_balls_released'];end=marks['normal_return']
    assert entered['phase']==4 and entered['played_multiballs']==ordinal and entered['locks']==0
    assert entered['jackpot']==released['jackpot']==jp
    assert released['ball_count']==locks and released['ball_states']==[2]*locks
    # At least the current JP is awarded; incidental original base points may
    # occur while captured balls are released. Never subtract a guessed value.
    for b,a,value in [('before_jackpot','after_jackpot',jp),('before_raised','after_raised',jp+1000000)]:
        assert marks[a]['collected']-marks[b]['collected']==value
        assert score(marks[a])-score(marks[b])>=value
    assert marks['after_growth']['jackpot']==marks['before_growth']['jackpot']+1000000==jp+1000000
    assert end['phase']==2 and end['ball_count']==1 and end['ball_states']==[2]and end['locks']==0
    assert [(c['old_count'],c['new_count'])for c in t['compactions']]==[(n,n-1)for n in range(locks,1,-1)]
    assert all(c['index']==0 and c['source_sha256']==c['destination_sha256']for c in t['compactions'])
    start=marks['cannon_ready_intro']['tick'];stop=marks['cannon_result']['tick']
    assert not any(start<=s['tick']<stop for s in t['diagnostic_shots'])
    return dict(case=case,ordinal=ordinal,locks=locks,balls=locks,initial_jackpot=jp,grown_jackpot=jp+1000000,steps=t['tick_count'],compactions=locks-1)

def coverage(buildsha,datsha,new):
    rows={(r['ordinal'],r['locks']):r for r in new}
    for case,names in [('crocodile',[(1,2,'crocodile_balls_released')]),('multiball-campaign',[(2,3,'storm:all_balls_released'),(3,4,'battle:all_balls_released'),(4,5,'mutiny:all_balls_released')]),('multiball-surplus',[(i,5,name+':all_balls_released')for i,name in enumerate(['crocodile','storm','battle','mutiny'],1)])]:
        t=read(ROOT/f'build/oracle/pirate-modes/{case}/trace.json');f=read(ROOT/f'analysis/traces/pirate-{case}.json');integrity(t,f,buildsha,datsha)
        for ordinal,locks,label in names:
            m=next(m for m in t['milestones']if m['label']==label)
            assert m['phase']==4 and m['ball_count']==locks and m['played_multiballs']==ordinal
            expected={1:5000000+(locks-2)*2500000,2:10000000+(locks-3)*2500000,3:15000000+(locks-4)*2500000,4:20000000}[ordinal]
            assert m['jackpot']==expected
            rows.setdefault((ordinal,locks),dict(case=case,ordinal=ordinal,locks=locks,balls=locks,initial_jackpot=expected,source='retained original/native/reset/SDL fixture'))
    assert set(rows)=={(ordinal,n)for ordinal in range(1,5)for n in range(ordinal+1,6)}
    return [rows[k]for k in sorted(rows)]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe');p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview');a=p.parse_args()
    game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT';dat=game/'DAT/PIRATE.DAT';prepared=ROOT/'build/oracle/pirate-full-tick'
    bsha=sha((game/'SLAMTILT.EXE').read_bytes());dsha=sha(dat.read_bytes());reports=[]
    for case,ordinal,locks,jp in CASES:
        folder=ROOT/f'build/oracle/pirate-modes/{case}';path=folder/'trace.json';t=read(path);f=read(ROOT/f'analysis/traces/pirate-{case}.json')
        n=integrity(t,f,bsha,dsha)
        for k in ['prefix_case','prefix_ticks','ordinal','lock_count','initial_jackpot','compactions']:assert t[k]==f[k]
        if t['prefix_case']:
            prefix=read(ROOT/f"build/oracle/pirate-modes/{t['prefix_case']}/trace.json");assert prefix['tick_count']==t['prefix_ticks']
            for key in KEYS:assert t[key][:t['prefix_ticks']+(key=='states')]==prefix[key]
        reports.append(contract(t,case,ordinal,locks,jp))
        native=folder/'native-verified.json';rendered=folder/'rendered-verified.json';capture=folder/'verified.bmp'
        subprocess.run([a.native,prepared,dat,native,str(n),'--full','--lamps','--replay',path,'--diagnostic-shots',path],check=True)
        subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames',str(n//4),'--replay',path,'--diagnostic-shots',path,'--trace-output',rendered,'--capture',capture],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
        for label,file in [('native/reset',native),('SDL',rendered)]:
            v=read(file);assert v['tick_count']==n and v.get('error','')==''
            for key in KEYS:assert v[key]==t[key],(case,label,key)
        assert capture.read_bytes()[:2]==b'BM'
    matrix=coverage(bsha,dsha,reports)
    out=dict(status='VERIFIED bounded original/native/reset/SDL lock-count matrix',new_cases=reports,total_new_steps=sum(r['steps']for r in reports),matrix=matrix,
        scope='All10 lock-count/ordinal combinations using new and SHA-pinned retained fixtures; diagnostic free-ball entry/parking. No legal-key-only complete table claim.')
    (ROOT/'build/oracle/pirate-lock-matrix-verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print('3new fixtures /',out['total_new_steps'],'original/native/reset/SDL steps exact; all10 lock/ball-count combinations covered')
if __name__=='__main__':main()
