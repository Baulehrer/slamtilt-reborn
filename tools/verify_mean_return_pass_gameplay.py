#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1];dat=next((r/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
args=[sys.argv[1],str(dat),str(r/'build/mean-prepared'),str(r/'analysis/traces/mean-flight-100.json')]
a=json.loads(subprocess.check_output(args,text=True));b=json.loads(subprocess.check_output(args,text=True));assert a==b
assert [x['selected'] for x in a]==[1,2,3]
(r/'analysis/traces/mean-return-pass-gameplay.json').write_text(json.dumps(dict(scope='Native targeted original layer2 free switch bitmap; three explicit ball placements, actual physics/switch/rules/score/display chain, repeat exact. Not natural gameplay or original whole-table trajectory proof.',rows=a),separators=(',',':'))+'\n')
print('Three native return passes: modes1/2/3,0/5M/15M, original display; repeat exact')
