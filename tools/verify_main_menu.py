#!/usr/bin/env python3
"""Original-menu pixels, shared import, four actual native children and return lifecycle."""
import argparse,hashlib,json,os,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--native',type=Path,default=ROOT/'build/native/slamtilt');p.add_argument('--report',type=Path,default=ROOT/'analysis/traces/reborn-menu-acceptance.json');a=p.parse_args();work=ROOT/'build/menu-acceptance';work.mkdir(exist_ok=True)
 game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT';demo=ROOT/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT'
 with tempfile.TemporaryDirectory(dir=work)as tmp:
  w=Path(tmp);env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',XDG_DATA_HOME=str(w/'profile'));config=w/'menu.json'
  def run(*args,ok=True):
   r=subprocess.run([a.native,'--config',config,*map(str,args)],env=env,text=True,capture_output=True,timeout=120);assert (r.returncode==0)==ok,(r.stdout[-1000:],r.stderr[-1800:]);return r
  run('--frames',3,'--capture',work/'menu.bmp','--trace',w/'initial.json');assert read(w/'initial.json')['original_menu']and read(w/'initial.json')['menu_style']=='reborn';assert (work/'menu.bmp').stat().st_size>10000
  run('--import',game,'--frames',1);c=read(config)
  for table in ['pirate','space','demon']:
   dest=Path(c['tables'][table]['data']);recipe=read(ROOT/f'analysis/import/{table}-dat-startup.json')
   for name,h in recipe['files_sha256'].items():assert sha(dest/name)==h
  run('--import',demo,'--frames',1);c=read(config);mean=Path(c['tables']['mean']['data'])
  for line in (ROOT/'packaging/mean-retail-data.sha256').read_text().splitlines():
   h,name=line.split(maxsplit=1);assert sha(mean/name.strip())==h
  run('--exercise-all','--child-frames',4,'--trace',w/'cycle.json');events=read(w/'cycle.json')['events'];assert len(events)==8
  for i,table in enumerate(['mean','pirate','space','demon']):assert events[i*2]==dict(event='launched',table=table)and events[i*2+1]==dict(event='returned',table=table,exit_code=0)
  keys=w/'keys.json';keys.write_text(json.dumps(dict(events=[dict(frame=0,key='O')])));run('--frames',2,'--ui-events',keys,'--trace',w/'options.json');assert read(w/'options.json')['options_open']
  bad=w/'partial-retail';(bad/'DAT').mkdir(parents=True)
  for name in ['SLAMTILT.EXE','DAT/PIRATE.DAT','DAT/MAIN.DAT']:shutil.copyfile(game/name,bad/name)
  (bad/'DAT/SPACE.DAT').write_bytes(b'corrupt')
  original=config.read_bytes();before_dirs=set((w/'profile/SlamTiltNative/SlamTilt').glob('*-menu-data-*'))
  run('--import',bad,'--frames',1,ok=False)
  assert config.read_bytes()==original and set((w/'profile/SlamTiltNative/SlamTilt').glob('*-menu-data-*'))==before_dirs
  theme_keys=['O','Tab','Tab','Tab','Tab','Tab','Right','Down','Down','Down','Return']
  keys.write_text(json.dumps(dict(events=[dict(frame=i,key=k)for i,k in enumerate(theme_keys)])))
  run('--frames',12,'--ui-events',keys,'--trace',w/'classic.json','--capture',work/'classic.bmp');assert read(w/'classic.json')['menu_style']=='classic'
  run('--frames',1,'--trace',w/'theme-reload.json');assert read(w/'theme-reload.json')['menu_style']=='classic'
  run('--frames',12,'--ui-events',keys,'--trace',w/'modern.json');assert read(w/'modern.json')['menu_style']=='reborn'
  before=config.read_bytes();run('--import',w/'absent','--frames',1,ok=False);assert config.read_bytes()==before
  run('--menu',w/'missing.dat','--frames',1,'--trace',w/'fallback.json');assert not read(w/'fallback.json')['original_menu']
  report=dict(status='VERIFIED',original_menu_sha256=sha(game/'DAT/MENU.DAT'),shared_retail_import=['pirate','space','demon'],mean_demo_import=True,all_imported_files_exact=True,children=[e for e in events if e['event']=='returned'],options_open=True,classic_modern_theme_persistence=True,failed_import_preserves_config=True,partial_import_rolls_back=True,missing_art_fallback=True,scope='Actual native subprocess starts/returns with finite4-frame games, dummySDL. F10/MainMenu quit-event behavior checked by port_options CTest; no physical mouse/keyboard claim.')
  a.report.write_text(json.dumps(report,indent=2)+'\n');print('Original menu/import/four native tables/options/return PASS')
if __name__=='__main__':main()
