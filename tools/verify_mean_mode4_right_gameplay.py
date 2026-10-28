#!/usr/bin/env python3
"""Native right-mode4 composition; component oracles establish original boundaries."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
dat=next((root/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
def run(scenario,seed):
 return json.loads(subprocess.check_output([sys.argv[1],str(dat),str(root/'build/mean-prepared'),str(root/'analysis/traces/mean-flight-100.json'),'12000',scenario,str(seed),'summary']))
rows=[]
for scenario in ['mode4-right','minigame2','right-route']:
 for seed in range(4):
  a=run(scenario,seed)
  assert a['active'] and a['states']==12001,(scenario,seed,a['status'])
  assert a['mode4_starts']>=1 and a['mode4_completions']>=1,(scenario,seed)
  if scenario in ['minigame2','right-route']:assert a['minigame_starts']>=1 and a['minigame_completions']>=1
  if scenario=='right-route':assert a['right_markers']>=1 and a['right_captures']>=1
  rows.append(dict(scenario=scenario,seed=seed,**{k:a[k] for k in ['states','mode4_starts','mode4_completions','minigame_starts','minigame_completions','releases','score','right_markers','right_captures','right_arms']}))
 assert run(scenario,0)==run(scenario,0),'Non-deterministic composition'
(root/'analysis/traces/mean-mode4-right-native-cycle.json').write_text(json.dumps(dict(scope='Native-only direct bounded entry setup plus synthetic flipper input; right-route uses verified progress then actual bitmap switch/marker20; no original whole-trajectory proof',cases=rows),indent=2)+'\n')
print('PASS twelve12000-step right-entry/return cycles; deterministic repeats')

negative=json.loads(subprocess.check_output([sys.argv[1],str(dat),str(root/'build/mean-prepared'),str(root/'analysis/traces/mean-flight-100.json'),'2','right-empty','0','summary']))
assert negative['active'] and negative['right_captures']==0 and negative['minigame_starts']==0, 'Capture bypassed actualmask3 switch gate'
print('PASS x>=260/marker20 withoutswitch3 doesnotcapture')

cancel=json.loads(subprocess.check_output([sys.argv[1],str(dat),str(root/'build/mean-prepared'),str(root/'analysis/traces/mean-flight-100.json'),'2','right-cancel','0','summary']))
assert cancel['active'] and cancel['right_cancellations']==1 and not cancel['right_route_armed'], 'Upper ramp return failed to cancel armed route'
assert cancel['layer']==0 and cancel['right_captures']==0
(root/'analysis/traces/mean-right-cancel-native.json').write_text(json.dumps(dict(scope='Native original bitmap switch, synthetic armed-route and pose setup',result=cancel),indent=2)+'\n')
print('PASS actual upper-return switch cancels armed route once')
