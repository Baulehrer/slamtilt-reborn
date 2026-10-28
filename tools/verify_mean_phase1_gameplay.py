#!/usr/bin/env python3
"""Native phase1 chain with real bitmap switches and explicit synthetic placement."""
import json,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1]
dat=next((r/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
cmd=[sys.argv[1],str(dat),str(r/'build/mean-prepared'),str(r/'analysis/traces/mean-flight-100.json')]
a=json.loads(subprocess.check_output(cmd));b=json.loads(subprocess.check_output(cmd))
assert a==b
assert [x['award'] for x in a['states']]==[25000000,35000000,60000000]
assert a['gate_open'] and a['armed'] and a['point_force_updates']>0
(r/'analysis/traces/mean-phase1-native-chain.json').write_text(json.dumps(dict(scope='Native verified entry; synthetic free layer2 magnet pose; actual200Hz clock and right-input edge; explicit synthetic placements at actual bitmap top/top/exit switch pixels; not an autonomous original trajectory',result=a),indent=2)+'\n')
print('PASS native magnet→release→25M→10M→25M→mode2; armed gate preserved')
