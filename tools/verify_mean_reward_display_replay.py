#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
reward2='--reward2' in sys.argv
reward3='--reward3' in sys.argv
fixture=json.loads((root/('analysis/traces/mean-reward3-display-original.json' if reward3 else 'analysis/traces/mean-reward2-display-original.json' if reward2 else 'analysis/traces/mean-reward-display-original.json')).read_text())
rows=fixture['states']
actual=[list(map(int,line.split())) for line in subprocess.check_output([sys.argv[1],str(159 if reward2 else 168)],text=True).splitlines()]
keys=['state','active','frame','gate'] + (['service70','service68','slot_request'] if reward3 else [])
assert actual==[[row[k] for k in keys] for row in rows]
print(f'{len(rows)} original reward-display states match')
