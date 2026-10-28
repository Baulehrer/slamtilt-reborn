#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/(sys.argv[2] if len(sys.argv)>2 else 'analysis/traces/mean-lamp-events-original.json')).read_text())
actual=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(data),text=True))
expected=[c['expected'] for c in data['cases']]
differences=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
print(json.dumps(dict(cases=len(expected),differences=differences)))
assert actual==expected
