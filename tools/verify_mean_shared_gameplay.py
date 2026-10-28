#!/usr/bin/env python3
"""Real native steps at original bitmap switch pixels; synthetic placement only."""
import json,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1]
dat=next((r/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
cmd=[sys.argv[1],str(dat),str(r/'build/mean-prepared'),str(r/'analysis/traces/mean-flight-100.json')]
a=json.loads(subprocess.check_output(cmd));b=json.loads(subprocess.check_output(cmd));assert a==b
assert [row['selected'] for row in a]==[1,2,4]
assert all(e['display']==0x412fa8 for e in a[0]['events'])
assert a[1]['wrong_turn']['display']==0x411824 and a[1]['wrong_turn']['award']==2500000 and a[1]['wrong_turn']['mode']==5
assert [e['display'] for e in a[1]['events']]==[0x411c60]*5+[0x411db4]
assert all(e['display']==0x41041c for e in a[2]['events'])
assert [x['award'] for x in a[0]['events']]==[5000000,12500000,17500000,22500000,25000000,52500000]
assert a[0]['events'][-1]['total']==125000000 and a[0]['events'][-1]['mode']==2
assert [x['award'] for x in a[1]['events']]==[15000000,17500000,17500000,15000000,15000000,136500000]
assert a[1]['events'][-1]['total']==211500000 and a[1]['events'][-1]['mode']==2
assert [x['award'] for x in a[2]['events']]==[17500000,0,17500000,0,17500000]
assert a[2]['events'][-1]['total']==45000000 and a[2]['events'][-1]['mode']==5
assert a[1]['wrong_turn']['pit_punctures']==[1,0,0,0]
assert a[0]['events'][-1]['pit_punctures']==[0,0,0,0] and a[0]['events'][-1]['pit_timer']==1500
assert a[2]['events'][-1]['pit_punctures']==[1,1,1,0]
(r/'analysis/traces/mean-shared-native-chains.json').write_text(json.dumps(dict(scope='Native original mode initialization and six actual switch/capture consumers; explicit synthetic ball placement at free original bitmap pixels, not a captured natural route; original timers advance for six/five ticks; Monster/Offroad/Rally correct, wrong and final events start independently pixel-verified original callbacks; immediate native display scheduling, original queue external; real ramp shots also puncture PitStop tyres for2.5M, duplicates do not puncture twice; fourth starts1500timer without changing main mode',chains=a),indent=2)+'\n')
print('PASS 3 native shared-rule chains / 18 gameplay steps, deterministic')
