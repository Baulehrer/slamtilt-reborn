#!/usr/bin/env python3
"""Actual older userspace acceptance for the shared native import/frontend bundle."""
import argparse,hashlib,json,os,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--retail-only',action='store_true');p.add_argument('--dat-only',action='store_true');p.add_argument('--report',type=Path,default=ROOT/'analysis/traces/reborn-distribution.json');a=p.parse_args()
 if a.dat_only:a.retail_only=True
 meta=read(ROOT/'build/compat/reborn-build.json');app=Path(meta['program']);archive=Path(str(app)+'.tar.gz');archive_sha=sha(archive);manifest=read(app/'frontend-bundle.json');maxima={}
 for item in manifest['runtime_requirements']:
  key,value=item.split('_',1);version=lambda s:tuple(map(int,s.split('.')))
  assert version(value)<=version(meta['pins']['abi_ceiling'][key]),item
  if key not in maxima or version(value)>version(maxima[key]):maxima[key]=value
 with tempfile.TemporaryDirectory(prefix='.reborn-runtime-',dir=ROOT/'build/compat')as tmp:
  w=Path(tmp);state=w/'state';state.mkdir();raw=w/'raw';demo=w/'demo'
  names=['DAT/MAIN.DAT','DAT/MEAN.DAT','DAT/MENU.DAT','DAT/PIRATE.DAT','DAT/SPACE.DAT','DAT/DEMON.DAT']
  if not a.dat_only:names.insert(0,'SLAMTILT.EXE')
  sources=[(raw,ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT',names)]
  if not a.retail_only:sources.append((demo,ROOT/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT',['SLAMTILT.EXE','DAT/MEAN.DAT','DAT/MAIN.DAT']))
  else:demo.mkdir()
  for dest,source,names in sources:
   for name in names:(dest/name).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/name,dest/name)
  replay=w/'replay.json';replay.write_text('{}')
  base=['docker','run','--rm','--network','none','--read-only','--tmpfs','/tmp','--user',f'{os.getuid()}:{os.getgid()}','--mount',f'type=bind,src={app},dst=/app,readonly','--mount',f'type=bind,src={raw},dst=/raw,readonly','--mount',f'type=bind,src={demo},dst=/demo,readonly','--mount',f'type=bind,src={state},dst=/state','--mount',f'type=bind,src={replay},dst=/replay.json,readonly','-e','HOME=/state','-e','XDG_DATA_HOME=/state','-e','SDL_VIDEODRIVER=dummy','-e','SDL_AUDIODRIVER=dummy','-e','LD_LIBRARY_PATH=/app/lib','-e','SLAM_TABLE_PROFILES=/app/share/slamtilt/table-profiles.json']
  def run(args,empty=False):
   r=subprocess.run([*base,*(['-e','PATH=/no-tools']if empty else[]),meta['image_id'],*map(str,args)],capture_output=True,text=True,timeout=180);assert r.returncode==0,(r.stdout[-1000:],r.stderr[-2000:]);return r.stdout.strip()
  libc=run(['ldd','--version']).splitlines()[0]
  native=['/app/bin/slamtilt','--config','/state/frontend.json']
  for folder in (['/raw']if a.retail_only else['/raw','/demo']):run([*native,'--import',folder,'--frames',1],True)
  run([*native,'--exercise-all','--child-frames',4,'--trace','/state/session.json'],True)
  events=read(state/'session.json')['events'];assert len(events)==8 and all(e.get('exit_code',0)==0 for e in events)
  assert [e['table']for e in events if e['event']=='returned']==['mean','pirate','space','demon']
  assert run(['/app/slamtilt-reborn','--help'])==run(['/app/slamtilt','--help'])
  config=read(state/'frontend.json');sessions=[]
  for table in ['pirate','space','demon']:
   data=state/Path(config['tables'][table]['data']).relative_to('/state');recipe=read(app/f'share/slamtilt/{table}-dat-startup.json')
   for n,h in recipe['files_sha256'].items():assert sha(data/n)==h
  data=state/Path(config['tables']['mean']['data']).relative_to('/state')
  mean_profile='mean-retail-data.sha256'
  for line in (app/'share/slamtilt'/mean_profile).read_text().splitlines():h,n=line.split(maxsplit=1);assert sha(data/n.strip())==h
  for table in ['mean','pirate','space','demon']:
   source=ROOT/(f'build/reborn-playtest/{table}/primary-'+('input.json'if table=='mean'else'oracle.json'));g=read(source);n=g['tick_count'];replay.write_text(json.dumps(dict(inputs=g['inputs'])))
   data=config['tables'][table]['data'];prepared=config['tables'][table]['prepared']
   if table=='mean':cmd=['/app/bin/slamview',data+'/MEAN.DAT','--play',prepared,'--trace','/app/share/slamtilt/initial-state.json','--retail-minigame','--trace-output','/state/game.json','--realtime-steps',n]
   elif table=='pirate':cmd=['/app/bin/slamview',data+'/PIRATE.DAT','--pirate-play',prepared,'--full-state-trace','--trace-output','/state/game.json','--audio-trace','/state/audio.json','--replay-only']
   else:cmd=['/app/bin/slamslice',table,prepared,data+'/'+table.upper()+'.DAT','--trace','/state/game.json','--audio','--audio-trace','/state/audio.json','--presentation','--replay-only']
   run([*cmd,'--frames',n//4+1 if table=='mean'else n//4,'--replay','/replay.json'],True)
   t=read(state/'game.json');assert t['tick_count']==n,(table,t['tick_count'])
   if table=='mean':
    baseline=read(ROOT/'build/reborn-playtest/mean/primary-native.json');assert t['states']==baseline['states']and t['audio_events']==baseline['audio_events']
   else:
    keys=['states','lifecycle','highscore_sha256','lamp_sha256','ball_pool_sha256']+(['timing','dmd_sha256','rule_sha256','video_sha256']if table=='pirate'else['poses','globals']+(['raw_state_sha256']if table=='demon'else[]))
    for key in keys:assert t[key]==g[key],(table,key)
    assert read(state/'audio.json')['events']==g['audio_events'],table
   sessions.append(dict(table=table,steps=n,exact=True,equivalence_target='native baseline + separate Original components'if table=='mean'else'configured Original Retail',whole_original_trajectory=table!='mean'));print('Debian Reborn',table,n,'PASS',flush=True)
 assert sha(archive)==archive_sha,'Archive changed during runtime acceptance'
 report=dict(status='VERIFIED',project='Slamtilt - Reborn',archive_sha256=archive_sha,actual_runtime=libc,image_id=meta['image_id'],abi_maxima=maxima,checkout_not_mounted=True,network_disabled=True,program_originals_readonly=True,empty_PATH_import_and_four_children=True,all_imported_files_exact=True,old_launcher_alias=True,accelerated_sessions=sessions,total_steps=sum(s['steps']for s in sessions),scope='Actual pinned Debian12 userspace/currenthost kernel, dummySDL. HostGPU/audio/endurance/focus separately recorded.')
 report['retail_only_inputs']=a.retail_only
 report['dat_only_inputs']=a.dat_only
 a.report.write_text(json.dumps(report,indent=2)+'\n');print('Reborn actual Debian12 runtime/import/four tables PASS',maxima)
if __name__=='__main__':main()
