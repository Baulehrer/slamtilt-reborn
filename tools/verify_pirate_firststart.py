#!/usr/bin/env python3
"""Relocated asset-free bundle: raw import/UI/saved path/game/camera/audio."""
import argparse,hashlib,json,os,shutil,subprocess,tarfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--program-archive',type=Path);p.add_argument('--output',type=Path,default=ROOT/'analysis/traces/pirate-firststart-acceptance.json');args=p.parse_args()
    with tempfile.TemporaryDirectory(prefix='pirate package ')as tmp:
        root=Path(tmp);build=root/'program';state=root/'state';state.mkdir();raw=root/'Original $(touch BAD) `false`';raw.mkdir();(raw/'DAT').mkdir()
        game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
        for name in ['SLAMTILT.EXE','DAT/PIRATE.DAT','DAT/MAIN.DAT']:shutil.copyfile(game/name,raw/name)
        if args.program_archive:shutil.copyfile(args.program_archive,str(build)+'.tar.gz')
        else:subprocess.run([ROOT/'tools/slampirate-pack','--output',build],check=True,stdout=subprocess.DEVNULL)
        # Archive is the input under test; no direct staged-folder shortcuts.
        if build.exists():shutil.rmtree(build)
        with tarfile.open(str(build)+'.tar.gz')as archive:
            archive_root=archive.getnames()[0].split('/')[0];archive.extractall(root/'unpacked',filter='data')
        app=root/'Relocated Pirate';shutil.move(root/'unpacked'/archive_root,app)
        manifest=json.loads((app/'bundle.json').read_text());assert not manifest['original_assets_included']
        assert not any(p.suffix.lower()in ['.dat','.exe','.bin']for p in app.rglob('*')if p.is_file())
        assert (app/'LICENSES/OFL.txt').exists()
        for name,digest in manifest['files'].items():assert hashlib.sha256((app/name).read_bytes()).hexdigest()==digest
        env=dict(os.environ,HOME=str(state),XDG_DATA_HOME=str(state),SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',LD_LIBRARY_PATH=str(app/'lib'))
        env.pop('PWD',None);env.pop('SLAM_TABLE_PROFILES',None);env.pop('SLAM_PIRATE_DATA_DIR',None)
        setup=[app/'bin/slampirate-setup','--importer',app/'bin/slampirate-import','--profile',app/'share/slamtilt/pirate-retail-startup.json']
        def run(cmd,ok=True):
            result=subprocess.run(cmd,cwd=root,env=env,capture_output=True,text=True,timeout=120)
            assert (result.returncode==0)==ok,(result.returncode,result.stderr,result.stdout)
            return result
        run([*setup,'--saved'],False)
        run([*setup,'--frames','2','--capture',root/'welcome.bmp'],False)
        trace=root/'import-access.log';cmd=[*setup,'--select',raw,'--capture',root/'import.bmp']
        imported=run(['strace','-f','-e','trace=file','-o',trace,*cmd]);data=Path(imported.stdout.strip())
        assert data.is_dir()and not (root/'BAD').exists()
        assert run([*setup,'--saved']).stdout.strip()==str(data)
        run([*setup,'--select',root],False);assert run([*setup,'--saved']).stdout.strip()==str(data)
        assert not list(state.rglob('mean-data-path.txt'))
        run([app/'slampirate','--check']);run([app/'slampirate','--data',data,'--check'])
        # New process uses saved data. Freeze input outside checkout; source evidence remains host-only.
        case='acceptance-multiball';fixture=json.loads((ROOT/f'analysis/traces/pirate-{case}.json').read_text())
        replay=root/'replay.json';replay.write_text(json.dumps(fixture));out=root/'game.json';audio=root/'audio.json'
        access=root/'game-access.log'
        run(['strace','-f','-e','trace=file','-o',access,app/'slampirate','--frames',str(fixture['tick_count']//4),
            '--replay',replay,'--full-state-trace','--trace-output',out,'--audio-trace',audio])
        t=json.loads(out.read_text());gold=json.loads((ROOT/f'build/oracle/pirate-modes/{case}/trace.json').read_text())
        from verify_pirate_multiball import KEYS
        assert not t['error']and t['tick_count']==fixture['tick_count']
        for key in KEYS+['magnasaver_state']:assert t[key]==gold[key],key
        camera=json.loads((ROOT/'analysis/traces/pirate-camera-sdl-original.json').read_text())
        assert len(t['presentation_origins'])==len(camera['frames'])
        for a,b in zip(t['presentation_origins'],camera['frames']):
            for key in ['tick','camera_state','camera_scroll']:assert a[key]==b[key]
        expected=next(r for r in json.loads((ROOT/'analysis/traces/pirate-audio-events.json').read_text())['cases']if r['case']==case)
        actual=json.loads(audio.read_text());assert actual['events']==expected['events']and actual['queued_bytes']>0 and not actual['error']
        for path in [trace,access]:
            text=path.read_text();assert str(ROOT)not in text and '/workspace/'not in text,[v for v in text.splitlines()if str(ROOT)in v or '/workspace/'in v][:3]
            assert not any('execve('in line and any(tool in line.split(', [',1)[0]for tool in ['python','wine','sha256sum'])for line in text.splitlines())
        recipe=json.loads((app/'share/slamtilt/pirate-retail-startup.json').read_text())
        for name,digest in recipe['files_sha256'].items():assert hashlib.sha256((data/name).read_bytes()).hexdigest()==digest
        assert (root/'welcome.bmp').stat().st_size>10000
        report=dict(status='VERIFIED',archive_relocated=True,original_assets_included=False,native_setup_import=True,
            saved_path=True,invalid_selection_preserves_preference=True,separate_mean_preference=True,
            steps=fixture['tick_count'],gameplay_vectors=10,camera_frames=len(camera['frames']),audio_requests=len(actual['events']),
            checkout_file_accesses=0,python_wine_checksum_execs=0,scope='Current Linux host userspace, dummySDL; no arbitrary older ABI/physical GPU/audio/native portal-click or filesystem namespace isolation claim.')
        args.output.write_text(json.dumps(report,indent=2)+'\n')
        print('Relocated Pirate package/import/saved selection/game/camera/audio PASS',report['steps'])
if __name__=='__main__':main()
