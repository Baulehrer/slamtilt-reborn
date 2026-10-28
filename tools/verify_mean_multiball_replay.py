#!/usr/bin/env python3
import json,subprocess,sys,struct
from pathlib import Path
r=Path(__file__).resolve().parents[1];prep=r/'build/mean-prepared'
if '--flight' in sys.argv:
 dat=next((r/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
 a=json.loads(subprocess.check_output([sys.argv[1],str(dat),str(prep),str(r/'analysis/traces/mean-flight-100.json')],text=True))
 b=json.loads((r/'analysis/traces/mean-multiball-flight-original.json').read_text())['states']
 delta=struct.unpack_from('<I',bytes(a[0]),64)[0]-struct.unpack_from('<I',bytes(b[0]),64)[0]
 for y in b:
  data=bytearray(y)
  for offset in [64,68,84]:struct.pack_into('<I',data,offset,(struct.unpack_from('<I',data,offset)[0]+delta)&0xffffffff)
  y[:]=data
 assert a==b
 print(json.dumps({'original_flight_states':len(a),'differences':0,'pointer_relocation_only':delta}));sys.exit(0)
f=json.loads((r/'analysis/traces/mean-multiball-fixture.json').read_text())
a=json.loads(subprocess.check_output([sys.argv[1],str(prep/'pe-data.bin'),str(prep/'lookup.bin')],input=json.dumps(f['cases']),text=True))
assert a==f['expected']
print(json.dumps({'original_cases':len(a),'differences':0}))
