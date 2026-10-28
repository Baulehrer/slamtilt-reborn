#!/usr/bin/env python3
"""Original/native/reset/SDL Mermaid collections, Hold Bonus and Tilt."""
import argparse,json,os,subprocess
from pathlib import Path
from verify_pirate_modes import ROOT,read,sha,jsha
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity
from pirate_mermaid_contracts import contracts, BANKS
CASES=['mermaid-'+c for c in BANKS]
def main():
    p=argparse.ArgumentParser();p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview');a=p.parse_args()
    prepared=ROOT/'build/oracle/pirate-full-tick';game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT';dat=game/'DAT/PIRATE.DAT';rows=[]
    profiles=a.viewer.resolve().parent.parent/'share/slamtilt/table-profiles.json'
    if not profiles.exists():profiles=ROOT/'analysis/table-profiles.json'
    tag=sha(a.viewer.read_bytes())[:12]
    for case in CASES:
        path=ROOT/f'build/oracle/pirate-modes/{case}/trace.json';t=read(path);f=read(ROOT/f'analysis/traces/pirate-{case}.json')
        n=integrity(t,f,sha((game/'SLAMTILT.EXE').read_bytes()),sha(dat.read_bytes()));assert jsha(t['magnasaver_state'])==f['magnasaver_state_sha256']
        summary=contracts(t)
        native=path.parent/f'native-{tag}-verified.json';rendered=path.parent/f'rendered-{tag}-verified.json'
        subprocess.run([ROOT/'build/native/pirate_session_probe',prepared,dat,native,str(n),'--full','--lamps','--replay',path,'--diagnostic-shots',path],check=True)
        subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames',str(n//4),'--no-audio','--replay',path,'--diagnostic-shots',path,'--trace-output',rendered],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SLAM_TABLE_PROFILES=str(profiles)))
        for label,out in [('native/reset',read(native)),('SDL',read(rendered))]:
            assert out['tick_count']==n and not out.get('error','')
            for key in KEYS+['magnasaver_state']:assert out[key]==t[key],(case,label,key)
        rows.append(dict(case=case,steps=n,contract=summary));print(case,n,'10vectors exact',flush=True)
    (ROOT/'analysis/traces/pirate-mermaid-acceptance.json').write_text(json.dumps(dict(status='VERIFIED',cases=rows,scope='Actual MagnaTable rewards, Mermaid captures, physical drains, earned Hold Bonus/multiplier and keyboard Tilt/F1. No gameplay-field writes; diagnostic trajectories, not legal-key-only fullgame.'),indent=2)+'\n')
if __name__=='__main__':main()
