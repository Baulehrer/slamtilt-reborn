#!/usr/bin/env python3
"""Native raw Pirate import, protected outputs and full finite SDL trajectory."""
import argparse,hashlib,json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--native',type=Path,default=ROOT/'build/native/slamspace-import');p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamslice');a=p.parse_args()
    game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    recipe=json.loads((ROOT/'analysis/import/space-retail-startup.json').read_text())
    work=ROOT/'build/oracle/space-import';work.mkdir(parents=True,exist_ok=True)
    protected={p:sha(p)for p in [game/'SLAMTILT.EXE',game/'DAT/SPACE.DAT',game/'DAT/MAIN.DAT']}
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
        missing=temp/'missing';missing.mkdir();(missing/'SPACE.DAT').symlink_to(game/'DAT/SPACE.DAT')
        run(game/'SLAMTILT.EXE',missing,temp/'reject-main',False)
        (missing/'MAIN.DAT').write_bytes(b'corrupt');run(game/'SLAMTILT.EXE',missing,temp/'reject-dat',False)
        assert not any((temp/name).exists()for name in ['reject-exe','reject-main','reject-dat'])
        trace=work/'sdl.json';audio=work/'audio.json'
        source=ROOT/'build/oracle/space-full-game/trace.json';gold=json.loads(source.read_text());n=12000
        subprocess.run([a.viewer,'space',out/'space-prepared',out/'SPACE.DAT',
            '--frames',str(n//4),'--replay',source,'--trace',trace,'--audio','--audio-trace',audio],check=True,env=env)
        t=json.loads(trace.read_text());assert t['tick_count']==n
        from verify_space_session import compare
        compare(t,gold)
        actual=json.loads(audio.read_text());assert actual['enabled']and actual['queued_bytes']>0
        for name,expected in recipe['files_sha256'].items():assert sha(out/name)==expected
        for path,expected in protected.items():assert sha(path)==expected
        report=dict(status='VERIFIED',steps=n,files=recipe['files_sha256'],native_only_import=True,
            protected_outputs=['existing data','empty directory','dangling symlink'],rejected=['wrong EXE','missing MAIN','corrupt MAIN'],
            gameplay_vectors_exact=True,audio_deliveries=len(actual['events']),
            scope='Five exact-profile files from supported raw Retail; native subprocess PATH has no Python/Wine/emulator. Bounded startup recipe, not original full loader; standalone package tested separately.')
        (ROOT/'analysis/traces/space-import-acceptance.json').write_text(json.dumps(report,indent=2)+'\n')
        print(n,'imported Space SDL steps exact;5files byte-exact; protected outputs PASS')
if __name__=='__main__':main()
