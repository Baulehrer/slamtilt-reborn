#!/usr/bin/env python3
"""Native phase1 magnet composition, synthetic pose; component oracles separate."""
import json,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1]
dat=next((r/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
cmd=[sys.argv[1],str(dat),str(r/'build/mean-prepared'),str(r/'analysis/traces/mean-flight-100.json'),'1000','point-force','0','summary']
a=json.loads(subprocess.check_output(cmd));b=json.loads(subprocess.check_output(cmd))
assert a==b, 'Non-deterministic magnet composition'
assert a['active'] and a['states']==1001
assert a['point_force_updates']>0, 'Original phase1 magnet never affected ball'
assert a['point_force_type']==0, 'Original phase1 clock/exit failed to disable magnet'
(r/'analysis/traces/mean-point-force-native-cycle.json').write_text(json.dumps(dict(scope='Native phase1 entry via verified41b010 helper; synthetic actual-free-bitmap pose; original type/clock gates; no flipper input; not whole-original gameplay equivalence',result=a),indent=2)+'\n')
print('PASS deterministic1000-step native magnet cycle; velocity updates',a['point_force_updates'])
