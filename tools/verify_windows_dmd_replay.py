#!/usr/bin/env python3
import json,subprocess,sys,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];f=json.loads((root/'analysis/traces/windows-dmd-fixture.json').read_text())
for c in f['cases']:
 actual=subprocess.check_output([sys.argv[1]],input=bytes.fromhex(c['input']))
 assert len(actual)==1920 and hashlib.sha256(actual).hexdigest()==c['expected_sha256']
print('61440 original decoder pixels match')
