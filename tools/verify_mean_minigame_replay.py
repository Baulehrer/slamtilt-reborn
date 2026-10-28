#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];prepared=root/'build/mean-minigame-prepared';dat=next((root/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
if '--terminal' in sys.argv:
 f=json.loads((root/'analysis/traces/mean-minigame-terminal-fixture.json').read_text())
 actual=json.loads(subprocess.check_output([sys.argv[1],str(prepared/'image.bin'),str(prepared/'runtime.bin'),str(dat)],input=json.dumps(f['cases']),text=True))
 assert actual==f['expected']
 print(json.dumps(dict(terminal_cases=len(actual),differences=0)));sys.exit(0)
f=json.loads((root/'analysis/traces/mean-minigame-fixture.json').read_text())
for c in f['cases']:
 actual=json.loads(subprocess.check_output([sys.argv[1],str(prepared/'image.bin'),str(prepared/'runtime.bin'),str(dat),str(c['seed']),'2000'],text=True))
 assert actual==c['states'],f"Original mini-game differs for seed{c['seed']}"
print(json.dumps(dict(original_states=sum(len(c['states']) for c in f['cases']),differences=0)))
