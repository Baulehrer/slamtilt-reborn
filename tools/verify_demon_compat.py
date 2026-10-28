#!/usr/bin/env python3
"""Actual Debian userspace: raw Demon import and Original-exact rule fixtures."""
import argparse,hashlib,json,os,shutil,subprocess,tempfile
from pathlib import Path
from verify_demon_legal import KEYS
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def main():
 p=argparse.ArgumentParser();p.add_argument('--report',type=Path,default=ROOT/'analysis/traces/demon-compat-acceptance.json');a=p.parse_args();meta=read(ROOT/'build/compat/demon-build.json');app=Path(meta['program']);manifest=read(app/'bundle.json');maxima={}
 for symbol in manifest['runtime_requirements']:
  k,v=symbol.split('_',1);version=lambda s:tuple(map(int,s.split('.')))
  assert version(v)<=version(meta['pins']['abi_ceiling'][k]),symbol
  if k not in maxima or version(v)>version(maxima[k]):maxima[k]=v
 with tempfile.TemporaryDirectory(prefix='.demon-abi-',dir=ROOT/'build/compat')as tmp:
  temp=Path(tmp);raw=temp/'raw';raw.mkdir();(raw/'DAT').mkdir();state=temp/'state';state.mkdir()
  game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
  for n in ['SLAMTILT.EXE','DAT/DEMON.DAT','DAT/MAIN.DAT']:shutil.copyfile(game/n,raw/n)
  replay=temp/'replay.json';replay.write_text('{}')
  base=['docker','run','--rm','--network','none','--read-only','--tmpfs','/tmp','--user',f'{os.getuid()}:{os.getgid()}', '--mount',f'type=bind,src={app},dst=/app,readonly','--mount',f'type=bind,src={raw},dst=/raw,readonly','--mount',f'type=bind,src={state},dst=/state','--mount',f'type=bind,src={replay},dst=/replay.json,readonly','-e','HOME=/state','-e','XDG_DATA_HOME=/state/prefs','-e','SDL_VIDEODRIVER=dummy','-e','SDL_AUDIODRIVER=dummy','-e','LD_LIBRARY_PATH=/app/lib']
  def run(cmd,empty=False):
   r=subprocess.run([*base,*(['-e','PATH=/no-import-tools']if empty else[]),meta['image_id'],*map(str,cmd)],capture_output=True,text=True,timeout=180);assert r.returncode==0,(r.stderr[-2000:],r.stdout[-1000:]);return r.stdout.strip()
  libc=run(['ldd','--version']).splitlines()[0]
  data=run(['/app/bin/slamdemon-setup','--importer','/app/bin/slamdemon-import','--profile','/app/share/slamtilt/demon-retail-startup.json','--select','/raw'],True)
  recipe=read(app/'share/slamtilt/demon-retail-startup.json');host=state/Path(data).relative_to('/state')
  for n,h in recipe['files_sha256'].items():assert hashlib.sha256((host/n).read_bytes()).hexdigest()==h,n
  run(['/app/slamdemon','--check']);rows=[]
  for case in ['legal-game','witch-force-on','twice-cycles','zombie-values']:
   gold=read(ROOT/f'build/oracle/demon-modes/{case}-rewards.json');replay.write_text(json.dumps(gold));n=gold['tick_count']
   run(['/app/slamdemon','--frames',n//4,'--replay','/replay.json',*(['--diagnostic-shots','/replay.json']if gold.get('diagnostic_shots')else[]),'--replay-only','--trace','/state/game.json','--audio','--audio-trace','/state/audio.json'])
   t=read(state/'game.json');sound=read(state/'audio.json')
   for k in KEYS:assert t[k]==gold[k],(case,k)
   assert sound['events']==gold['audio_events']and sound['queued_bytes']>0
   rows.append(dict(case=case,steps=n,audio=len(sound['events']),ten_vectors_exact=True));print('Debian Demon',case,'PASS',flush=True)
  for n,h in recipe['files_sha256'].items():assert hashlib.sha256((host/n).read_bytes()).hexdigest()==h,n
 report=dict(status='VERIFIED',abi_maxima=maxima,older_runtime=libc,image_id=meta['image_id'],archive_sha256=hashlib.sha256(Path(str(app)+'.tar.gz').read_bytes()).hexdigest(),native_import_empty_PATH=True,five_files_exact=True,checkout_not_mounted=True,network_disabled=True,program_originals_readonly=True,cases=rows,total_steps=sum(r['steps']for r in rows),scope='Actual Debian12 userdemon, shared host kernel; dummySDL. Not universal distro/GPU-driver compatibility.')
 a.report.write_text(json.dumps(report,indent=2)+'\n');meta.update(verification_pending=False,verification='analysis/traces/demon-compat-acceptance.json');(ROOT/'build/compat/demon-build.json').write_text(json.dumps(meta,indent=2)+'\n');print('Demon compatibility PASS',maxima)
if __name__=='__main__':main()
