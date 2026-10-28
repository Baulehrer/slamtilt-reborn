#!/usr/bin/env python3
"""Frozen original camera consumers vs real SDL, with gameplay preservation."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from verify_pirate_multiball import KEYS

def main():
    viewer=Path(sys.argv[1]);fixture=json.loads((ROOT/'analysis/traces/pirate-camera-sdl-original.json').read_text())
    case=fixture['source_case'];source=ROOT/f'analysis/traces/pirate-{case}.json'
    assert hashlib.sha256(source.read_bytes()).hexdigest()==fixture['source_fixture_sha256']
    out=ROOT/'build/oracle/pirate-camera-sdl-verified.json'
    dat=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT'
    subprocess.run([viewer,dat,'--pirate-play',ROOT/'build/oracle/pirate-full-tick',
        '--frames',str(fixture['tick_count']//4),'--no-audio','--replay',source,'--full-state-trace','--trace-output',out],check=True,
        env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
    t=json.loads(out.read_text());assert not t['error']and t['tick_count']==fixture['tick_count']
    golden=json.loads((ROOT/f'build/oracle/pirate-modes/{case}/trace.json').read_text())
    for key in KEYS+['magnasaver_state']:assert t[key]==golden[key],('unchanged gameplay',key)
    assert len(t['presentation_origins'])==len(fixture['frames'])
    for actual,expected in zip(t['presentation_origins'],fixture['frames']):
        for key in ['tick','camera_state','camera_scroll']:assert actual[key]==expected[key],(key,expected['tick'])
        assert actual['origin']==[-actual['horizontal_pixels'],-max(0,min(208,actual['camera_scroll']+(actual['vertical_fixed']>>16)))]
    print(len(fixture['frames']),'SDL camera frames exact; gameplay10vectors unchanged')
if __name__=='__main__':main()
