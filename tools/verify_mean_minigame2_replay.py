#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1];d=json.loads((r/'analysis/traces/mean-minigame2-original.json').read_text());dat=next((r/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'));cache=r/'build/mean-minigame2-prepared'
for c in d['cases']:
 actual=json.loads(subprocess.check_output([sys.argv[1],str(cache/'image.bin'),str(cache/'runtime.bin'),str(dat),str(c['seed']),'2500',str(c['threshold_1f6'])]))
 assert actual==c['states'],(c['seed'],c['threshold_1f6'])
print('PASS',sum(len(c['states']) for c in d['cases']),'original second-minigame states')
