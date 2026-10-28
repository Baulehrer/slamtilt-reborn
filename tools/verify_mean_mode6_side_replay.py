#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
f=json.loads((root/'analysis/traces/mean-mode6-side-fixture.json').read_text())
a=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(f['cases']),text=True))
assert a==f['expected'],next(((i,x,y) for i,(x,y) in enumerate(zip(a,f['expected'])) if x!=y),None)
print(json.dumps(dict(cases=len(a),differences=0)))
