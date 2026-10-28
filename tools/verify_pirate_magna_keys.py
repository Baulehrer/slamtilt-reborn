#!/usr/bin/env python3
"""Original/native/reset/SDL exact key-only Magna reward after frozen entry."""
import argparse,json,os,subprocess
from pathlib import Path
from verify_pirate_modes import ROOT,read,sha,score
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity
CASE='magna-key-reward'

def contract(t):
    marks={r['label']:r for r in t['milestones']};released=marks['field_released'];before=marks['before_award'];after=marks['natural_award'];end=marks['natural_return']
    assert released['tick']==1352 and released['active']==65535 and released['ball_state']==2
    assert before['tick']==1819 and before['active']==65535 and before['ball_state']==2
    assert after['tick']==1820 and after['ball_state']==3 and after['capture']==6 and after['active']==0
    assert after['candidates'][after['selected']]==11 and score(after)-score(before)==5000000
    assert after['magnets']==[0,0]and after['capture_wait']==150
    assert end['tick']==1970 and end['phase']==2 and end['ball_state']==2 and end['active']==0
    assert end['x']==120*65536 and end['y']==14*65536 and end['vx']==0 and end['vy']==640
    assert all(e['tick']<=1209 for e in t['diagnostic_shots'])
    actual=[(e['tick'],e['action'],e['down'])for e in t['inputs']if e['tick']>=1352]
    expected=[(tick,side,down)for tick,down in [(1352,False),(1472,True),(1592,False),(1712,True),(1820,False)]for side in ['left','right']]
    assert actual==expected and t['natural_flight_ticks']==468
    assert next(i for i,row in enumerate(t['states'])if row[0x58]==3 and row[0x5a]==6)==1820
    return dict(case=CASE,ticks=t['tick_count'],release_tick=1352,reward_tick=1820,return_tick=1970,amount=5000000,
        natural_flight_steps=468,last_diagnostic_tick=1209,inputs_after_release=expected)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe');p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview');a=p.parse_args()
    prepared=ROOT/'build/oracle/pirate-full-tick';game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT';dat=game/'DAT/PIRATE.DAT'
    folder=ROOT/'build/oracle/pirate-modes'/CASE;path=folder/'trace.json';t=read(path);f=read(ROOT/f'analysis/traces/pirate-{CASE}.json')
    n=integrity(t,f,sha((game/'SLAMTILT.EXE').read_bytes()),sha(dat.read_bytes()));report=contract(t)
    prefix=read(ROOT/'build/oracle/pirate-modes/magna-natural-both/trace.json')
    for key in KEYS:assert t[key][:1352+(key=='states')]==prefix[key][:1352+(key=='states')],key
    native=folder/'native-verified.json';rendered=folder/'rendered-verified.json';capture=folder/'verified.bmp'
    subprocess.run([a.native,prepared,dat,native,str(n),'--full','--lamps','--replay',path,'--diagnostic-shots',path],check=True)
    subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames',str(n//4),'--replay',path,'--diagnostic-shots',path,'--trace-output',rendered,'--capture',capture],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
    for label,file in [('native/reset',native),('SDL',rendered)]:
        v=read(file);assert v['tick_count']==n and v.get('error','')==''
        for key in KEYS:assert v[key]==t[key],(label,key)
    assert capture.read_bytes()[:2]==b'BM'
    report.update(status='VERIFIED original/native/reset/SDL key-only Magna flight/reward/return after diagnostic entry')
    (folder/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('2052 original/native/reset/SDL steps exact;468 key-only flight steps,5M reward and normal return')
if __name__=='__main__':main()
