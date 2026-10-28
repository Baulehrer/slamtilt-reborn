#!/usr/bin/env python3
"""Long legal Mean session/determinism; complete Original trajectory equivalence unclaimed."""
import argparse,hashlib,json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,separators=(',',':')).encode()).hexdigest()
def world_states(states):return [{k:v for k,v in row.items()if k!='camera_scroll'}for row in states]
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',default='primary');p.add_argument('--app',type=Path);p.add_argument('--realtime',action='store_true');a=p.parse_args();work=ROOT/'build/reborn-playtest/mean';source=work/f'{a.case}-input.json';schedule=read(source);n=schedule['tick_count'];bin=(a.app/'bin'if a.app else ROOT/'build/native')/'slamview';dat=ROOT/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT';out=work/f'{a.case}-{"realtime"if a.realtime else"native"}.json'
 cmd=[bin,dat,'--play',ROOT/'build/mean-prepared','--trace',ROOT/'analysis/traces/mean-flight-100.json','--retail-minigame','--replay',source,'--realtime-steps',str(n),'--trace-output',out]
 if not a.realtime:cmd+=['--frames',str(n//4+1)]
 profile=work/(a.case+'-profile-'+str(time.time_ns()));profile.mkdir();env=dict(os.environ,XDG_DATA_HOME=str(profile));runtime_sha=sha(bin)
 if a.app:env.update(LD_LIBRARY_PATH=str(a.app/'lib'),SLAM_TABLE_PROFILES=str(a.app/'share/slamtilt/table-profiles.json'))
 if not a.realtime:env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
 start=time.monotonic();run=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=n/200+180);assert run.returncode==0,(run.returncode,run.stdout[-800:],run.stderr[-2000:]);t=read(out);assert t['tick_count']==n and not t['failure'],(t['tick_count'],t['failure'])
 expected=[e for e in schedule['inputs']if e['tick']<n];assert t['inputs']==expected
 baseline=work/f'{a.case}-native.json'
 if a.realtime:
  b=read(baseline);assert world_states(t['states'])==world_states(b['states']),'Mean gameplay state mismatch'
  assert t['audio_events']==b['audio_events'],'Mean exact per-step audio request sequence mismatch'
  assert t['clamped_frames']==0,(t['clamped_frames'],t['real_wall_ms'])
 else:
  repeat=work/f'{a.case}-repeat.json';env['XDG_DATA_HOME']=str(profile.with_name(profile.name+'-repeat'));cmd[cmd.index('--trace-output')+1]=repeat;subprocess.run(cmd,check=True,env=env,capture_output=True,text=True,timeout=180);r=read(repeat);assert r['states']==t['states']and r['inputs']==t['inputs']and r['audio_events']==t['audio_events']
 camera=[row['camera_scroll']for row in t['states']];assert all(isinstance(v,int)and 0<=v<=200 for v in camera)
 report=dict(status='VERIFIED_NATIVE_REGRESSION',table='mean',case=a.case,tick_count=n,active_simulation_steps=t.get('active_steps',n),game_over_wait_ticks=t.get('game_over_wait_ticks',0),source_sha256=sha(source),runtime_sha256=runtime_sha,diagnostic_contacts=0,input_events=len(t['inputs']),state_sha256=digest(world_states(t['states'])),camera_sha256=digest(camera),camera_scroll_bounds=[min(camera),max(camera)],camera_original_evidence='analysis/traces/reborn-mean-camera-original.json',audio_requests=len(t['audio_events']),audio_services_sha256=digest([e[1:]for e in t['audio_events']]),whole_original_trajectory_equivalence=False,original_component_evidence='analysis/traces/reborn-mean-components.json',realtime=a.realtime,wall_seconds=time.monotonic()-start,scope='Legal native input session and deterministic replay; complete Original scheduler/contact/rule trajectory equivalence remains PARTIAL. Existing independent Original component evidence retained. Camera scroll is presentation-cadence dependent and separately bounded/proven against Original4086b8. Mean audio request tick/payload ordering is step-accurate and deterministic across rendering cadence; physical playback timing not claimed.')
 if a.realtime:
  report.update(clamped_frames=t['clamped_frames'],real_wall_ms=t['real_wall_ms'],renderer=t['renderer'],video_driver=t['video_driver'],fullscreen=t['fullscreen'],audio_driver=t.get('audio_driver'),archive_sha256=sha(Path(str(a.app)+'.tar.gz'))if a.app else None)
  assert n*5<=t['real_wall_ms']<n*5+15000,t['real_wall_ms']
  assert t['fullscreen']and t['renderer']=='gpu'and t.get('audio_driver')!='none'
 (ROOT/f'analysis/traces/reborn-mean-{a.case}{"-realtime"if a.realtime else""}.json').write_text(json.dumps(report,indent=2)+'\n');print('Mean',a.case,n,'native legal/deterministic PASS',flush=True)
if __name__=='__main__':main()
