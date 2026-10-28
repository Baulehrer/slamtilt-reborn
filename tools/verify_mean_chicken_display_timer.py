#!/usr/bin/env python3
"""Bounded original412908 side effects; reuse the existing bitmap-service harness."""
from pathlib import Path
prefix=(Path(__file__).parent/'verify_mean_material5_display.py').read_text().split('specs=')[0]
exec(compile(prefix.replace("required=True", "required=False"), 'existing-dmd-harness', 'exec'))
cases=[]
for timer in [8400,4200,999]:
 for races in [0,1,2]:
  put(0x1002014,0x412908);put(0x100201c,0);put(0x43f050,35684000)
  u.mem_write(0x43f39c,struct.pack('<h',timer));u.mem_write(0x43f3b4,struct.pack('<h',races))
  put(0x43efd0,0x1005000);u.mem_write(0x1005000,bytes(480));u.mem_write(0x1000000,bytes(1920))
  for tick in range(163):
   call(0x412908)
   assert struct.unpack('<h',u.mem_read(0x43f39c,2))[0]==timer,(timer,races,tick,'timer')
   assert struct.unpack('<h',u.mem_read(0x43f3b4,2))[0]==races,(timer,races,tick,'races')
  cases.append({'initial_timer':timer,'initial_races':races,'ticks':163,'final_timer':timer,'final_races':races})
report={'scope':'Actual Original412908 callback through retirement, real bitmap/font/clear/invert services; external lamp/audio adapters and original shared scheduler excluded. No39c/3b4 mutation observed.','image_sha256':hashlib.sha256(image).hexdigest(),'cases':cases,'verified_ticks':1467}
(root/'analysis/traces/mean-chicken-display-timer-original.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS1467 Original Chicken award-DMD ticks preserve timer/race counter')
