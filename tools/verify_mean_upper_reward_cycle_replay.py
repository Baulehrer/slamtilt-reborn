#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
fixture=json.loads((root/'analysis/traces/mean-upper-reward-cycle-original.json').read_text())
for case in fixture['cases']:
 actual=json.loads(subprocess.check_output([sys.argv[1],*(['reward2'] if case['reward']==2 else [])],text=True))
 assert actual==case['states'], f"Reward{case['reward']} callback/display/release replay differs"
print(f"{sum(len(c['states']) for c in fixture['cases'])} original upper reward-cycle states match")
