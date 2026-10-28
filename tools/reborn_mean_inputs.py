#!/usr/bin/env python3
"""Legal Mean held-plunger/flipper keys, explicit initials confirm and R press/release."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
work=ROOT/'build/reborn-playtest/mean';work.mkdir(parents=True,exist_ok=True)
for seed,n in [(0,60000),(1,4000),(2,4000)]:
 events=[dict(tick=0,action='enter',down=True)];last=[False,False]
 for tick in range(n):
  period=173+seed*17
  for i,(action,down)in enumerate([('left',(tick//period)%2==0),('right',(tick//(period+53))%2==0)]):
   if last[i]!=down:events.append(dict(tick=tick,action=action,down=down));last[i]=down
  if tick>0 and tick%12000==0:
   events.extend([dict(tick=tick-4,action='enter',down=False),dict(tick=tick-3,action='enter',down=True),dict(tick=tick-2,action='enter',down=False),dict(tick=tick,action='new_game',down=True),dict(tick=tick+1,action='new_game',down=False),dict(tick=tick+2,action='enter',down=True)])
 events.sort(key=lambda e:e['tick']);case=['primary','variant-1','variant-2'][seed]
 (work/f'{case}-input.json').write_text(json.dumps(dict(table='mean',case=case,tick_count=n,inputs=events,diagnostic_shots=[],scope='Legal held plunger, periodic left/right flippers; Enter release/confirm/release before explicit R down/up and relaunch. Native regression; full Original scheduler equivalence not claimed.'),indent=2)+'\n')
