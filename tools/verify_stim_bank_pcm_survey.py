#!/usr/bin/env python3
"""Survey bounded Original/native PCM at sampled orders of all ten banks.

Runs manually clocked tracker/mixer scenarios from explicit bank/order
boundaries. The game scheduler, effect events and device output are not fully
modeled. Failed or non-identical cases remain in the report rather than being
classified as matching. Original game data stays in the private work directory.
"""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from extract_mean_stim import extract,BANK_OFFSETS
from verify_retail_tracker_pcm import ROOT,GAME,TABLES,EXE_SHA

BANKS={'mean':BANK_OFFSETS,'pirate':(0x51876,0x568e8),'space':(0x53642,0x5b8e0,0x5fef8),'demon':(0x6ffb4,0x6b2bc,0x6e2ce)}
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--native',type=Path,required=True);p.add_argument('--library',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--ticks',type=int,default=128);p.add_argument('--all-orders',action='store_true');p.add_argument('--require-exact',action='store_true',help='Fail if any case differs or cannot be evaluated');a=p.parse_args();assert 1<=a.ticks<=2048;a.work.mkdir(parents=True,exist_ok=True)
library_sha=hashlib.sha256(a.library.read_bytes()).hexdigest()
native_sha=hashlib.sha256(a.native.read_bytes()).hexdigest()
cases=[]
for table,offsets in BANKS.items():
 dat=(GAME/'DAT'/f'{table.upper()}.DAT').read_bytes();assert hashlib.sha256(dat).hexdigest()==TABLES[table][0]
 for bank,offset in enumerate(offsets):
  _,meta=extract(dat,0,(offset,));length=meta['orders']
  for order in (range(length) if a.all_orders else sorted({0,length//2,length-1})):
   work=a.work/f'{table}-{bank}-{order}';out=work/'report.json'
   cmd=[sys.executable,str(ROOT/'tools/verify_stim_dynamic_pcm.py'),'--native',str(a.native.resolve()),'--library',str(a.library.absolute()),'--table',table,'--order',str(order),'--bank-offset',hex(offset),'--ticks',str(a.ticks),'--min-correlation','-1.1','--allow-silent','--work',str(work),'--output',str(out)]
   proc=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
   if hashlib.sha256(a.library.read_bytes()).hexdigest()!=library_sha or hashlib.sha256(a.native.read_bytes()).hexdigest()!=native_sha:
    raise RuntimeError('Probe or library changed during survey; results would be ambiguous')
   if proc.returncode:
    row={'table':table,'bank':bank,'order':order,'status':'UNRESOLVED','error_tail':proc.stderr[-3000:]}
   else:
    result=json.loads(out.read_text())['cases'][0]
    row={'table':table,'bank':bank,'order':order,'status':'EXACT' if result['exact_frames']==result['frames'] else 'DIFFERENT','exact_frames':result['exact_frames'],'frames':result['frames'],'overall_correlation':result['overall_correlation'],'mismatched_windows':result['mismatched_windows'],'first_mismatches':result['first_mismatches'][:3]}
   cases.append(row);print(table,bank,order,row['status'],flush=True)
report={'status':'MEASURED_BOUNDED','scope':__doc__,'exe_sha256':EXE_SHA,
        'dat_sha256':{table:details[0] for table,details in TABLES.items()},
        'library_sha256':library_sha,'native_sha256':native_sha,'ticks_per_case':a.ticks,'cases':cases}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
if a.require_exact and any(row['status'] != 'EXACT' for row in cases):
 raise SystemExit('Some cases differ or could not be evaluated; see report')
