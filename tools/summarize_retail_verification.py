#!/usr/bin/env python3
"""Summarize locally verified Retail replays; requires private test artifacts."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]; out=root/'docs/verification'; out.mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
 return h.hexdigest()
def read(p): return json.loads(p.read_text())
retail=root/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
exe=sha(retail/'SLAMTILT.EXE')
rows=[]
for table in ('pirate','space','demon'):
 dat=sha(retail/'DAT'/f'{table.upper()}.DAT')
 native=sha(root/'build/native'/('slamview' if table=='pirate' else 'slamslice'))
 for case in ('primary','variant-1','variant-2'):
  report=read(root/f'build/gameplay-verification/{table}/reborn-{table}-{case}.json')
  source=root/f'build/reborn-playtest/{table}/{case}-oracle.json'
  fixture=read(source)
  assert report['status']=='VERIFIED' and not report['differences']
  assert sha(source)==report['source_sha256']
  assert exe==report['build_sha256']==fixture['build_sha256']
  assert dat==report['dat_sha256']==fixture['dat_sha256']
  assert native==report['runtime_sha256']
  assert report['tick_count']==fixture['tick_count']
  rows.append({k:report[k] for k in ('table','case','tick_count','source_sha256','dat_sha256','runtime_sha256','input_events','diagnostic_contacts','audio_requests','vectors','scope')}|{'original_reset_exact':fixture['original_reset_exact']})
mean=read(root/'analysis/traces/mean-retail-natural-integration.json')
assert mean['status']=='VERIFIED' and not mean['differences'] and mean['original_executable_sha256']==exe
assert sha(retail/'DAT/MEAN.DAT')==mean['dat_sha256']
assert sha(root/'build/native/mean_sim_probe')==mean['native_sim_sha256']
assert sha(root/'build/native/mean_probe')==mean['native_integrator_sha256']
summary={'status':'PARTIAL','whole_game_equivalence':False,'original_build_sha256':exe,'replay_scope':'Saved original initialized contexts; legal observed-state keyboard schedules; state vectors and audio service requests, not final PCM, original video raster or human play. Exact reset status is specified per case.','replays':rows,'mean_integration':{k:mean[k] for k in ('status','original_entry','dat_sha256','native_sim_sha256','native_integrator_sha256','lookup_sha256','input_trace_sha256','cases','skipped','compared','scope','whole_trajectory_equivalence','source_context')},'unverified':['complete natural original Mean trajectory','other unvisited gameplay and minigame branches','final mixed audio, music sequencing, event-to-device timing and physical listening','whole original video raster','Amiga gameplay equivalence']}
minigame = read(root/'build/gameplay-verification/mean-retail-minigame.json')
assert minigame['dat_sha256'] == mean['dat_sha256']
cases = minigame['builds']
assert len(cases) == 4
for row in cases:
 assert (row['ticks'], row['points']) == ((2455, 120000000) if row['scenario'] == 'win' else (1189, 40000000))
 if row['build'] == 'retail': assert row['build_sha256'] == exe
summary['historical_startup_audio_correction'] = ('These original fixture comparisons seeded their first audio request from incomplete zeroed snapshot globals. Retail initialization independently establishes Pirate order 34, Space 32 and Demon 25; see retail-music-start-2026-10-30.json. Earlier audio-request exactness does not establish the actual startup selection.')
summary['mean_minigame'] = {'scope': minigame['scope'], 'dat_sha256': minigame['dat_sha256'],
 'cases': [{k: row[k] for k in ('build', 'scenario', 'build_sha256', 'instructions', 'ticks', 'points', 'callback', 'trace_sha256')} for row in cases]}
(out/'windows-retail-2026-10-30.json').write_text(json.dumps(summary,indent=2)+'\n')
for src,name in [('analysis/traces/space-post-jackpot-original.json','space-post-jackpot-2026-10-30.json'),('analysis/traces/demon-video-consecutive-acceptance.json','demon-video-consecutive-2026-10-30.json'),('build/retail-sample-pcm/report.json','retail-sample-pcm-2026-10-30.json')]:
 data=read(root/src); assert data.get('status') in ('PASS','VERIFIED_BOUNDED'); assert data.get('original_build_sha256',data.get('build_sha256'))==exe
 (out/name).write_text(json.dumps(data,indent=2)+'\n')
print('Verified',len(rows),'replays,',sum(r['tick_count'] for r in rows),'ticks; reset flags:',[(r['table'],r['case'],r['original_reset_exact']) for r in rows])
