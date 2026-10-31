#!/usr/bin/env python3
"""Watch descriptor writes during bounded Original Space event replays.

Audio consumption is not scheduled by these replays, and the contact scenarios
use diagnostic shots. This checks writes in the executed gameplay, not all paths.
"""
import argparse, hashlib, json, runpy, sys
from pathlib import Path
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.x86_const import UC_X86_REG_EIP
from pirate_adventure_oracle import Original
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--native',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
profiles=json.loads((ROOT/'analysis/space-audio-reuse.json').read_text())['sample_profiles']; descriptors=[int(x['descriptor'],0) for x in profiles]
changes=[];controls=[];initial=Original.__init__
def instrument(self,*args,**kwargs):
 initial(self,*args,**kwargs)
 def watch(u,access,addr,size,value,data):
  for d in descriptors:
   if addr<d+12 and addr+size>d+4:changes.append({'pc':hex(u.reg_read(UC_X86_REG_EIP)),'address':hex(addr),'size':size,'value':value})
   if addr<d+36 and addr+size>d+24:controls.append({'pc':hex(u.reg_read(UC_X86_REG_EIP)),'address':hex(addr)})
 self.u.hook_add(UC_HOOK_MEM_WRITE,watch,begin=min(descriptors),end=max(descriptors)+35)
Original.__init__=instrument
prior=sys.argv;target=ROOT/'tools/verify_space_sfx_descriptor_state.py';scratch=a.output.with_name(a.output.stem+'-replay.json')
try:
 sys.argv=[str(target),'--native',str(a.native),'--output',str(scratch)];runpy.run_path(str(target),run_name='__main__')
finally:sys.argv=prior;Original.__init__=initial
replay=json.loads(scratch.read_text());assert controls, 'write hook did not observe queue writes';assert not changes,changes
report={'status':'VERIFIED_BOUNDED','scope':__doc__,'replay_report_sha256':hashlib.sha256(scratch.read_bytes()).hexdigest(),'exe_sha256':replay['original_exe_sha256'],'dat_sha256':replay['dat_sha256'],'ticks':replay['ticks'],'events':replay['events'],'cases':len(replay['cases']),'descriptor_count':len(descriptors),'period_volume_writes':changes,'positive_queue_write_count':len(controls),'positive_queue_writes':controls[:4]}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print('PASS: no descriptor period/volume writes;',len(controls),'positive queue writes')
