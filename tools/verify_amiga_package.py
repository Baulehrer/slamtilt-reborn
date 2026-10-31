#!/usr/bin/env python3
"""Debian12 relocated package: only five ADFs and fresh state, no checkout/PC data."""
import argparse,hashlib,json,os,shutil,subprocess,tempfile
from verify_dat_only_import import exact_prefix,world_states
from retail_audio_fixture import corrected_audio_events
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--ticks',type=int,default=4000);p.add_argument('--legacy-audio-fixture',action='store_true',help='Expect historical 0/0 startup from an unchanged older package');p.add_argument('--report',type=Path,default=ROOT/'analysis/traces/amiga-package-debian12.json');a=p.parse_args();package=a.package.resolve();assert a.ticks>0 and a.ticks%4==0
 manifest=read(package/'frontend-bundle.json')
 for name,h in manifest['files'].items():assert sha(package/name)==h,name
 assert not manifest['original_assets_included']
 assert not any(f.suffix.lower()in['.exe','.dat','.bin']for f in package.rglob('*')if f.is_file())
 image=read(ROOT/'build/compat/build.json')['image_id'];cases=[]
 with tempfile.TemporaryDirectory(prefix='adf-package-',dir=ROOT/'build')as temp:
  work=Path(temp);raw=work/'adfs';raw.mkdir();state=work/'state';state.mkdir();fixtures=work/'fixtures';fixtures.mkdir()
  for f in (ROOT/'amiga/historical-mods/DLM').glob('*.adf'):shutil.copyfile(f,raw/f.name)
  originals={f.name:sha(f)for f in raw.iterdir()};assert len(originals)==5
  for table in ['mean','pirate','space','demon']:
   source=read(ROOT/f'build/reborn-playtest/{table}/primary-{"input"if table=="mean"else"oracle"}.json');(fixtures/(table+'.json')).write_text(json.dumps({'inputs':source['inputs']}))
  base=['docker','run','--rm','--network','none','--read-only','--user',f'{os.getuid()}:{os.getgid()}','--tmpfs','/tmp','--tmpfs','/run']
  for src,dst,ro in [(package,'/app',True),(raw,'/raw',True),(state,'/state',False),(fixtures,'/fixtures',True)]:base+=['--mount',f'type=bind,src={src},dst={dst}'+(',readonly'if ro else '')]
  for k,v in {'HOME':'/state','XDG_DATA_HOME':'/state','PATH':'/no-tools','LD_LIBRARY_PATH':'/app/lib','SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','SLAM_TABLE_PROFILES':'/app/share/slamtilt/table-profiles.json'}.items():base+=['--env',f'{k}={v}']
  def run(command,ok=True):
   result=subprocess.run([*base,image,*map(str,command)],capture_output=True,text=True,timeout=240)
   assert(result.returncode==0)==ok,(command,result.returncode,result.stderr[-1800:],result.stdout[-1000:])
  run(['/usr/bin/test','!','-e',str(ROOT)]);run(['/usr/bin/test','!','-e','/workspace/CMakeLists.txt']);run(['/usr/bin/test','!','-e','/raw/SLAMTILT.EXE'])
  run(['/app/slamimport','--adf','/raw','/state/direct'])
  assert read(state/'direct/amiga-import.json')['windows_files_required']is False
  before={str(q.relative_to(state/'direct')):sha(q)for q in (state/'direct').rglob('*')if q.is_file()}
  run(['/app/slamimport','--adf','/raw','/state/direct'],False)
  assert before=={str(q.relative_to(state/'direct')):sha(q)for q in (state/'direct').rglob('*')if q.is_file()}
  menu=['/app/bin/slamtilt','--config','/state/menu.json'];run([*menu,'--import','/raw','--frames','1'])
  config=read(state/'menu.json');assert all(row['source']=='amiga'for row in config['tables'].values())
  for repeat in range(2):
   run([*menu,'--exercise-all','--child-frames','16','--trace',f'/state/menu-cycle-{repeat}.json'])
   events=read(state/f'menu-cycle-{repeat}.json')['events'];assert len(events)==8 and all(e.get('exit_code',0)==0 for e in events)
  for table in ['mean','pirate','space','demon']:
   paths=config['tables'][table];data=paths['data'];prepared=paths['prepared'];trace='/state/'+table+'-game.json';frames=str(a.ticks//4)
   if table=='mean':cmd=['/app/bin/slamview',data+'/MEAN.DAT','--play',prepared,'--trace','/app/share/slamtilt/initial-state.json','--retail-minigame','--trace-output',trace,'--realtime-steps',str(a.ticks),'--frames',str(a.ticks//4+1)]
   elif table=='pirate':cmd=['/app/bin/slamview',data+'/PIRATE.DAT','--pirate-play',prepared,'--full-state-trace','--trace-output',trace,'--frames',frames]
   else:cmd=['/app/bin/slamslice',table,prepared,data+'/'+table.upper()+'.DAT','--trace',trace,'--frames',frames,'--presentation']
   if table!='mean':cmd+=['--audio-trace','/state/'+table+'-audio.json']
   if table in ['space','demon']:cmd+=['--audio']
   run([*cmd,'--replay','/fixtures/'+table+'.json','--replay-only'])
   result=read(state/(table+'-game.json'));assert result['tick_count']==a.ticks
   if table=='mean':
    reference=read(ROOT/'build/reborn-playtest/mean/primary-native.json')
    assert not result['failure'] and result['audio_driver']!='none'
    assert len(result['states'])==a.ticks
    exact_prefix(world_states(result['states']),world_states(reference['states']),table,'states')
    audio=result['audio_events'];vectors=['states excluding camera_scroll']
   else:
    reference=read(ROOT/f'build/reborn-playtest/{table}/primary-oracle.json')
    vectors=['states','lifecycle','ball_pool_sha256']
    for vector in vectors:
     extra=len(reference[vector])-reference['tick_count'];assert extra in [0,1]
     assert len(result[vector])==a.ticks+extra,(table,vector,len(result[vector]),a.ticks+extra)
     exact_prefix(result[vector],reference[vector],table,vector)
    sound=read(state/(table+'-audio.json'));assert sound['enabled']
    audio=sound['events']
   expected_audio=[e for e in reference['audio_events']if e[0]<a.ticks]
   if table!='mean' and not a.legacy_audio_fixture:expected_audio=corrected_audio_events(expected_audio,table)
   assert audio==expected_audio,(table,'shared native audio events')
   cases.append({'table':table,'shared_native_state_vectors':vectors,'audio_requests':len(audio),'audio_sha256':hashlib.sha256(json.dumps(audio,separators=(',',':')).encode()).hexdigest(),'tick_count':a.ticks,'trace_sha256':sha(state/(table+'-game.json')),'status':'PASS'})
   print(table,a.ticks,'isolated Debian12 ADF-only ticks PASS',flush=True)
  assert originals=={f.name:sha(f)for f in raw.iterdir()}
 report={'status':'PASS','legacy_audio_fixture':a.legacy_audio_fixture,'image_id':image,'package_manifest_sha256':sha(package/'frontend-bundle.json'),'runtime_requirements':manifest['runtime_requirements'],'adf_sha256':originals,'cases':cases,'first_import':'ADF-only native, empty PATH, no checkout or PC files mounted','menu':'four imports, two reload/child cycles','protection':'read-only program/ADFs/root filesystem; network disabled; existing destination preserved','limitations':['Shared native gameplay, no original Amiga physics/rule parity claim','Dummy SDL, not a subjective GPU/audio test','Remaining individual scene fragments not mapped']}
 a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
