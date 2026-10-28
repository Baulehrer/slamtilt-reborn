#!/usr/bin/env python3
"""Rendered Reborn/classic layouts and options at laptop/full-HD/DPI-like sizes."""
import hashlib,json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def main():
 work=ROOT/'build/reborn-visuals';work.mkdir(exist_ok=True);rows=[]
 with tempfile.TemporaryDirectory(dir=work)as tmp:
  w=Path(tmp);env=dict(os.environ,XDG_DATA_HOME=str(w/'profile'),SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy');config=w/'frontend.json'
  for width,height in [(1280,720),(1280,800),(1920,1080),(2560,1600)]:
   for name,keys in [('main',[]),('options',['O']),('general',['O','Tab','Tab','Tab','Tab','Tab'])]:
    events=w/'events.json';events.write_text(json.dumps(dict(events=[dict(frame=i,key=k)for i,k in enumerate(keys)])))
    bmp=work/f'{width}x{height}-{name}.bmp';trace=w/'trace.json'
    subprocess.run([ROOT/'build/native/slamtilt','--config',config,'--preview-size',f'{width}x{height}','--frames','8','--ui-events',events,'--capture',bmp,'--trace',trace],env=env,check=True,stdout=subprocess.DEVNULL)
    t=read(trace);assert t['menu_style']=='reborn'and t['options_open']==bool(keys)
    from PIL import Image
    image=Image.open(bmp);assert image.size==(width,height);png=bmp.with_suffix('.png');image.save(png);bmp.unlink()
    rows.append(dict(width=width,height=height,view=name,screenshot=str(png.relative_to(ROOT)),sha256=hashlib.sha256(png.read_bytes()).hexdigest()))
 report=dict(status='VERIFIED_RENDERED_LAYOUTS',cases=rows,scope='Actual native SDL rendering at4sizes, including2xlogicalpixelcount. GPU/physicalDPI/visualinspection separate. Classic mode persistence covered main_menu_flow.')
 (ROOT/'analysis/traces/reborn-visuals.json').write_text(json.dumps(report,indent=2)+'\n');print('Reborn12layout renders PASS')
if __name__=='__main__':main()
