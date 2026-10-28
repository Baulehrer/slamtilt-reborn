#!/usr/bin/env python3
"""Twelve original/native/reset/SDL Nudge/Tilt contracts plus real SDL key events."""
import argparse,json,os,subprocess
from pathlib import Path
from verify_pirate_modes import ROOT,read,sha,jsha
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity
CASES=['left','right','up','warning','decay','prelaunch','tilt-game','tilt-knife','tilt-magna','tilt-crocodile','tilt-held-magna','tilt-held-crocodile']

def contract(case,t):
    nudge=t['nudge'];calls=t['warning_calls'];marks={m['label']:m for m in t['milestones']}
    assert len(nudge)==t['tick_count']and all(len(row)==18 for row in nudge)
    if case.startswith('tilt-'):
        start=t['prefix_ticks'] or 600
        assert [(v['tick'],v['argument'],v['counter'],v['target'])for v in calls]==[(start+4,0,79,'0x4344c8'),(start+8,1,118,'0x4344c8')]
        at=marks['input_'+str(start+8)]['nudge'];assert at[11:17]==[1,0,0,0xffffffff,0xffffffff,0xffffffff]
        # Further key-down while Tilted must not reactivate any flipper latch.
        assert marks['input_'+str(start+24)]['nudge'][12:17]==[0,0,0,0,0]
        assert any(s[7]==3 for s in t['timing'][start:]),'Tilt must drain naturally'
        if case=='tilt-game':
            clear=next(i for i in range(start+8,len(nudge))if nudge[i][11]==0)
            assert t['timing'][clear][7]==1 and t['lifecycle'][clear][4]==2
            assert all(s[11]==1 for s in nudge[start+8:clear])
            assert t['timing'][-1][7]==2 and nudge[-1][11]==0
        else:
            clear=next(i for i in range(start+8,len(nudge))if nudge[i][11]==0)
            assert t['timing'][clear][7]==1 and t['lifecycle'][clear][4]==2
            assert all(s[11]==1 for s in nudge[start+8:clear])
            assert t['timing'][-1][7]==1 and nudge[-1][11]==0
    else:
        assert all(s[11]==0 for s in nudge)
        if case=='warning':
            assert calls==[dict(tick=604,target='0x4344c8',argument=0,counter=79)]
            assert len(set(t['dmd_sha256'][608:800]))==2
        else:assert calls==[]
        if case=='prelaunch':assert all(s[10]==0 for s in nudge[:200])
        if case=='decay':assert all(nudge[t][10]==40 for t in [600,800,1000])and nudge[-1][10]==0
        if case in ['left','right']:assert any(s[6]for s in nudge[600:680])
        if case=='up':assert any(s[8]for s in nudge[600:680])
    return dict(case=case,steps=t['tick_count'],prefix_ticks=t['prefix_ticks'],warning_calls=calls)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe');p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview');a=p.parse_args()
    prepared=ROOT/'build/oracle/pirate-full-tick';game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT';dat=game/'DAT/PIRATE.DAT'
    buildsha=sha((game/'SLAMTILT.EXE').read_bytes());datsha=sha(dat.read_bytes());reports=[];traces={}
    env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
    for case in CASES:
        folder=ROOT/'build/oracle/pirate-modes'/('nudge-'+case);path=folder/'trace.json';t=read(path);f=read(ROOT/f'analysis/traces/pirate-nudge-{case}.json')
        n=integrity(t,f,buildsha,datsha);assert jsha(t['nudge'])==f['nudge_sha256']
        for key in ['nudge_addresses','warning_calls','prefix_ticks']:assert t[key]==f[key]
        reports.append(contract(case,t));traces[case]=t
        native=folder/'native-verified.json';rendered=folder/'rendered-verified.json';capture=folder/'verified.bmp'
        subprocess.run([a.native,prepared,dat,native,str(n),'--full','--lamps','--replay',path,'--diagnostic-shots',path],check=True)
        subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames',str(n//4),'--replay',path,'--diagnostic-shots',path,'--trace-output',rendered,'--capture',capture],check=True,env=env)
        for label,file in [('native/reset',native),('SDL',rendered)]:
            v=read(file);assert v['tick_count']==n and v.get('error','')==''
            for key in [*KEYS,'nudge']:assert v[key]==t[key],(case,label,key)
            if label=='SDL':
                origins=v['presentation_origins'];assert len(origins)==n//4
                for frame,row in enumerate(origins):
                    tick=4*(frame+1);assert row['tick']==tick
                    values=t['nudge'][tick-1]
                    signed=lambda value:value-(1<<32)if value>=1<<31 else value
                    horizontal,vertical=signed(values[9]),signed(values[7])
                    assert row['horizontal_pixels']==horizontal and row['vertical_fixed']==vertical
                    # Original source RECT runs are retained separately in63 fixtures.
                    expected=[-horizontal,-max(0,min(row['camera_scroll']+(vertical>>16),208))]
                    assert row['origin']==expected,(case,tick,row,expected)
        assert capture.read_bytes()[:2]==b'BM'
    for l,r in zip(traces['left']['nudge'][600:680],traces['right']['nudge'][600:680]):
        assert (l[5]+r[5])&0xffffffff==0 and (l[6]+r[6])&0xffffffff==0
    assert traces['left']['states'][680]!=traces['right']['states'][680], 'Nudges must affect actual ball motion'
    output=ROOT/'build/oracle/pirate-nudge-frontend.json'
    subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames','14','--nudge-acceptance',output],check=True,env=env)
    expected=[dict(frame=f,direction=d,accepted=True)for f,d in [(1,-1),(5,1),(7,0),(9,-1),(11,0),(12,-1)]]
    assert read(output)==expected,read(output)
    report=dict(status='VERIFIED',build_sha256=buildsha,dat_sha256=datsha,cases=reports,
        total_steps=sum(t['tick_count']for t in traces.values()),native_reset_exact=True,sdl_exact=True,
        sdl_key_events=expected,limitations=['Mode entries use frozen diagnostic physical prefixes; ordinary Nudge/Tilt cases use keys only.','No claim of physical host/Alt desktop shortcut acceptance.'])
    (ROOT/'build/oracle/pirate-nudge-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('12 Nudge/Tilt original/native/reset/SDL cases;',report['total_steps'],'steps exact; actual SDL default/remapped keys and focus/pause/options/minimize/repeat gates pass')
if __name__=='__main__':main()
