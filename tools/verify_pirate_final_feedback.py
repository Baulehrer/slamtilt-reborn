#!/usr/bin/env python3
"""Four actual ordinary-table DMD events vs original/native/reset/SDL."""
import argparse,json,os,subprocess
from pathlib import Path
from verify_pirate_modes import ROOT,read,sha
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity

WANTED={'0x42c42c','0x42e41c','0x42c03c','0x42e5bc'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe')
    p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview')
    p.add_argument('--original-only',action='store_true');a=p.parse_args()
    cases=[]
    for side in ['a','b']:
        b=read(ROOT/f'analysis/pirate-final-feedback-{side}-boundary.json')
        assert b['gameplay_stubs']==[];cases+=b['cases']
    assert len(cases)==len(set(cases))
    game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    dat=game/'DAT/PIRATE.DAT';prepared=ROOT/'build/oracle/pirate-full-tick'
    bsha,dsha=sha((game/'SLAMTILT.EXE').read_bytes()),sha(dat.read_bytes())
    reports=[];observed=set()
    for case in cases:
        folder=ROOT/f'build/oracle/pirate-modes/{case}';path=folder/'trace.json'
        t=read(path);f=read(ROOT/f'analysis/traces/pirate-{case}.json')
        n=integrity(t,f,bsha,dsha);events=t['feedback_events'];assert events==f['feedback_events']
        for e in events:
            assert e['target']in WANTED
            assert e['event_tick']<e['first_dispatch_tick']<=e['last_dispatch_tick']<e['idle_after_tick']<=n
            assert e['dispatch_count']>0 and e['distinct_dmd_frames']>0
            assert e['last_dispatch_tick']-e['first_dispatch_tick']==4*(e['dispatch_count']-1)
            observed.add(e['target'])
        reports.append(dict(case=case,steps=n,events=events))
        if a.original_only:continue
        native=folder/'native-verified.json';rendered=folder/'rendered-verified.json'
        subprocess.run([a.native,prepared,dat,native,str(n),'--full','--lamps','--replay',path,'--diagnostic-shots',path],check=True)
        subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames',str(n//4),'--no-audio',
            '--replay',path,'--diagnostic-shots',path,'--trace-output',rendered],check=True,
            env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
        for label,out in [('native/reset',read(native)),('SDL',read(rendered))]:
            assert out['tick_count']==n and out.get('error','')==''
            for key in KEYS:assert out[key]==t[key],(case,label,key)
        print(case,n,'original/native/reset/SDL9vectors exact',flush=True)
    assert observed==WANTED,('unproved callbacks',WANTED-observed)
    result=dict(status='ORIGINAL VERIFIED'if a.original_only else'VERIFIED',build_sha256=bsha,
        dat_sha256=dsha,cases=reports,total_steps=sum(r['steps']for r in reports),targets=sorted(observed),
        scope='Actual event/priority admission; explicit diagnostic free-ball waypoints, no rule/score/timer/priority/callback writes; bounded registration inventory, not all possible indirect calls.')
    (ROOT/'build/oracle/pirate-final-feedback-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(len(cases),'cases;',result['total_steps'],'steps;',result['status'])

if __name__=='__main__':main()
