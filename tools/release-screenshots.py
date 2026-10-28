#!/usr/bin/env python3
"""Capture genuine SDL software-rendered release screenshots from private local data."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def main():
 work=ROOT/'build/github-release/v0.1.0-rc1/screenshot-proof';work.mkdir(parents=True,exist_ok=True)
 output=ROOT/'docs/screenshots';output.mkdir(exist_ok=True)
 stage=work.parent/'screenshots';stage.mkdir(exist_ok=True)
 binary=ROOT/'build/native';game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT';demo=ROOT/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT'
 env=dict(os.environ,SDL_VIDEO_DRIVER='dummy',SDL_AUDIO_DRIVER='dummy',SDL_RENDER_DRIVER='software',XDG_DATA_HOME=str(work/'prefs'),SLAM_TABLE_PROFILES=str(ROOT/'analysis/table-profiles.json'))
 rows=[]
 def capture(name,args):
  bmp=work/(name+'.bmp');cmd=[str(x) for x in [*args,'--capture',bmp]]
  r=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=120)
  (work/(name+'.log')).write_text(r.stdout+r.stderr)
  if r.returncode:raise RuntimeError(name+': '+r.stderr[-1500:])
  image=Image.open(bmp).convert('RGB');crop=None
  if name not in ['main-menu','options-menu']:
   left=(image.width-720)//2;crop=[left,0,left+720,image.height];image=image.crop(crop)
  dest=output/(name+'.png');image.save(dest,optimize=True)
  assert dest.stat().st_size<=1024*1024
  shutil.copy2(dest,stage/dest.name)
  rows.append(dict(name=name,crop=crop,width=image.width,height=image.height,bytes=dest.stat().st_size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),command=cmd,binary_sha256=hashlib.sha256(Path(cmd[0]).read_bytes()).hexdigest()))
 capture('main-menu',[binary/'slamtilt','--config',work/'frontend.json','--preview-size','1280x800','--frames','8','--trace',work/'main-menu.json'])
 events=work/'options-events.json';events.write_text(json.dumps({'events':[{'frame':0,'key':'O'}]}))
 capture('options-menu',[binary/'slamtilt','--config',work/'frontend.json','--preview-size','1280x800','--frames','8','--ui-events',events,'--trace',work/'options-menu.json'])
 capture('mean-machines',[binary/'slamview',demo/'MEAN.DAT','--play',ROOT/'build/mean-prepared','--retail-minigame','--trace',ROOT/'analysis/traces/mean-flight-100.json','--replay',ROOT/'build/reborn-playtest/mean/primary-input.json','--frames','180','--preview-size','1280x800','--trace-output',work/'mean.json'])
 capture('the-pirate',[binary/'slamview',game/'PIRATE.DAT','--pirate-play',ROOT/'build/oracle/pirate-complete-game-lamps-ready','--replay',ROOT/'build/reborn-playtest/pirate/primary-oracle.json','--frames','180','--trace-output',work/'pirate.json'])
 for table,name in [('space','ace-of-space'),('demon','night-of-the-demon')]:
  capture(name,[binary/'slamslice',table,ROOT/f'build/oracle/{table}-full-game',game/(table.upper()+'.DAT'),'--presentation','--replay',ROOT/f'build/reborn-playtest/{table}/primary-oracle.json','--frames','180','--trace',work/(table+'.json')])
 (work/'capture-proof.json').write_text(json.dumps(dict(format=1,renderer='SDL software',video_driver='dummy',gpu_shader_claim=False,scope='Actual native game pixels with user-owned original data; PNG conversion and unchanged-pixel side-margin crop only; no compositing or generated image content.',screenshots=rows),indent=2)+'\n')
 print(json.dumps([{k:r[k] for k in ['name','width','height','bytes']} for r in rows],indent=2))
if __name__=='__main__':main()
