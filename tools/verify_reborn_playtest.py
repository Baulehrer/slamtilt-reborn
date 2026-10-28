#!/usr/bin/env python3
"""Compare a fresh legal Original schedule against native packaged/runtime execution."""
import argparse,gc,hashlib,json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PREP={'pirate':'pirate-complete-game-lamps-ready','space':'space-full-game','demon':'demon-full-game'}
def read(p):return json.loads(p.read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,separators=(',',':')).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--table',choices=PREP,required=True);p.add_argument('--case',default='primary');p.add_argument('--app',type=Path);p.add_argument('--realtime',action='store_true');p.add_argument('--controlled-focus',action='store_true');p.add_argument('--sdl-stall-probe',type=Path);a=p.parse_args();table=a.table;work=ROOT/f'build/reborn-playtest/{table}';source=work/f'{a.case}-oracle.json';baseline=ROOT/f'analysis/traces/reborn-{table}-{a.case}.json'
 if baseline.exists():
  meta=read(baseline);assert meta['source_sha256']==sha(source)and meta['diagnostic_contacts']==0;steps=meta['tick_count']
 else:
  assert not a.realtime,'Generate accelerated comparison before real-time acceptance'
  initial=read(source);steps=initial['tick_count'];assert not initial['diagnostic_shots'];del initial;gc.collect()
 binary=(a.app/'bin'if a.app else ROOT/'build/native')/('slamview'if table=='pirate'else'slamslice');prepared=ROOT/'build/oracle'/PREP[table];dat=ROOT/f'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/{table.upper()}.DAT';trace=work/f'{a.case}-{"realtime"if a.realtime else"native"}.json';audio=trace.with_name(trace.stem+'-audio.json')
 cmd=[binary,dat,'--pirate-play',prepared,'--full-state-trace','--trace-output',trace]if table=='pirate'else[binary,table,prepared,dat,'--trace',trace,'--presentation','--replay-only']
 cmd+=['--replay',source,'--audio-trace',audio]
 if table=='pirate':cmd+=['--replay-only']
 if a.realtime:
  cmd+=['--realtime-steps',str(steps),'--fullscreen']
  if table=='pirate':cmd+=['--timing-output',trace.with_name(trace.stem+'-timing.json')]
 else:cmd+=['--frames',str(steps//4)]
 if a.controlled_focus:
  assert a.realtime and table in ['space','demon'],'Controlled UI focus currently supported by Retail slice adapter'
  focus=work/'controlled-focus-events.json';focus.write_text(json.dumps(dict(events=[dict(frame=i,type='focus_gained')for i in range(100000)])))
  cmd+=['--ui-events',focus]
 if table!='pirate':cmd+=['--audio']
 env=dict(os.environ,XDG_DATA_HOME=str(work/f'{a.case}-prefs'))
 if a.app:env.update(LD_LIBRARY_PATH=str(a.app/'lib'),SLAM_TABLE_PROFILES=str(a.app/'share/slamtilt/table-profiles.json'))
 if a.sdl_stall_probe:env['LD_PRELOAD']=str(a.sdl_stall_probe.resolve(strict=True))
 if not a.realtime:env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
 runtime_sha=sha(binary);start=time.monotonic();run=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=steps/200+180)
 trace.with_suffix('.stderr.log').write_text(run.stderr)
 if run.returncode:raise AssertionError((run.returncode,run.stdout[-600:],run.stderr[-2000:]))
 g=read(source);assert not g['diagnostic_shots']
 t=read(trace);sound=read(audio);keys=['states','lifecycle','highscore_sha256','lamp_sha256','ball_pool_sha256']+(['timing','dmd_sha256','rule_sha256','video_sha256']if table=='pirate'else['poses','globals']+(['raw_state_sha256']if table=='demon'else[]));differences=[]
 assert t['tick_count']==steps
 for k in keys:
  if t[k]!=g[k]:
   i=next((i for i,(x,y)in enumerate(zip(t[k],g[k]))if x!=y),min(len(t[k]),len(g[k])));differences.append(dict(vector=k,index=i,expected=g[k][max(0,i-1):i+2],actual=t[k][max(0,i-1):i+2]))
 if sound['events']!=g['audio_events']:differences.append(dict(vector='audio_events',expected=g['audio_events'][:6],actual=sound['events'][:6]))
 report=dict(status='DIFFERENCE'if differences else'VERIFIED',table=table,case=a.case,tick_count=steps,source_sha256=sha(source),build_sha256=g['build_sha256'],dat_sha256=g['dat_sha256'],runtime_sha256=runtime_sha,input_sha256=digest(g['inputs']),input_events=len(g['inputs']),diagnostic_contacts=0,vectors=keys,audio_requests=len(sound['events']),audio_enabled=sound['enabled'],audio_queued_bytes=sound['queued_bytes'],realtime=a.realtime,wall_seconds=time.monotonic()-start,sequence_sha256={k:digest(t[k])for k in keys},differences=differences,oracle_loaded_after_gameplay=True,focus_policy='CONTROLLED_TEST_EVENTS'if a.controlled_focus else'ACTUAL_WINDOW_FOCUS',scope='Frozen observed-state legal keys against actual Original instructions; exact per-step arrays and canonical audio requests. No physical hearing/input or whole-raster claim.')
 if a.realtime:
  if table=='pirate':
   timing=read(trace.with_name(trace.stem+'-timing.json'));columns=timing['frame_columns'];at={name:i for i,name in enumerate(columns)};frame_rows=timing['frames'];clamps=sum(r[at['advancing']]and r[at['raw_elapsed_ns']]>100000000 for r in frame_rows);wall_ms=(frame_rows[-1][at['elapsed_ns']]+frame_rows[-1][at['frame_work_ns']])/1e6
   report.update(clamped_frames=clamps,real_wall_ms=wall_ms,renderer=timing['renderer'],video_driver=timing['video'],fullscreen=timing['fullscreen'])
  else:report.update(clamped_frames=t['clamped_frames'],real_wall_ms=t['real_wall_ms'],renderer=t['renderer'],video_driver=t['video_driver'],fullscreen=t['fullscreen'])
  if a.sdl_stall_probe:
   report['sdl_stall_probe_sha256']=sha(a.sdl_stall_probe)
   report['scope']+=' QA-only LD_PRELOAD measures blocking SDL calls; packaged executable and assets are unchanged.'
  trace.with_name(trace.stem+'-measurement.json').write_text(json.dumps(report,indent=2)+'\n')
  assert report['clamped_frames']==0,(report['clamped_frames'],report['real_wall_ms'])
  assert steps*5<=report['real_wall_ms']<steps*5+15000,report['real_wall_ms']
  assert report['fullscreen']and report['renderer']=='gpu'
  report['archive_sha256']=sha(Path(str(a.app)+'.tar.gz'))if a.app else None
  report['scope']+=' Realtime timing acceptance separately bounded by available frontend fields.'
  if a.controlled_focus:report['scope']+=' Synthetic focus-gain events keep only this benchmark advancing in background; actual interactive focus/audio lifecycle is separately tested in reborn-focus.json.'
 out=ROOT/f'analysis/traces/reborn-{table}-{a.case}{"-realtime"if a.realtime else""}.json';out.write_text(json.dumps(report,indent=2)+'\n')
 assert not differences,(table,a.case,[(d['vector'],d.get('index'))for d in differences]);assert sound['enabled']and sound['queued_bytes']>0
 print(table,a.case,steps,'Original/native/audio exact',flush=True)
if __name__=='__main__':main()
