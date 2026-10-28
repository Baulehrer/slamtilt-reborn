#!/usr/bin/env python3
"""Observe SDL camera inputs, independently execute original camera consumers."""
import json,os,subprocess
from pirate_adventure_oracle import ROOT,Original,BUILD_SHA,digest,compact
from verify_pirate_multiball import KEYS

def main():
    case='acceptance-multiball';source=ROOT/f'analysis/traces/pirate-{case}.json'
    golden=json.loads((ROOT/f'build/oracle/pirate-modes/{case}/trace.json').read_text())
    out=ROOT/'build/oracle/pirate-camera-sdl.json';capture=ROOT/'build/oracle/pirate-camera-sdl.bmp'
    dat=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT'
    subprocess.run([ROOT/'build/native/slamview',dat,'--pirate-play',ROOT/'build/oracle/pirate-full-tick',
        '--frames',str(golden['tick_count']//4),'--no-audio','--replay',source,'--full-state-trace',
        '--trace-output',out,'--capture',capture],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
    t=json.loads(out.read_text());assert not t['error']
    for key in KEYS+['magnasaver_state']:assert t[key]==golden[key],('gameplay unchanged',key)
    m=Original(ROOT/'build/oracle/pirate-full-tick');context=0x1007000
    m.put(0x46c72c,context);m.put(context+0x10,200);m.put(context+0x1c,400)
    for a,v in [(0x46c688,0),(0x454a94,0),(0x454d8c,0),(0x454d90,0),(0x454a98,0),(0x454a9c,1)]:m.put(a,v)
    restarts={e['tick']for e in t['inputs']if e['action']=='new_game'}if 'inputs'in t else {e['tick']for e in golden['inputs']if e['action']=='new_game'}
    previous=[];tick=0;rows=[]
    for frame in t['presentation_origins']:
        m.put(0x46c67c,len(previous))
        for i,(y,state)in enumerate(previous):
            address=0x46c15c+100*i;m.put(0x454b68+4*i,address)
            m.put(address+0x10,(y&65535)<<16);m.put(address+0x58,state,2)
        while tick<frame['tick']:
            phase=1 if tick==0 or tick in restarts else t['lifecycle'][tick-1][0]
            m.put(0x46c6ac,phase);m.run(0x409350);tick+=1
        state=[m.get(a)for a in [0x46c688,0x454a94,0x454d8c,0x454d90,0x454a98,0x454a9c]]
        state=[v if v<0x80000000 else v-0x100000000 for v in state]
        assert state==frame['camera_state'],('camera',tick,state,frame['camera_state'])
        m.put(0x46c744,0);m.put(0x46c4a4,0);m.put(0x46c5f4,0)
        m.run(0x405486,until=0x4054e1);scroll=m.get(context+8)
        assert scroll==frame['camera_scroll'],('scroll',tick)
        previous=frame['projected_balls'];rows.append(dict(tick=tick,camera_state=state,camera_scroll=scroll))
    public=ROOT/'analysis/traces/pirate-camera-sdl-original.json'
    public.write_bytes(compact(dict(schema=1,build_sha256=BUILD_SHA,source_case=case,
        source_fixture_sha256=digest(source.read_bytes()),tick_count=tick,frames=rows,
        scope='Actual original409350 and405486 consumers fed frozen SDL previous-frame projections/phase sequence; all10existing gameplay vectors unchanged. No whole original raster or render-scheduler equivalence claim.'))+b'\n')
    print(tick,'SDL steps /',len(rows),'original camera frames exact; all10gameplay vectors unchanged')
if __name__=='__main__':main()
