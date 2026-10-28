#!/usr/bin/env python3
"""Legal-key-only Pirate Cave game and naturally reached callbacks."""
import argparse,json,os,subprocess
from pathlib import Path
from verify_pirate_modes import ROOT,read,sha,jsha
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity

def cave_contract(t):
    marks={m['label']:m for m in t['milestones']}
    for n,tick in [(1,1317),(2,4517),(3,7717)]:
        m=marks['natural_lock_'+str(n)];assert m['tick']==tick and m['locks']==n and m['ball_state']==3
        assert t['lifecycle'][tick-1][4]==n
    end=marks['game_over'];stable=marks['game_over_stable'];new=marks['new_game'];second=marks['second_game_running']
    assert end['tick']==10080 and end['phase']==0 and end['score_bcd']=='000005145000'
    assert stable['tick']-end['tick']==64 and stable['phase']==0
    records=bytes.fromhex(end['highscore_hex']);assert records[6:9]==b'ABC'
    assert records==bytes.fromhex(new['highscore_hex']) and new['locks']==0 and new['phase']==1
    assert second['phase']==2 and second['ball_state']==2
    return dict(case=t['case'],steps=t['tick_count'],natural_locks=[1317,4517,7717],score=5145000,game_over=10080,new_game=new['tick'],free_ball=second['tick'])

def feedback_contract(t,f):
    records=t['target_entries'];assert jsha(records)==f['target_entries_sha256']
    assert t['target_entry_counts']==f['target_entry_counts']and t['source_policy']==f['source_policy']
    target=t['missing_target'];entries=[v for v in records if v['target']==target]
    assert entries and entries[0]['tick']==t['source_policy']['steps']
    assert all(v['target']==target for v in entries)
    assert t['draw_service_entries']==f['draw_service_entries']
    # Six draw callbacks and the original service+54 routine; retain field names.
    expected='0x43522f'if target=='0x406650'else'0x407c09'
    assert all(v['callsite']==expected for v in entries)
    return dict(case=t['case'],steps=t['tick_count'],target=target,entry_count=len(entries),first_tick=entries[0]['tick'],last_tick=entries[-1]['tick'])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe');p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview');a=p.parse_args()
    game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT';dat=game/'DAT/PIRATE.DAT';prepared=ROOT/'build/oracle/pirate-full-tick'
    bsha=sha((game/'SLAMTILT.EXE').read_bytes());dsha=sha(dat.read_bytes());reports=[]
    cases=['legal-cave-game',*read(ROOT/'analysis/pirate-legal-feedback-boundary.json')['cases']];assert len(cases)==11
    extra=ROOT/'analysis/pirate-natural-feedback-boundary.json'
    if extra.exists():cases+=read(extra)['cases']
    assert len(cases)==len(set(cases))
    for case in cases:
        folder=ROOT/f'build/oracle/pirate-modes/{case}';path=folder/'trace.json';t=read(path);f=read(ROOT/f'analysis/traces/pirate-{case}.json')
        n=integrity(t,f,bsha,dsha);assert t['diagnostic_shots']==f['diagnostic_shots']==[]
        assert all(e['action']in ['enter','left','right','key','new_game']for e in t['inputs'])
        reports.append(cave_contract(t)if case=='legal-cave-game'else feedback_contract(t,f))
        native=folder/'native-verified.json';rendered=folder/'rendered-verified.json';capture=folder/'verified.bmp'
        subprocess.run([a.native,prepared,dat,native,str(n),'--full','--lamps','--full-state-trace','--replay',path],check=True)
        subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames',str(n//4),'--replay',path,'--full-state-trace','--trace-output',rendered,'--capture',capture],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
        for label,file in [('native/reset',native),('SDL',rendered)]:
            v=read(file);assert v['tick_count']==n and v.get('error','')==''
            for key in KEYS:
                assert v[key]==t[key],(case,label,key,next((i for i,(x,y)in enumerate(zip(v[key],t[key]))if x!=y),None))
        assert capture.read_bytes()[:2]==b'BM'
    out=dict(status='VERIFIED original/native/reset/SDL legal inputs without waypoints',cases=reports,total_steps=sum(r['steps']for r in reports),
        limitations=['Bounded frozen input schedules; no complete all-mode key-only trajectory or original raster equivalence claimed.'])
    (ROOT/'build/oracle/pirate-legal-play-verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(len(cases),'legal-key fixtures /',out['total_steps'],'original/native/reset/SDL steps exact; three earned locks, finite game and missing-call continuations closed')
if __name__=='__main__':main()
