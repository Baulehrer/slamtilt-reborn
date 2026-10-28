#!/usr/bin/env python3
"""Relocated AppImage first import and four child launches, no project mounted."""
import argparse,json,os,shutil,subprocess,tempfile,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('appimage',type=Path);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
with tempfile.TemporaryDirectory(dir=ROOT/'build',prefix='appimage-check-')as tmp:
 w=Path(tmp);raw=w/'raw';raw.mkdir();state=w/'state';state.mkdir();(state/'tmp').mkdir()
 for name in ['MEAN','PIRATE','SPACE','DEMON','MAIN']:
  shutil.copyfile(ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT'/(name+'.DAT'),raw/(name+'.DAT'))
 base=['bwrap','--ro-bind','/usr','/usr','--symlink','usr/bin','/bin','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--ro-bind','/etc','/etc','--ro-bind',str(a.appimage.resolve()),'/app/game.AppImage','--ro-bind',str(raw),'/raw','--bind',str(state),'/state','--dir','/home','--dir','/tmp','--proc','/proc','--dev','/dev','--unshare-net','--chdir','/state']
 for k,v in {'HOME':'/state','XDG_DATA_HOME':'/state','TMPDIR':'/state/tmp','SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','PATH':'/usr/bin:/bin'}.items():base+=['--setenv',k,v]
 command=['/app/game.AppImage','--appimage-extract-and-run','--config','/state/menu.json']
 for args in [['--import','/raw','--frames','2'],['--exercise-all','--child-frames','16','--trace','/state/cycle.json']]:
  r=subprocess.run([*base,*command,*args],capture_output=True,text=True,timeout=180);assert r.returncode==0,(r.returncode,r.stdout[-1000:],r.stderr[-2000:])
 events=json.loads((state/'cycle.json').read_text())['events'];assert len(events)==8 and all(e.get('exit_code',0)==0 for e in events)
report={'status':'PASS','appimage_sha256':hashlib.sha256(a.appimage.read_bytes()).hexdigest(),'mode':'actual AppImage extract-and-run, bwrap networkoff and checkout hidden','native_first_import':True,'all_four_child_sessions':events,'limitations':['FUSE mounting and real GPU/audio not tested in this run']};a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n');print('AppImage isolated first import +four table launches PASS')
