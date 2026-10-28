#!/usr/bin/env python3
"""Native finite-game input diversity; no original trajectory equivalence."""
import concurrent.futures,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
dat=next((R/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
base=[sys.argv[1],str(dat),str(R/'build/mean-prepared'),str(R/'analysis/traces/mean-flight-100.json')]
specs=[(p,s) for p,n in [('periodic',36),('random',32),('held',8),('passive',8),('alternating',16)] for s in range(n)]
def run(c):
 profile,seed=c
 j=json.loads(subprocess.check_output(base+['200000','finite',str(seed),'summary',profile],text=True));j.pop('samples',None)
 assert j['game_over'] and not j['active'],(c,j['status'],j['states'])
 assert j['game_over_frozen'] and j['new_game_restored'],c
 assert j['ball_count']==0 and j['table_mode']==0,c
 assert j['bonus_starts']==j['bonus_completions']==j['bonus_awards']>=3,c
 assert j['bonus_ball_frozen'] and j['bonus_frozen_steps']>0,c
 return dict(seed=seed,**j)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:cases=list(pool.map(run,specs))
for profile in ['periodic','random','held','passive','alternating']:
 assert run((profile,0))==next(c for c in cases if c['input_profile']==profile and c['seed']==0)
report=dict(scope='100 native complete finite games, Full lifecycle policy and Demo physics, five synthetic input profiles; repeat seed0 for each; no captured original trajectories',cases=cases,total_steps=sum(c['states'] for c in cases))
(R/'analysis/traces/mean-finite-input-coverage.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
print('PASS',len(cases),'finite games;',report['total_steps'],'steps; five deterministic repeats')
# Separate synthetic mode4 upper entry at an actual original free bitmap pixel.
def upper(seed,steps,summary=True):
 return json.loads(subprocess.check_output(base+[str(steps),'mode4-upper',str(seed)]+(['summary'] if summary else []),text=True))
cycles=[upper(seed,12000) for seed in range(4)]
for c in cycles:assert c['active'] and c['states']==12001 and c['upper_captures']>=1 and c['releases']>=1,(c['status'],c['states'])
assert upper(0,12000)==cycles[0]
trace=upper(0,180,False);samples=trace['samples']
assert samples[1]['state']==3 and samples[1]['x']==14*65536 and samples[1]['y']==14*65536
held=[s for s in samples if s['state']==3]
assert len(held)==152,len(held)
assert any(s['state']==2 and s['step']>1 for s in samples)
assert trace['score']==500000,trace['score']
(R/'analysis/traces/mean-mode4-upper-gameplay.json').write_text(json.dumps(dict(scope='Synthetic original phase1 initializer and actual upper bitmap pixel;152 held native steps, award/release and12000-step continuation; no natural route or original complete trajectory proof',cycles=[{k:c[k] for k in ['states','status','upper_captures','releases','score','mode4_starts','mode4_completions','table_mode']} for c in cycles],entry_release=samples),separators=(',',':'))+'\n')
print('PASS mode4 upper bitmap capture / 152 held steps / award / release / four12000-step continuations')
