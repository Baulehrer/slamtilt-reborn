#!/usr/bin/env python3
"""Relocated four-table archive; hidden checkout, native imports/children, empty PATH."""
import argparse,hashlib,json,os,shutil,subprocess,tarfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,default=ROOT/'build/releases/slamtilt-four-tables-064.tar.gz');p.add_argument('--report',type=Path,default=ROOT/'analysis/traces/reborn-package-isolation.json');a=p.parse_args()
 with tempfile.TemporaryDirectory(prefix='slam menu ')as tmp:
  w=Path(tmp);state=w/'state';state.mkdir();retail=w/'retail';demo=w/'demo'
  for dest,game,names in [(retail,ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT',['SLAMTILT.EXE','DAT/MENU.DAT','DAT/MAIN.DAT','DAT/PIRATE.DAT','DAT/SPACE.DAT','DAT/DEMON.DAT']), (demo,ROOT/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT',['SLAMTILT.EXE','DAT/MAIN.DAT','DAT/MEAN.DAT'])]:
   for name in names:(dest/name).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(game/name,dest/name)
  with tarfile.open(a.archive)as t:name=t.getnames()[0].split('/')[0];t.extractall(w/'unpack',filter='data')
  app=w/'app';shutil.move(w/'unpack'/name,app);manifest=read(app/'frontend-bundle.json');assert not manifest['original_assets_included']
  for name,h in manifest['files'].items():assert sha(app/name)==h
  base=['bwrap','--ro-bind','/','/','--tmpfs','/home','--tmpfs','/tmp','--bind',w,'/tmp/case','--ro-bind',app,'/tmp/case/app','--ro-bind',retail,'/tmp/case/retail','--ro-bind',demo,'/tmp/case/demo','--unshare-net','--proc','/proc','--dev','/dev','--chdir','/tmp/case','--setenv','HOME','/tmp/case/state','--setenv','XDG_DATA_HOME','/tmp/case/state','--setenv','LD_LIBRARY_PATH','/tmp/case/app/lib','--setenv','SDL_VIDEODRIVER','dummy','--setenv','SDL_AUDIODRIVER','dummy','--setenv','PATH','/no-tools','--unsetenv','SLAM_TABLE_PROFILES']
  def run(*args):
   r=subprocess.run([*map(str,base),'/tmp/case/app/bin/slamtilt','--config','/tmp/case/state/menu.json',*map(str,args)],capture_output=True,text=True,timeout=120);assert r.returncode==0,(r.stderr[-2000:],r.stdout[-1000:])
  run('--import','/tmp/case/retail','--frames',1);run('--import','/tmp/case/demo','--frames',1)
  run('--exercise-all','--child-frames',4,'--trace','/tmp/case/state/cycle.json');events=read(state/'cycle.json')['events'];assert len(events)==8 and all(e.get('exit_code',0)==0 for e in events);assert [e['table']for e in events if e['event']=='returned']==['mean','pirate','space','demon']
  run('--frames',2,'--capture','/tmp/case/state/menu.bmp','--trace','/tmp/case/state/menu-trace.json');assert read(state/'menu-trace.json')['original_menu']
  assert not any(p.suffix.lower()in['.dat','.exe','.bin']for p in app.rglob('*')if p.is_file())
  report=dict(status='VERIFIED',archive_sha256=sha(a.archive),original_assets_included=False,checkout_hidden=True,network_disabled=True,program_originals_readonly=True,empty_PATH_native_import_and_gameplay=True,four_children_returned=True,original_menu_rendered=True,scope='Relocated extracted current-host build, dummySDL; original Retail art after import, Mean Demo and all3Retail tables launch/return4frames. Individual frozen older-ABI RCs preserved; combined older-ABI/GPU/listening not claimed.')
  a.report.write_text(json.dumps(report,indent=2)+'\n');print('Four-table isolated package PASS')
if __name__=='__main__':main()
