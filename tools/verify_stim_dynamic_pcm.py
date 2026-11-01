#!/usr/bin/env python3
"""Compare manually clocked original tracker/mixer PCM with four native starts.

Original code runs on SHA-pinned Retail EXE/DAT data. The voice list is rebuilt
from four tracker voices on each manually clocked 50 Hz tick; no game scheduler,
SFX, device timing or complete-song equivalence is claimed. PCM stays private.
"""
import argparse,hashlib,json,math,struct,subprocess,sys
from pathlib import Path
from extract_mean_stim import extract
from verify_retail_tracker_pcm import ROOT,GAME,TABLES

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--native',type=Path,required=True)
p.add_argument('--work',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--ticks',type=int,default=256)
a=p.parse_args();assert 1<=a.ticks<=512;a.work.mkdir(parents=True,exist_ok=True)
rows=[]
for table,(dat_sha,offset,order) in TABLES.items():
 dat=(GAME/'DAT'/f'{table.upper()}.DAT').read_bytes();assert hashlib.sha256(dat).hexdigest()==dat_sha
 subprocess.run([sys.executable,str(ROOT/'tools/verify_retail_tracker_pcm.py'),'--table',table,'--ticks',str(a.ticks),'--dynamic-voices','--output',str(a.work)],check=True,stdout=subprocess.DEVNULL)
 orig=(a.work/f'{table}-first-tick.s16le').read_bytes(); info=json.loads((a.work/f'{table}-report.json').read_text())
 if a.ticks >= 5:
  static_work=a.work/f'{table}-static-five'
  subprocess.run([sys.executable,str(ROOT/'tools/verify_retail_tracker_pcm.py'),'--table',table,'--ticks','5','--output',str(static_work)],check=True,stdout=subprocess.DEVNULL)
  assert orig[:5*882*4]==(static_work/f'{table}-first-tick.s16le').read_bytes(),(table,'initial oracle mismatch')
 bank,_=extract(dat,0,(offset,));path=a.work/f'{table}.stim';path.write_bytes(bank)
 native=subprocess.check_output([str(a.native.resolve()),str(path),str(a.ticks*882),'137','restart',str(order),'retail'])
 assert len(orig)==len(native)==a.ticks*882*4
 raw_orig=struct.unpack(f'<{a.ticks*1764}h',orig);raw_native=struct.unpack(f'<{a.ticks*1764}h',native)
 assert raw_orig[::2]==raw_orig[1::2] and raw_native[::2]==raw_native[1::2]
 x=raw_orig[::2];y=raw_native[::2]
 windows=[]
 for tick in range(a.ticks):
  q=x[tick*882:(tick+1)*882];r=y[tick*882:(tick+1)*882];aa=sum(i*i for i in q);bb=sum(i*i for i in r)
  if aa and bb: windows.append((tick,sum(i*j for i,j in zip(q,r))/math.sqrt(aa*bb)))
 assert windows
 worst=sorted(windows,key=lambda w:w[1])[:5]
 aa=sum(i*i for i in x);bb=sum(i*i for i in y);assert aa and bb
 rows.append({'table':table,'ticks':a.ticks,'frames':a.ticks*882,'initial_five_windows_match_previous_oracle':a.ticks>=5,'original_sha256':hashlib.sha256(orig).hexdigest(),'native_sha256':hashlib.sha256(native).hexdigest(),'original_blocks':info['executed_original_blocks'],'overall_correlation':round(sum(i*j for i,j in zip(x,y))/math.sqrt(aa*bb),6),'rms_ratio':round(math.sqrt(bb/aa),6),'exact_frames':sum(i==j for i,j in zip(x,y)),'worst_windows':[{'tick':k,'correlation':round(c,6)} for k,c in worst]})
 assert rows[-1]['overall_correlation'] > 0.995, (table,rows[-1]['overall_correlation'])
 print(table,'overall',rows[-1]['overall_correlation'],'worst',rows[-1]['worst_windows'][0],flush=True)
report={'status':'MEASURED_BOUNDED','scope':__doc__,'native_sha256':hashlib.sha256(a.native.read_bytes()).hexdigest(),'cases':rows}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
