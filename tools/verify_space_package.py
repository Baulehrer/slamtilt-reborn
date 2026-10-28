#!/usr/bin/env python3
"""Extracted Space archive: native first import, masked checkout, session/storage."""
import argparse,hashlib,json,os,shutil,subprocess,tarfile,tempfile
from pathlib import Path
from verify_space_session import compare
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,default=ROOT/'build/compat/releases/slamtilt-space-rc1.tar.gz');a=p.parse_args()
 with tempfile.TemporaryDirectory(prefix='space package ')as tmp:
  root=Path(tmp);state=root/'state';state.mkdir();raw=root/'raw $(touch BAD) `false`';raw.mkdir();(raw/'DAT').mkdir();nsraw='/tmp/case/Original $(touch BAD) `false`'
  game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
  for n in ['SLAMTILT.EXE','DAT/SPACE.DAT','DAT/MAIN.DAT']:shutil.copyfile(game/n,raw/n)
  with tarfile.open(a.archive)as t:
   name=t.getnames()[0].split('/')[0];t.extractall(root/'unpack',filter='data')
  app=root/'app';shutil.move(root/'unpack'/name,app);manifest=read(app/'bundle.json');assert not manifest['original_assets_included']
  for n,h in manifest['files'].items():assert hashlib.sha256((app/n).read_bytes()).hexdigest()==h,n
  assert not any(p.suffix.lower()in['.exe','.dat','.bin']for p in app.rglob('*')if p.is_file())
  base=['bwrap','--ro-bind','/','/','--tmpfs','/home','--tmpfs','/tmp','--bind',str(root),'/tmp/case','--ro-bind',str(app),'/tmp/case/app','--ro-bind',str(raw),nsraw,'--unshare-net','--proc','/proc','--dev','/dev','--chdir','/tmp/case','--setenv','HOME','/tmp/case/state','--setenv','XDG_DATA_HOME','/tmp/case/state','--setenv','SDL_VIDEODRIVER','dummy','--setenv','SDL_AUDIODRIVER','dummy','--setenv','LD_LIBRARY_PATH','/tmp/case/app/lib','--unsetenv','SLAM_TABLE_PROFILES','--unsetenv','SLAM_SPACE_DATA_DIR']
  def run(cmd,ok=True,empty=False,trace=None):
   prefix=base+(['--setenv','PATH','/no-import-tools']if empty else[])
   if trace:prefix+=['/usr/bin/strace','-f','-e','trace=file','-o','/tmp/case/'+trace]
   r=subprocess.run([*prefix,*map(str,cmd)],capture_output=True,text=True,timeout=180)
   if (r.returncode==0)!=ok and (root/'import-access.log').exists():shutil.copyfile(root/'import-access.log',ROOT/'build/space-package-failure-access.log')
   assert (r.returncode==0)==ok,(r.stderr[-1800:],r.stdout[-1000:]);return r.stdout.strip()
  setup=['/tmp/case/app/bin/slamspace-setup','--importer','/tmp/case/app/bin/slamspace-import','--profile','/tmp/case/app/share/slamtilt/space-retail-startup.json']
  run([*setup,'--saved'],False,True);run([*setup,'--frames',2,'--capture','/tmp/case/welcome.bmp'],False);assert (root/'welcome.bmp').stat().st_size>10000
  data=run([*setup,'--select',nsraw],empty=True,trace='import-access.log');assert data.startswith('/tmp/case/state/')
  assert run([*setup,'--saved'],empty=True)==data
  run([*setup,'--select','/tmp/case'],False);assert run([*setup,'--saved'])==data
  assert not list(state.rglob('mean-data-path.txt'))and not list(state.rglob('pirate-data-path.txt'))
  run(['/tmp/case/app/slamspace','--check']);run(['/tmp/case/app/slamspace','--data',data,'--check'])
  source=ROOT/'build/oracle/space-full-game/trace.json';shutil.copyfile(source,root/'replay.json')
  run(['/tmp/case/app/slamspace','--frames',3000,'--replay','/tmp/case/replay.json','--trace','/tmp/case/game.json','--audio','--audio-trace','/tmp/case/audio.json','--highscore-file','/tmp/case/state/scores.json'],trace='game-access.log')
  t=read(root/'game.json');compare(t,read(source));assert t['tick_count']==12000
  audio=read(root/'audio.json');assert audio['enabled']and audio['queued_bytes']>0
  scores=read(state/'scores.json');stamp=(state/'scores.json').stat().st_mtime_ns
  run(['/tmp/case/app/slamspace','--frames',1,'--highscore-file','/tmp/case/state/scores.json','--trace','/tmp/case/reload.json'])
  assert read(root/'reload.json')['highscore_loaded']and (state/'scores.json').stat().st_mtime_ns==stamp
  keys=['Escape','Down','Down','Down','Right','Tab','Right','Tab','Right','Tab','Left','Tab','Down','Down','Down','Down','Down','Down','Return']
  events=[dict(frame=i,type='key',key=k,down=True)for i,k in enumerate(keys)]+[dict(frame=19,type='focus_lost'),dict(frame=20,type='focus_gained')]
  (root/'events.json').write_text(json.dumps(dict(events=events)))
  run(['/tmp/case/app/slamspace','--presentation','--persist-options','--frames',22,'--ui-events','/tmp/case/events.json','--audio','--audio-trace','/tmp/case/menu-audio.json','--trace','/tmp/case/menu.json'])
  f=read(root/'menu.json')['ui_frames'];assert all(v['tick']==0 and v['menu']and v['audio_device_paused']for v in f[:18]);assert f[19]['tick']==f[18]['tick']and not f[19]['focused']and f[19]['audio_device_paused'];assert f[20]['tick']>f[19]['tick']and not f[20]['audio_device_paused']
  assert abs(f[-1]['zoom']-1.05)<1e-5 and f[-1]['dmd_position']==1
  run(['/tmp/case/app/slamspace','--presentation','--persist-options','--frames',1,'--trace','/tmp/case/options-reload.json']);assert abs(read(root/'options-reload.json')['ui_frames'][0]['zoom']-1.05)<1e-5
  for name in ['import-access.log','game-access.log']:
   text=(root/name).read_text();assert str(ROOT)not in text and '/workspace/'not in text
   assert not any('execve('in l and any(v in l.split(', [',1)[0]for v in ['python','wine','sha256sum'])for l in text.splitlines())
  assert not (root/'BAD').exists();recipe=read(app/'share/slamtilt/space-retail-startup.json');hostdata=root/Path(data).relative_to('/tmp/case')
  for n,h in recipe['files_sha256'].items():assert hashlib.sha256((hostdata/n).read_bytes()).hexdigest()==h,n
  report=dict(status='VERIFIED',archive_sha256=hashlib.sha256(a.archive.read_bytes()).hexdigest(),archive_relocated=True,original_assets_included=False,checkout_hidden=True,program_and_originals_readonly=True,network_disabled=True,native_import_empty_PATH=True,saved_selection=True,separate_preferences=True,finite_game_steps=12000,original_game_vectors_exact=True,highscore_save_reload_no_rewrite=True,options_reload=True,menu_focus_audio_pause=True,audio_requests=len(audio['events']),checkout_accesses=0,python_wine_checksum_execs=0,scope='Extracted archive in filesystem namespace on current host userspace; dummySDL. Native portal click, physical listening and full-raster parity not claimed.')
  (ROOT/'analysis/traces/space-package-acceptance.json').write_text(json.dumps(report,indent=2)+'\n');print('Space isolated package/import/session PASS')
if __name__=='__main__':main()
