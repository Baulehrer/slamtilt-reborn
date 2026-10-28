#!/usr/bin/env python3
"""Native launch regression; not a substitute for an original live launch trace."""
import json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
command=[str(ROOT/'build/native/mean_sim_probe'),str(ROOT/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT'),str(ROOT/'build/mean-prepared'),str(ROOT/'analysis/traces/mean-flight-100.json'),'2000','launch']
a=json.loads(subprocess.check_output(command,text=True));b=json.loads(subprocess.check_output(command,text=True))
transitions=[]
for sample in a['samples']:
 if not transitions or sample['layer']!=transitions[-1]['layer']:
  transitions.append({k:sample[k] for k in ('step','layer','x','y','state')})
report=dict(method='Native-only deterministic launch regression; component x86 comparisons separate',tick_hz=200,deterministic=a==b,transitions=transitions,launches=a['launches'],events=a['events'],contacts=a['collisions'],states=len(a['samples']),status=a['status'],remaining_blocker=dict(mask=a['field_38'],x=a['final_x'],y=a['final_y']))
(ROOT/'analysis/traces/mean-native-launch-validation.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'analysis/traces/mean-native-launch-slice.json').write_text(json.dumps(a,indent=2)+'\n')
print(json.dumps(report))
assert a==b
assert [t['layer'] for t in transitions[:5]]==[0,1,2,3,0]
assert a['launches']>0 and len(a['samples'])>=800

# Regression for the reported freeze: continue beyond the former step453 stop.
# The later path can return into upper ramps; lower-flipper arrival is not a
# proven expectation for this scripted input sequence.
assert len({(s["x"],s["y"]) for s in a["samples"][453:500]})>=40, "Ball remained frozen at former lower switch4 stop"

# Upper transfer / return ramp must continue to the original drain boundary.
assert len(a["samples"]) >= 1800
assert a["status"].startswith("BALL_DRAIN:")
assert any(s["layer"] == 0 for s in a["samples"][1378:])
