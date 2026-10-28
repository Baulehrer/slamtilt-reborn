#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,sys
r=Path(__file__).resolve().parents[1];d=next((r/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
a=[sys.argv[1],str(d),str(r/'build/mean-prepared'),str(r/'analysis/traces/mean-flight-100.json')]
x=json.loads(subprocess.check_output(a,text=True));assert json.loads(subprocess.check_output(a,text=True))==x
(r/'analysis/traces/mean-minigame2-player-gameplay.json').write_text(json.dumps(dict(scope='Original initialized8000 player record, synthetic actual rightcapture bitmap pose; native alternating flipper edges, second minigame completion, saved-record/nextball reset and newgame default restoration; not a natural rightentry or full original trajectory proof',cases=x),separators=(',',':'))+'\n')
print('Native second-minigame8000 completion/7600 persistence/newgame8000 exact repeat',x)
