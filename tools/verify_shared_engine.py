#!/usr/bin/env python3
"""Bounded Mean/Pirate parity for an alternative native frontend build."""
import os,subprocess,json,hashlib,argparse
from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--output',type=Path,default=r/'build/shared-engine-verification');p.add_argument('--frames',type=int,default=1000);args=p.parse_args();
if args.frames<1:p.error('frames must be positive')
w=args.output;w.mkdir(parents=True,exist_ok=True)
env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software')
rows=[]
for table in ['mean','pirate']:
 runs=[]
 for label,directory in [('before',args.before),('after',args.after)]:
  output=w/f'{table}-{label}.json';bmp=w/f'{table}-{label}.bmp'
  binary=str(directory.resolve()/'slamview')
  if table=='mean':cmd=[binary,str(r/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT'),'--play',str(r/'build/mean-prepared'),'--trace',str(r/'analysis/traces/mean-flight-100.json'),'--retail-minigame','--replay',str(r/'build/reborn-playtest/mean/primary-input.json'),'--realtime-steps',str(args.frames*4),'--frames',str(args.frames+1)]
  else:cmd=[binary,str(r/'build/imported/pirate-retail/PIRATE.DAT'),'--pirate-play',str(r/'build/oracle/pirate-complete-game-lamps-ready'),'--replay',str(r/'build/reborn-playtest/pirate/primary-oracle.json'),'--full-state-trace','--replay-only','--frames',str(args.frames)]
  profile=directory.resolve().parent/'share/slamtilt/table-profiles.json'
  env['SLAM_TABLE_PROFILES']=str(profile if profile.exists() else r/'analysis/table-profiles.json')
  subprocess.run(cmd+['--trace-output',str(output),'--capture',str(bmp)],env=env,check=True,stdout=subprocess.DEVNULL)
  runs.append(json.loads(output.read_text()))
 a,b=runs;ignored={'elapsed_ms','real_wall_ms','ui_frames','timing_profile','session_ui_frames','runtime_sha256'}
 diffs=[k for k in a if k not in ignored and a[k]!=b.get(k)]
 assert not diffs,(table,diffs)
 assert b.get('tick_count')==args.frames*4
 assert (w/f'{table}-before.bmp').read_bytes()==(w/f'{table}-after.bmp').read_bytes()
 rows.append({'table':table,'differences':diffs,'before_keys':list(a),'ticks':b.get('tick_count'),'bmp_exact':(w/f'{table}-before.bmp').read_bytes()==(w/f'{table}-after.bmp').read_bytes()})
 print(rows[-1],flush=True)
(w/'report.json').write_text(json.dumps(rows,indent=2)+'\n')
