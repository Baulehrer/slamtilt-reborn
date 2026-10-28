#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
cases=json.loads((root/'analysis/traces/mean-minigame-input-fixture.json').read_text())['cases']
p=subprocess.run([sys.argv[1]],input=''.join(' '.join(map(str,c['input']))+'\n' for c in cases),text=True,capture_output=True,check=True)
actual=[list(map(int,line.split())) for line in p.stdout.splitlines()]
diff=[i for i,c in enumerate(cases) if i>=len(actual) or actual[i]!=c['expected']]
print(json.dumps({'cases':len(cases),'differences':diff}));raise SystemExit(bool(diff) or len(actual)!=len(cases))
