#!/usr/bin/env python3
"""Compare manually clocked original tracker/mixer PCM with four native starts.

Original code runs on SHA-pinned Retail EXE/DAT data. The voice list is rebuilt
from four tracker voices on each manually clocked 50 Hz tick; no game scheduler,
SFX, device timing or complete-song equivalence is claimed. PCM stays private.
"""
import argparse,hashlib,json,math,os,struct,subprocess,sys
from pathlib import Path
from extract_mean_stim import extract
from verify_retail_tracker_pcm import ROOT,GAME,TABLES

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--native',type=Path,required=True)
p.add_argument('--work',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--ticks',type=int,default=256)
p.add_argument('--table',choices=tuple(TABLES),help='Optional single table')
p.add_argument('--order',type=int,help='Override order in the selected table bank')
p.add_argument('--bank-offset',type=lambda v:int(v,0),help='Override the selected table bank DAT offset')
p.add_argument('--require-exact',action='store_true',help='Require sample-exact bounded PCM')
p.add_argument('--min-correlation',type=float,default=0.995,help='Minimum bounded overall correlation')
p.add_argument('--allow-silent',action='store_true',help='Allow silent cases in bounded surveys')
p.add_argument('--library',type=Path,help='Optional explicitly selected shared libxmp')
a=p.parse_args();assert 1<=a.ticks<=2048 and (a.table or (a.order is None and a.bank_offset is None));a.work.mkdir(parents=True,exist_ok=True)
env=dict(os.environ)
if a.library:
 library=a.library.absolute();env['LD_LIBRARY_PATH']=str(library.parent)
 assert str(library) in subprocess.check_output(['ldd',str(a.native.resolve())],env=env,text=True)
rows=[]
for table,(dat_sha,offset,order) in TABLES.items():
 if a.table and table!=a.table:continue
 if a.order is not None:order=a.order
 if a.bank_offset is not None:offset=a.bank_offset
 dat=(GAME/'DAT'/f'{table.upper()}.DAT').read_bytes();assert hashlib.sha256(dat).hexdigest()==dat_sha
 cmd=[sys.executable,str(ROOT/'tools/verify_retail_tracker_pcm.py'),'--table',table,'--ticks',str(a.ticks),'--dynamic-voices','--output',str(a.work)]
 if a.order is not None:cmd+=['--order',str(order)]
 if a.bank_offset is not None:cmd+=['--bank-offset',hex(offset)]
 if a.allow_silent:cmd+=['--allow-silent']
 subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL)
 orig=(a.work/f'{table}-first-tick.s16le').read_bytes(); info=json.loads((a.work/f'{table}-report.json').read_text())
 if a.ticks >= 5 and a.order is None and a.bank_offset is None:
  static_work=a.work/f'{table}-static-five'
  subprocess.run([sys.executable,str(ROOT/'tools/verify_retail_tracker_pcm.py'),'--table',table,'--ticks','5','--output',str(static_work)],check=True,stdout=subprocess.DEVNULL)
  assert orig[:5*882*4]==(static_work/f'{table}-first-tick.s16le').read_bytes(),(table,'initial oracle mismatch')
 bank,_=extract(dat,0,(offset,));path=a.work/f'{table}.stim';path.write_bytes(bank)
 native=subprocess.check_output([str(a.native.resolve()),str(path),str(a.ticks*882),'137','restart',str(order),'retail'],env=env)
 assert len(orig)==len(native)==a.ticks*882*4
 raw_orig=struct.unpack(f'<{a.ticks*1764}h',orig);raw_native=struct.unpack(f'<{a.ticks*1764}h',native)
 assert raw_orig[::2]==raw_orig[1::2] and raw_native[::2]==raw_native[1::2]
 x=raw_orig[::2];y=raw_native[::2]
 windows=[]
 for tick in range(a.ticks):
  q=x[tick*882:(tick+1)*882];r=y[tick*882:(tick+1)*882];aa=sum(i*i for i in q);bb=sum(i*i for i in r)
  if aa and bb: windows.append((tick,sum(i*j for i,j in zip(q,r))/math.sqrt(aa*bb)))
 assert windows or a.allow_silent
 worst=sorted(windows,key=lambda w:w[1])[:5]
 mismatch=[]
 for tick in range(a.ticks):
  q=x[tick*882:(tick+1)*882];r=y[tick*882:(tick+1)*882]
  count=sum(i!=j for i,j in zip(q,r))
  if count:mismatch.append({'tick':tick,'different_frames':count,'max_abs_error':max(abs(i-j) for i,j in zip(q,r))})
 aa=sum(i*i for i in x);bb=sum(i*i for i in y);assert (aa and bb) or a.allow_silent
 corr=round(sum(i*j for i,j in zip(x,y))/math.sqrt(aa*bb),6) if aa and bb else None
 rows.append({'table':table,'bank_offset':hex(offset),'order':order,'ticks':a.ticks,'frames':a.ticks*882,'initial_five_windows_match_previous_oracle':a.ticks>=5 and a.order is None and a.bank_offset is None,'original_sha256':hashlib.sha256(orig).hexdigest(),'native_sha256':hashlib.sha256(native).hexdigest(),'original_blocks':info['executed_original_blocks'],'overall_correlation':corr,'rms_ratio':round(math.sqrt(bb/aa),6) if aa else None,'exact_frames':sum(i==j for i,j in zip(x,y)),'mismatched_windows':len(mismatch),'first_mismatches':mismatch[:10],'worst_windows':[{'tick':k,'correlation':round(c,6)} for k,c in worst]})
 if a.require_exact:assert orig==native,(table,offset,order,mismatch[:3])
 assert corr is None or corr > a.min_correlation, (table,corr)
 print(table,'overall',corr,'worst',rows[-1]['worst_windows'][0] if worst else None,flush=True)
report={'status':'MEASURED_BOUNDED','scope':__doc__,'native_sha256':hashlib.sha256(a.native.read_bytes()).hexdigest(),'library_sha256':hashlib.sha256(library.read_bytes()).hexdigest() if a.library else None,'cases':rows}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
