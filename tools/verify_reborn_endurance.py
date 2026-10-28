#!/usr/bin/env python3
"""Serialize four real five-minute GPU sessions against the final immutable archive."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def telemetry():
 import os
 sample={'monotonic':time.monotonic(),'loadavg':list(os.getloadavg())}
 try:sample['actual_active_pid']=json.loads(subprocess.check_output(['hyprctl','activewindow','-j'],text=True,timeout=1)).get('pid',0)
 except (OSError,subprocess.SubprocessError,ValueError):sample['actual_active_pid']=None
 for item in ['cpu','memory','io']:
  path=Path('/proc/pressure')/item
  if path.exists():sample[item+'_pressure']=path.read_text().strip()
 temps={}
 for path in Path('/sys/class/thermal').glob('thermal_zone*/temp'):
  try:temps[path.parent.name]=int(path.read_text())
  except (OSError,ValueError):pass
 sample['temperatures_mC']=temps
 return sample

def main():
 p=argparse.ArgumentParser();p.add_argument('--app',type=Path,default=ROOT/'build/compat/releases/slamtilt-reborn-linux-x86_64-rc1');p.add_argument('--resume',action='store_true');p.add_argument('--controlled-focus',action='store_true');a=p.parse_args();app=a.app.resolve();work=ROOT/'build/reborn-endurance';work.mkdir(exist_ok=True);archive=Path(str(app)+'.tar.gz');archive_sha=sha(archive);rows=[];started=time.monotonic()
 def progress(table,state):
  (work/'progress.json').write_text(json.dumps(dict(table=table,state=state,completed=len(rows),total=4,elapsed_seconds=round(time.monotonic()-started,1)),indent=2)+'\n')
 for table in ['mean','pirate','space','demon']:
  assert sha(archive)==archive_sha,'Release archive changed during acceptance'
  existing=ROOT/f'analysis/traces/reborn-{table}-primary-realtime.json'
  if a.resume and existing.exists():
   old=json.loads(existing.read_text())
   if old.get('archive_sha256')==archive_sha and old.get('tick_count')==60000 and old.get('clamped_frames')==0:
    rows.append(dict(table=table,steps=60000,path=str(existing.relative_to(ROOT)),sha256=sha(existing),whole_original_trajectory=table!='mean',focus_policy=old.get('focus_policy','ACTUAL_WINDOW_FOCUS')));progress(table,'reused verified same archive');print('REUSE',table,flush=True);continue
  progress(table,'running');log=work/(table+'.log');script='verify_reborn_mean.py'if table=='mean'else'verify_reborn_playtest.py';cmd=['python3',str(ROOT/'tools'/script),'--app',str(app),'--case','primary','--realtime']
  if table!='mean':cmd+=['--table',table]
  if a.controlled_focus and table in ['space','demon']:cmd+=['--controlled-focus']
  print('START',table,'60000 steps / 5 minutes',flush=True)
  with log.open('w')as f:
   process=subprocess.Popen(cmd,stdout=f,stderr=f)
   with (work/(table+'-host-telemetry.jsonl')).open('w')as host:
    while process.poll()is None:
     host.write(json.dumps(telemetry())+'\n');host.flush();time.sleep(5);progress(table,'running')
  if process.returncode:
   progress(table,'FAILED');raise RuntimeError(table+' endurance failed; see '+str(log))
  report=ROOT/f'analysis/traces/reborn-{table}-primary-realtime.json';x=json.loads(report.read_text());assert x['tick_count']==60000 and x['archive_sha256']==archive_sha and x['clamped_frames']==0
  rows.append(dict(table=table,steps=60000,path=str(report.relative_to(ROOT)),sha256=sha(report),whole_original_trajectory=table!='mean',focus_policy=x.get('focus_policy','ACTUAL_WINDOW_FOCUS')));progress(table,'passed');print('PASS',table,flush=True)
 result=dict(status='VERIFIED_BOUNDED_REALTIME',archive_sha256=archive_sha,cases=rows,total_logical_session_steps=240000,minimum_realtime_minutes=20,controlled_focus_requested=a.controlled_focus,scope='Four serialized60000-tick GPU/fullscreen sessions on current host. Retail full source vectors/audio exact; Mean deterministic native trajectory plus separately pinned Original components. No human feel/listening or universal-driver claim.')
 (ROOT/'analysis/traces/reborn-endurance.json').write_text(json.dumps(result,indent=2)+'\n');progress('all','VERIFIED')
if __name__=='__main__':main()
