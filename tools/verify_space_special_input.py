#!/usr/bin/env python3
"""Actual SDL special keys reproduce Original raw scans and both loop directions."""
import json,os,subprocess
from pathlib import Path
from verify_space_weapons import ROOT,read,KEYS

def main():
 work=ROOT/'build/space-special-input';work.mkdir(exist_ok=True);rows=[]
 game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
 for case,keyname in [('magna-on','Right Ctrl'),('magna-off','Right Shift'),('special-left','Left Ctrl'),('lane-toggle','Left Ctrl'),('lane-double','Left Ctrl'),('lane-live','Left Ctrl')]:
  source=ROOT/f'build/oracle/space-modes/{case}-rewards.json';gold=read(source);schedule=dict(gold);schedule['inputs']=[e for e in gold['inputs']if e.get('scan')not in(0x9d,0x1d)];frozen=work/f'{case}-keys.json';frozen.write_text(json.dumps(schedule))
  raw=[e for e in gold['inputs']if e.get('scan')in(0x9d,0x1d)]if case!='magna-off'else [dict(tick=604,down=True),dict(tick=604,down=False)]
  assert all(e['tick']%4==0 for e in raw)
  events=work/f'{case}-events.json';events.write_text(json.dumps(dict(events=[dict(frame=e['tick']//4,type='key',key=keyname,down=e['down'])for e in raw])))
  out=work/f'{case}-native.json';subprocess.run([ROOT/'build/native/slamslice','space',ROOT/'build/oracle/space-full-game',game/'DAT/SPACE.DAT','--presentation','--frames',str(gold['tick_count']//4),'--replay',frozen,'--diagnostic-shots',source,'--ui-events',events,'--trace',out],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy'))
  actual=read(out)
  if case!='magna-off':
   for k in KEYS:assert actual[k]==gold[k],k
  else:assert all(r[5]==0 and r[3]==65535 for r in actual['weapon_state'][604:])
  rows.append(dict(case=case,physical_key=keyname,original_semantics_match=True,native_reset_includes_physical_events=True))
 (ROOT/'analysis/traces/space-special-input-acceptance.json').write_text(json.dumps(dict(status='VERIFIED',cases=rows),indent=2)+'\n');print(rows)
if __name__=='__main__':main()
