#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
transfer='--transfer' in sys.argv
f=json.loads((root/'analysis/traces'/('mean-mode4-transfer-fixture.json' if transfer else 'mean-mode4-fixture.json')).read_text())
a=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(f['cases']) if transfer else None,text=True))
assert a==f['expected' if transfer else 'states']
print(json.dumps({'verified_states':len(a),'differences':0}))
