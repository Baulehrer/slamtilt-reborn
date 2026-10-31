#!/usr/bin/env python3
"""Native raw Pirate import, protected outputs and full finite SDL trajectory."""
from retail_audio_fixture import corrected_audio_events
import argparse,hashlib,json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--native',type=Path,default=ROOT/'build/native/slampirate-import');p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview');a=p.parse_args()
    game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    recipe=json.loads((ROOT/'analysis/import/pirate-retail-startup.json').read_text())
    work=ROOT/'build/oracle/pirate-import';work.mkdir(parents=True,exist_ok=True)
    protected={p:sha(p)for p in [game/'SLAMTILT.EXE',game/'DAT/PIRATE.DAT',game/'DAT/MAIN.DAT']}
    with tempfile.TemporaryDirectory(prefix='acceptance-',dir=work)as tmp:
        temp=Path(tmp);out=temp/'private data $ literal';empty=temp/'existing';empty.mkdir();link=temp/'dangling';link.symlink_to(temp/'absent')
        env=dict(os.environ,PATH='/no-import-tools',SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
        def run(exe,dat,dest,ok):
            r=subprocess.run([a.native,exe,dat,dest],env=env,capture_output=True,text=True)
            assert (r.returncode==0)==ok,(r.returncode,r.stdout,r.stderr)
        run(game/'SLAMTILT.EXE',game/'DAT',out,True)
        for name,expected in recipe['files_sha256'].items():assert sha(out/name)==expected,name
        run(game/'SLAMTILT.EXE',game/'DAT',out,False)
        run(game/'SLAMTILT.EXE',game/'DAT',empty,False);assert empty.is_dir()and not list(empty.iterdir())
        run(game/'SLAMTILT.EXE',game/'DAT',link,False);assert link.is_symlink()
        bad=temp/'bad.exe';bad.write_bytes(b'bad');run(bad,game/'DAT',temp/'reject-exe',False)
        missing=temp/'missing';missing.mkdir();(missing/'PIRATE.DAT').symlink_to(game/'DAT/PIRATE.DAT')
        run(game/'SLAMTILT.EXE',missing,temp/'reject-main',False)
        (missing/'MAIN.DAT').write_bytes(b'corrupt');run(game/'SLAMTILT.EXE',missing,temp/'reject-dat',False)
        assert not any((temp/name).exists()for name in ['reject-exe','reject-main','reject-dat'])
        trace=work/'sdl.json';audio=work/'audio.json'
        case='acceptance-multiball';source=ROOT/f'analysis/traces/pirate-{case}.json'
        f=json.loads(source.read_text());gold=json.loads((ROOT/f'build/oracle/pirate-modes/{case}/trace.json').read_text())
        subprocess.run([a.viewer,out/'PIRATE.DAT','--pirate-play',out/'pirate-prepared',
            '--frames',str(f['tick_count']//4),'--replay',source,'--full-state-trace','--trace-output',trace,'--audio-trace',audio],check=True,env=env)
        t=json.loads(trace.read_text());assert not t['error']and t['tick_count']==f['tick_count']
        from verify_pirate_multiball import KEYS
        for key in KEYS+['magnasaver_state']:assert t[key]==gold[key],key
        camera=json.loads((ROOT/'analysis/traces/pirate-camera-sdl-original.json').read_text())
        for row,expected in zip(t['presentation_origins'],camera['frames']):
            for key in ['tick','camera_state','camera_scroll']:assert row[key]==expected[key]
        assert len(t['presentation_origins'])==len(camera['frames'])
        expected_audio=next(r for r in json.loads((ROOT/'analysis/traces/pirate-audio-events.json').read_text())['cases']if r['case']==case)
        actual=json.loads(audio.read_text());assert actual['events']==corrected_audio_events(expected_audio['events'], 'pirate')and actual['queued_bytes']>0 and not actual['error']
        for name,expected in recipe['files_sha256'].items():assert sha(out/name)==expected
        for path,expected in protected.items():assert sha(path)==expected
        report=dict(status='VERIFIED',steps=f['tick_count'],files=recipe['files_sha256'],native_only_import=True,
            protected_outputs=['existing data','empty directory','dangling symlink'],rejected=['wrong EXE','missing MAIN','corrupt MAIN'],
            gameplay_vectors=10,camera_frames=len(camera['frames']),audio_deliveries=len(actual['events']),
            scope='Exact supported Retail build; no Python/Wine/emulator/tools in import or game subprocess PATH. Test harness itself uses Python. Bounded startup recipe, not original full loader; not standalone package/first-start UI acceptance.')
        (ROOT/'analysis/traces/pirate-import-acceptance.json').write_text(json.dumps(report,indent=2)+'\n')
        print(f['tick_count'],'imported SDL steps / camera / audio exact;4files byte-exact; protected outputs PASS')
if __name__=='__main__':main()
