#!/usr/bin/env python3
"""Old Pirate ABI: actual Debian userspace, raw setup import, full replay, host."""
import argparse,hashlib,json,os,re,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--rule-cases',nargs='*',default=[]);parser.add_argument('--output',type=Path,default=ROOT/'analysis/traces/pirate-compat-acceptance.json');parser.add_argument('--host-output',type=Path,default=ROOT/'analysis/traces/pirate-compat-package-acceptance.json');args=parser.parse_args()
    args.output=args.output.resolve();args.host_output=args.host_output.resolve()
    build=ROOT/'build/compat';metadata=json.loads((build/'pirate-build.json').read_text());app=Path(metadata['program'])
    manifest=json.loads((app/'bundle.json').read_text());maxima={}
    for symbol in manifest['runtime_requirements']:
        kind,value=symbol.split('_',1);version=lambda v:tuple(map(int,v.split('.')))
        assert version(value)<=version(metadata['pins']['abi_ceiling'][kind]),symbol
        if kind not in maxima or version(value)>version(maxima[kind]):maxima[kind]=value
    assert set(maxima)=={'GLIBC','GLIBCXX','CXXABI'}
    host=args.host_output
    subprocess.run(['python3',ROOT/'tools/verify_pirate_firststart.py','--program-archive',str(app)+'.tar.gz','--output',host],check=True)
    with tempfile.TemporaryDirectory(prefix='.pirate-abi-',dir=build)as tmp:
        temp=Path(tmp);state=temp/'state';state.mkdir();raw=temp/'raw';raw.mkdir();(raw/'DAT').mkdir()
        game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
        for name in ['SLAMTILT.EXE','DAT/PIRATE.DAT','DAT/MAIN.DAT']:shutil.copyfile(game/name,raw/name)
        replay=temp/'replay.json';case='acceptance-multiball';shutil.copyfile(ROOT/f'analysis/traces/pirate-{case}.json',replay)
        fixture=json.loads(replay.read_text());gold=json.loads((ROOT/f'build/oracle/pirate-modes/{case}/trace.json').read_text())
        base=['docker','run','--rm','--network','none','--read-only','--tmpfs','/tmp','--user',f'{os.getuid()}:{os.getgid()}',
            '--mount',f'type=bind,src={app},dst=/app,readonly','--mount',f'type=bind,src={raw},dst=/raw,readonly',
            '--mount',f'type=bind,src={replay},dst=/replay.json,readonly','--mount',f'type=bind,src={state},dst=/state',
            '--mount',f'type=bind,src={build}/native/sha256_tests,dst=/sha256-check,readonly',
            '-e','HOME=/state','-e','XDG_DATA_HOME=/state/prefs','-e','SDL_VIDEODRIVER=dummy','-e','SDL_AUDIODRIVER=dummy','-e','LD_LIBRARY_PATH=/app/lib']
        def run(cmd,empty_path=False):
            p=subprocess.run([*base,*(['-e','PATH=/no-import-tools']if empty_path else[]),metadata['image_id'],*map(str,cmd)],capture_output=True,text=True,timeout=120)
            assert p.returncode==0,(cmd,p.stderr[-2000:],p.stdout[-1000:]);return p.stdout.strip()
        libc=run(['ldd','--version']).splitlines()[0];run(['/sha256-check'])
        selected=run(['/app/bin/slampirate-setup','--importer','/app/bin/slampirate-import','--profile','/app/share/slamtilt/pirate-retail-startup.json','--select','/raw'],True)
        data=state/Path(selected).relative_to('/state')
        recipe=json.loads((app/'share/slamtilt/pirate-retail-startup.json').read_text())
        for name,digest in recipe['files_sha256'].items():assert hashlib.sha256((data/name).read_bytes()).hexdigest()==digest
        run(['/app/slampirate','--check'])
        for kind in ['audio','nudge','special']:
            run(['/app/slampirate','--frames','14',f'--{kind}-acceptance',f'/state/{kind}.json'])
        assert json.loads((state/'audio.json').read_text())['passed']
        for kind,values,key in [('nudge',[-1,1,0,-1,0,-1],'direction'),('special',[224,224,224,224,224,29],'scancode')]:
            expected=[dict(frame=f,**{key:v},accepted=True)for f,v in zip([1,5,7,9,11,12],values)]
            assert json.loads((state/f'{kind}.json').read_text())==expected
        run(['/app/slampirate','--frames',fixture['tick_count']//4,'--replay','/replay.json','--full-state-trace','--trace-output','/state/game.json','--audio-trace','/state/events.json'])
        t=json.loads((state/'game.json').read_text());assert not t['error']and t['tick_count']==fixture['tick_count']
        from verify_pirate_multiball import KEYS
        for key in KEYS+['magnasaver_state']:assert t[key]==gold[key],key
        camera=json.loads((ROOT/'analysis/traces/pirate-camera-sdl-original.json').read_text());assert len(t['presentation_origins'])==len(camera['frames'])
        for a,b in zip(t['presentation_origins'],camera['frames']):
            for key in ['tick','camera_state','camera_scroll']:assert a[key]==b[key]
        events=json.loads((state/'events.json').read_text());expected=next(r for r in json.loads((ROOT/'analysis/traces/pirate-audio-events.json').read_text())['cases']if r['case']==case)
        assert events['events']==expected['events']and events['queued_bytes']>0 and not events['error']
        for name,digest in recipe['files_sha256'].items():assert hashlib.sha256((data/name).read_bytes()).hexdigest()==digest
        rule_rows=[]
        for rule_case in args.rule_cases:
            rule_fixture=json.loads((ROOT/f'analysis/traces/pirate-{rule_case}.json').read_text())
            replay.write_text(json.dumps(rule_fixture));rule_steps=rule_fixture['tick_count']
            run(['/app/slampirate','--frames',rule_steps//4,'--replay','/replay.json','--diagnostic-shots','/replay.json','--full-state-trace','--no-audio','--trace-output','/state/rule.json'])
            rule_trace=json.loads((state/'rule.json').read_text());rule_golden=json.loads((ROOT/f'build/oracle/pirate-modes/{rule_case}/trace.json').read_text())
            assert not rule_trace['error']and rule_trace['tick_count']==rule_steps
            for key in KEYS+['magnasaver_state']:assert rule_trace[key]==rule_golden[key],(rule_case,key)
            rule_rows.append(dict(case=rule_case,steps=rule_steps,vectors=10))
        out=build/'pirate-acceptance';out.mkdir(exist_ok=True)
        for name in ['audio.json','nudge.json','special.json','events.json']:shutil.copyfile(state/name,out/name)
    report=dict(status='VERIFIED',abi_maxima=maxima,older_runtime=libc,image_id=metadata['image_id'],program=str(app),archive_sha256=hashlib.sha256(Path(str(app)+'.tar.gz').read_bytes()).hexdigest(),
        host_package_report=str(host.relative_to(ROOT)),old_userspace_steps=fixture['tick_count'],gameplay_vectors=10,camera_frames=len(camera['frames']),audio_requests=len(events['events']),
        raw_import_four_files_exact=True,import_empty_path=True,known_sha_vectors=True,native_setup_saved_start=True,three_event_acceptances=True,rule_cases=rule_rows,
        network_disabled=True,source_checkout_not_mounted=True,program_originals_readonly=True,
        scope='Actual Debian12glibc2.36 userspace and currenthost; container shareshostkernel. No universaldistribution/driver compatibility claim.')
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    metadata.update(verification_pending=False,verification=str(args.output.relative_to(ROOT)));(build/'pirate-build.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print('Pirate older ABI VERIFIED',maxima,libc)
if __name__=='__main__':main()
