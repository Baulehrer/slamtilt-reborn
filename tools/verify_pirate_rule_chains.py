#!/usr/bin/env python3
"""Original/native/reset/SDL rule chains and formerly uncompiled Plank feedback."""
import argparse,json,os,subprocess
from pathlib import Path
from verify_pirate_modes import ROOT,read,sha,jsha
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity
from pirate_piranha_contracts import contracts as piranha_contracts
from pirate_multiplier_ladder_contracts import contracts as multiplier_contracts
from pirate_multiplier_payout_contracts import contracts as payout_contracts
CASES=['plank-super-feedback','piranha-chain','bonus-multiplier-ladder','bonus-multiplier-payout']

def plank_contracts(t):
    marks={v['label']:v for v in t['milestones']};a=marks['five_ropes_super_lit'];b=marks['returned']
    assert a['targets']==[0]*5 and a['super_jackpot']==1 and a['phase']==5
    assert b['phase']==2 and b['adventure']==1 and int(b['score_bcd'])-int(a['score_bcd'])==30500000
    e=t['feedback_events'];assert len(e)==1 and e[0]['target']=='0x42eb6c'
    assert e[0]['first_dispatch_tick']==4100 and e[0]['dispatch_count']==271 and e[0]['distinct_dmd_frames']==51
    return dict(score_award=30000000,ordinary_trap_score=500000,callback='0x42eb6c',dispatches=271,distinct_dmd_frames=51)

def main():
    p=argparse.ArgumentParser();p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe');p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview');p.add_argument('--cases',nargs='+',default=CASES);a=p.parse_args()
    profiles=a.viewer.resolve().parent.parent/'share/slamtilt/table-profiles.json'
    if not profiles.exists():profiles=ROOT/'analysis/table-profiles.json'
    game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT';dat=game/'DAT/PIRATE.DAT';prepared=ROOT/'build/oracle/pirate-full-tick';rows=[]
    for case in a.cases:
        path=ROOT/f'build/oracle/pirate-modes/{case}/trace.json';t=read(path);f=read(ROOT/f'analysis/traces/pirate-{case}.json')
        n=integrity(t,f,sha((game/'SLAMTILT.EXE').read_bytes()),sha(dat.read_bytes()));assert jsha(t['magnasaver_state'])==f['magnasaver_state_sha256']
        summary={'plank-super-feedback':plank_contracts,'piranha-chain':piranha_contracts,'bonus-multiplier-ladder':multiplier_contracts,'bonus-multiplier-payout':payout_contracts}[case](t)
        native=path.parent/'native-verified.json';rendered=path.parent/'rendered-verified.json'
        subprocess.run([a.native,prepared,dat,native,str(n),'--full','--lamps','--replay',path,'--diagnostic-shots',path],check=True)
        subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames',str(n//4),'--no-audio','--replay',path,'--diagnostic-shots',path,'--trace-output',rendered],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SLAM_TABLE_PROFILES=str(profiles)))
        for label,out in [('native/reset',read(native)),('SDL',read(rendered))]:
            assert out['tick_count']==n and not out.get('error','')
            for key in KEYS+['magnasaver_state']:assert out[key]==t[key],(case,label,key)
        rows.append(dict(case=case,steps=n,contract=summary));print(case,n,'original/native/reset/SDL10vectors exact',flush=True)
    (ROOT/'analysis/traces/pirate-rule-chain-acceptance.json').write_text(json.dumps(dict(status='VERIFIED',cases=rows,scope='ActualDAT diagnostic waypoints,original/reset proof andnative/reset/SDL10vectors; not legalkey-only all-feature game or wholeoriginal raster.'),indent=2)+'\n')
if __name__=='__main__':main()
