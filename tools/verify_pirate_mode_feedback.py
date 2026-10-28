#!/usr/bin/env python3
"""Six original Adventure DMD messages: physical events -> actual dispatch -> SDL."""
import argparse,json,os,subprocess
from pathlib import Path
from verify_pirate_modes import ROOT,read,sha,score
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity

CASES={'sword':['0x42f0cc','0x42f130'],'dive':['0x42f3e8','0x4300b4'],
       'monkey':['0x42f6ec']*4+['0x42f800']}


def contract(case,t,f):
    events=t['feedback_events'];assert events==f['feedback_events']
    assert [e['target']for e in events]==CASES[case]
    previous=0
    for e in events:
        assert previous<=e['event_tick']<e['first_dispatch_tick']<=e['last_dispatch_tick']<e['idle_after_tick']<=t['tick_count']
        assert e['dispatch_count']>1 and e['distinct_dmd_frames']>1
        assert e['last_dispatch_tick']-e['first_dispatch_tick']==4*(e['dispatch_count']-1)
        previous=e['idle_after_tick']
    marks={m['label']:m for m in t['milestones']};last=t['milestones'][-1]
    assert marks['started_and_released']['adventure']==t['mode']
    if case=='sword':
        assert last['phase']==5 and last['adventure']==1
        assert last['field_46e2a8']==5250000 and score(last)==6502480
    elif case=='dive':
        assert last['phase']==5 and last['adventure']==2
        assert last['field_46e54a']==last['field_46e54c']==11 and score(last)==6753720
    else:
        assert last['phase']==2 and last['adventure']==4 and last['field_4659a8']==5
        assert score(last)==72253720
    return dict(case=case,steps=t['tick_count'],feedback_events=events,score=score(last))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe')
    p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview')
    p.add_argument('--original-only',action='store_true');a=p.parse_args()
    prepared=ROOT/'build/oracle/pirate-full-tick';game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT';dat=game/'DAT/PIRATE.DAT'
    bsha,dsha=sha((game/'SLAMTILT.EXE').read_bytes()),sha(dat.read_bytes());reports=[]
    for case in CASES:
        name='feedback-'+case;folder=ROOT/'build/oracle/pirate-modes'/name;path=folder/'trace.json'
        t=read(path);f=read(ROOT/'analysis/traces'/('pirate-'+name+'.json'))
        n=integrity(t,f,bsha,dsha);reports.append(contract(case,t,f))
        if a.original_only:continue
        native=folder/'native-verified.json';rendered=folder/'rendered-verified.json'
        subprocess.run([a.native,prepared,dat,native,str(n),'--full','--lamps','--replay',path,'--diagnostic-shots',path],check=True)
        subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames',str(n//4),'--no-audio','--replay',path,
            '--diagnostic-shots',path,'--trace-output',rendered],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
        for label,out in [('native/reset',read(native)),('SDL',read(rendered))]:
            assert out['tick_count']==n and out.get('error','')==''
            for key in KEYS:assert out[key]==t[key],(case,label,key)
        reports[-1]['native_reset_sdl_exact']=True
        print(name,n,'original/native/reset/SDL9vectors exact',flush=True)
    result=dict(status='ORIGINAL VERIFIED'if a.original_only else'VERIFIED',build_sha256=bsha,dat_sha256=dsha,
        cases=reports,total_steps=sum(r['steps']for r in reports),
        scope='Physical diagnostic free-ball waypoints, real original DMD priority/dispatch; no rule/score/timer/priority/callback writes; not legal-key-only full-table gameplay.')
    (ROOT/'build/oracle/pirate-mode-feedback-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(len(reports),'cases;',result['total_steps'],'steps;',result['status'])

if __name__=='__main__':main()
