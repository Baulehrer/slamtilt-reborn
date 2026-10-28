#!/usr/bin/env python3
"""Unmodified native start + diagnostic keys only. Not original/live trajectory proof."""
import concurrent.futures,json,subprocess,sys,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];dat=next((R/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
base=[sys.argv[1],str(dat),str(R/'build/mean-prepared'),str(R/'analysis/traces/mean-flight-100.json')]
def run(seed,steps=400000):
 j=json.loads(subprocess.check_output(base+[str(steps),'cycle',str(seed),'advanced-trace','random'],text=True));j.pop('samples',None)
 assert j['active'] and j['bonus_ball_frozen'],(seed,j['status'])
 events=j['advanced_events']
 if seed in [27,34]:
  assert j['minigame_starts']==j['minigame_completions']==1,seed
  entry=next(e for e in events if e['counters'][2]);done=next(e for e in events if e['counters'][3])
  assert entry['display'][0]==0 and entry['display'][2:]==[0,0,-1,0,1],entry['display']
  assert done['display']==[0x40f994,0,4,2,7,0x40f994,0],done['display']
  assert any(e['step']>done['step'] and e['display'][0]!=0x40f994 and e['display'][-1]==0 for e in events), 'Result owner did not retire after completion'
  assert entry['selected']==3 and done['selected']==4 and done['step']>entry['step']
  assert done['counters'][6]==entry['counters'][6]
  assert any(e['step']>done['step'] and e['counters'][1]>done['counters'][1] for e in events)
 else:
  assert j['minigame_starts']==j['multiball_spawns']==0,seed
 if steps>400000:
  assert j['multiball_spawns']==7 and j['max_balls']==8 and j['ball_count']==1 and j['mode_resets']>=1
  eight=next(e for e in events if e['count']==8)
  assert eight['mode']==6 and eight['counters'][4]==7 and eight['counters'][5]>=1
  assert any(e['step']>eight['step'] and e['count']==1 and e['mode']==2 for e in events)
 return dict(seed=seed,ticks=steps,**j)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:cases=list(p.map(run,[13,16,27,34]))
for seed in [13,27]:assert run(seed)==next(c for c in cases if c['seed']==seed),'Non-deterministic native event chain'
# The old endless seed27 no longer reaches SPEED after proven rule fixes.
# Keep all four strict random controls; use the independently proven finite
# legal-input SPEED route for the stronger eightball/return/lifecycle contract.
speed_probe=Path(sys.argv[2]) if len(sys.argv)>2 else R/'build/native/mean_speed_finite'
speed_report=R/'analysis/traces/mean-natural-advanced-speed-finite.json'
subprocess.run([str(speed_probe),str(dat),str(R/'build/mean-prepared'),str(R/'analysis/traces/mean-flight-100.json'),str(R/'analysis/traces/mean-speed-natural-input.json'),str(speed_report)],check=True)
speed=json.loads(speed_report.read_text())
assert len(speed['cases'])==2 and speed['cases'][0]==speed['cases'][1]
for c in speed['cases']:
 events=[e for e in c['events'] if 'state' in e]
 eight=next(e for e in events if e['state']['count']==8)
 assert eight['state']['mode']==6 and eight['state']['spawns']==7 and eight['state']['starts']>=1
 assert any(e['tick']>eight['tick'] and e['state']['count']==1 and e['state']['mode']==2 for e in events)
 assert max(e['state']['spawns'] for e in events)==7 and max(e['state']['count'] for e in events)==8
 assert c['final_tick']==40380 and c['final_score']==482716240
report=dict(schedule_revision='Four random mini/negative controls unchanged. Stale1.8M seed27 SPEED expectation replaced by existing stricter finite legal-input route, two fresh replays, original eightball/return assertions retained.',scope='Native diagnostic ordinary reset;400000steps per random seed, deterministic legal actions. Separate finite SPEED RLE proves seven spawns/eightball/singleball-mode2 return and GameOver/reset. No Original whole-table trajectory claim.',speed_finite=speed,mean_dat_sha256=hashlib.sha256(dat.read_bytes()).hexdigest(),prepared_sha256=hashlib.sha256((R/'build/mean-prepared/pe-data.bin').read_bytes()).hexdigest(),cases=cases)
(R/'analysis/traces/mean-natural-advanced-gameplay.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
print('PASS four unforced advanced-mode chains; repeats13/27 exact;',[(c['seed'],c['minigame_starts'],c['multiball_spawns'],c['max_balls']) for c in cases])
