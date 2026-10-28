#!/usr/bin/env python3
"""Run Original integration on untouched ball records from fresh legal native routes.

This compares the component transformation, not complete Original trajectories.
No contact/point-force/dispatch context is invented or claimed.
"""
import argparse,hashlib,json,struct,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP,UC_X86_REG_EIP
R=Path(__file__).resolve().parents[1]
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--native-sim',type=Path,default=R/'build/native/mean_sim_probe')
 parser.add_argument('--native-integrator',type=Path,default=R/'build/native/mean_probe')
 parser.add_argument('--output',type=Path,default=R/'analysis/traces/mean-natural-component-original.json')
 args=parser.parse_args()
 dat=next((R/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
 prep=R/'build/mean-prepared';flight=R/'analysis/traces/mean-flight-100.json'
 image=(prep/'pe-data.bin').read_bytes()
 u=Uc(UC_ARCH_X86,UC_MODE_32)
 for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000)]:u.mem_map(a,n)
 u.mem_write(0x400000,image)
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 # Same explicit no-point-force/debug-overrides domain as component oracle.
 for a,v in [(0x4298c8,0x1000000),(0x43d860,0),(0x43d864,0),(0x4298a4,0)]:put(a,v)
 cases=[];expected=[];contexts=[];skipped=[]
 for seed in [0,1,2]:
  for tick in [100,250,500,750,1000,1250,1500,1750,2000,2500,3000,4000]:
   command=[str(args.native_sim),str(dat),str(prep),str(flight),str(tick),'finite',str(seed),'summary','periodic-no-bonus']
   result=json.loads(subprocess.check_output(command,text=True))
   ball=struct.pack('<25I',*result['final_raw_words'])
   state=struct.unpack_from('<H',ball,0x58)[0]
   if state!=2 or result['point_force_type']!=0 or result['bonus_phase']!=0:
    skipped.append(dict(seed=seed,tick=tick,state=state,point_force_type=result['point_force_type'],bonus_phase=result['bonus_phase']));continue
   context=dict(seed=seed,tick=tick,ball=list(ball),input_fnv=result['input_fnv'],ball_number=result['ball_number'],table_mode=result['table_mode'],collisions_so_far=result['collisions'],x=result['final_x'],y=result['final_y'])
   contexts.append(context);cases.append(dict(operation='integrate',bytes=list(ball)))
   u.mem_write(0x1000000,ball);put(0x200f000,0x200fff0)
   u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0)
   u.emu_start(0x40a010,0x200fff0,count=10000)
   assert u.reg_read(UC_X86_REG_EIP)==0x200fff0
   expected.append(list(u.mem_read(0x1000000,100)))
 path=R/'build/oracle/mean-natural-component-cases.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(cases))
 actual=json.loads(subprocess.check_output([str(args.native_integrator),str(path),str(prep/'lookup.bin')],text=True))
 assert len(actual)==len(expected) and cases
 differences=[dict(index=i,byte_offsets=[j for j in range(100) if a[j]!=b[j]]) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
 report=dict(schema_version=1,status='VERIFIED' if not differences else 'DIFFERENCE',original_entry='0x40a010',image_sha256=hashlib.sha256(image).hexdigest(),dat_sha256=hashlib.sha256(dat.read_bytes()).hexdigest(),input='Fresh reset; finite route; seed0/1/2; legal periodic flippers and held launch; no debug placement/state injection; snapshots at selectedticks',cases=len(cases),contexts=contexts,skipped=skipped,differences=differences,compared='All100 ball bytes after actual Original integration vs existing native mean_integrate',scope='Natural-input-derived ball state, bounded component execution. No point force/debug override; no contact/scheduler/table dispatch comparison.',whole_trajectory_equivalence=False,missing_full_contact_context=['per-step actual flipper poses/flags','engine globals including nudge offsets and active point-force nodes','table/raw material and rule state at pre-contact boundary','exact ball index and other active balls before separation'])
 out=args.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(status=report['status'],cases=len(cases),skipped=len(skipped),differences=differences)))
 assert not differences
if __name__=='__main__':main()
