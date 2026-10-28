#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];dat=next((R/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
a=json.loads(subprocess.check_output([sys.argv[1],str(dat),str(R/'build/mean-prepared'),str(R/'analysis/traces/mean-flight-100.json')],text=True))
assert a[0]['display_ticks']==a[1]['display_ticks'] and a[2]['display_ticks']<a[0]['display_ticks'],a
assert len({(c['score_before'],c['score_after'],c['ball_number']) for c in a})==1,a
assert a[0]['ball_number']==2,a
(R/'analysis/traces/mean-bonus-skip-gameplay.json').write_text(json.dumps(dict(scope='Native natural drain then controlled no/left/both flipper press; identical award and next-ball number, bonus ball frozen; not original full trajectory',cases=a),indent=2)+'\n');print('PASS bonus fast-forward',a)
