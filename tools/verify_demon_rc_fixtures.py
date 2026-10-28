#!/usr/bin/env python3
"""Run all completion fixtures against the imported packaged RC; no checkout data runtime."""
import argparse,hashlib,json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,separators=(',',':')).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--app',type=Path,default=ROOT/'build/compat/releases/slamtilt-demon-rc1');a=p.parse_args();app=a.app.resolve();contract=read(ROOT/'analysis/demon-completion-contract.json');rows=[]
 game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT';work=ROOT/'build/demon-rc-fixtures';work.mkdir(exist_ok=True)
 with tempfile.TemporaryDirectory(dir=work)as tmp:
  w=Path(tmp);data=w/'original data';env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',LD_LIBRARY_PATH=str(app/'lib'))
  subprocess.run([app/'bin/slamdemon-import',game/'SLAMTILT.EXE',game/'DAT',data],check=True,env=env)
  for case,f in contract['fixtures'].items():
   fixture=ROOT/f['path'];assert sha(fixture)==f['sha256'];g=read(fixture);gold=read(ROOT/f'build/oracle/demon-modes/{case}-rewards.json');n=g['tick_count'];assert n%4==0
   profile=w/case;profile.mkdir();e=dict(env,HOME=str(profile),XDG_DATA_HOME=str(profile));trace=w/'game.json';audio=w/'audio.json'
   cmd=[app/'slamdemon','--data',data,'--frames',str(n//4),'--replay',fixture,'--replay-only','--trace',trace,'--audio-trace',audio]
   if g['diagnostic_shots']:cmd+=['--diagnostic-shots',fixture]
   subprocess.run(cmd,check=True,env=e,stdout=subprocess.DEVNULL,timeout=180)
   t=read(trace);sound=read(audio);assert t['tick_count']==n
   # Pin Original JSON bytes; compare numeric values as existing oracle verifiers do
   # (C++ JSON may serialize an exact integral float as an integer).
   for k,h in g['sequence_sha256'].items():
    assert digest(gold[k])==h,(case,k,'Original fixture hash')
    assert t[k]==gold[k],(case,k)
   assert sound['events']==g['audio_events']and sound['enabled']and sound['queued_bytes']>0,case
   rows.append(dict(case=case,fixture_sha256=f['sha256'],steps=n,vectors_exact=True,vector_count=len(g['sequence_sha256']),audio_exact=True,audio_requests=len(sound['events'])))
   print(case,n,'PASS',flush=True)
 report=dict(status='VERIFIED',archive_sha256=sha(Path(str(app)+'.tar.gz')),cases=rows,total_steps=sum(r['steps']for r in rows),scope='All36 SHA-pinned bounded completion cases against native-imported packaged binary with fresh per-case profiles and Original reset check; dummySDL. Diagnostic contacts retained where fixtures declare them.')
 (ROOT/'analysis/traces/demon-rc-fixtures.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
