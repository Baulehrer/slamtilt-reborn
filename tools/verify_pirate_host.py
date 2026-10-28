#!/usr/bin/env python3
"""Actual host or controlled dummy driver matrix for Pirate event/audio gates."""
import argparse,json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--launcher',type=Path,default=ROOT/'tools/slampirate');p.add_argument('--data',type=Path,default=ROOT/'build/imported/pirate-retail');p.add_argument('--dummy',action='store_true');p.add_argument('--repeat',type=int,default=2);p.add_argument('--output',type=Path);a=p.parse_args()
    work=ROOT/'build/oracle/pirate-host';work.mkdir(parents=True,exist_ok=True);rows=[]
    env=dict(os.environ)
    if a.dummy:env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
    else:
        env.pop('SDL_VIDEODRIVER',None);env.pop('SDL_AUDIODRIVER',None)
        assert env.get('DISPLAY')or env.get('WAYLAND_DISPLAY'),'Actual host requires a desktop'
    for full in [False,True]:
        for kind in ['audio','nudge','special']:
            for repeat in range(a.repeat):
                label=f'{"dummy"if a.dummy else"desktop"}-{full}-{kind}-{repeat}'
                out=work/(label+'.json');trace=work/(label+'-trace.json')
                cmd=[a.launcher,'--data',a.data,'--fullscreen'if full else'--windowed','--frames','14',f'--{kind}-acceptance',out,'--trace-output',trace]
                result=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=30)
                assert result.returncode==0,(label,result.stderr)
                calls=json.loads(out.read_text());state=json.loads(trace.read_text());assert not state['error']
                if kind=='audio':
                    assert calls['passed']and calls['fullscreen']==full,calls
                    assert calls['video_driver']not in ['dummy','offscreen']or a.dummy
                    assert calls['audio_driver']!='dummy'or a.dummy
                    assert calls['checks'][2]['ticks']==calls['checks'][1]['ticks']
                    assert calls['checks'][3]['ticks']>calls['checks'][2]['ticks']
                    driver={k:calls[k]for k in ['video_driver','audio_driver','game_window_id']}
                else:
                    frames=[1,5,7,9,11,12]
                    expected=[dict(frame=f,**({'direction':d}if kind=='nudge'else{'scancode':d}),accepted=True)
                        for f,d in zip(frames,[-1,1,0,-1,0,-1]if kind=='nudge'else[224,224,224,224,224,29])]
                    assert calls==expected,(label,calls)
                    assert state['tick_count']==40,(label,state['tick_count'])
                    driver={}
                rows.append(dict(label=label,kind=kind,fullscreen=full,ticks=state['tick_count'],**driver))
                print(label,'PASS',flush=True)
    report=dict(status='VERIFIED',dummy=a.dummy,cases=rows,scope='Actual SDL event handlers, scripted focus/minimize/pause/options/mute/reset and remapped input. Desktop mode uses real video/audio drivers; no physical listening or external Alt-Tab automation claim.')
    path=a.output or ROOT/f'analysis/traces/pirate-host-{"dummy"if a.dummy else"desktop"}.json';path.write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
