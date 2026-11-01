#!/usr/bin/env python3
"""Compare tracker channel periods in manually clocked Retail/STIM sequences.

The original tracker is initialized at adapted bank/order boundaries and
called once per native frame; mixer, real scheduler and output are not run.
Reports raw differences rather than inferring their causes or audibility.
"""
import argparse
import hashlib
import json
import os
import struct
import subprocess
from pathlib import Path
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_HOOK_BLOCK, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_EDX, UC_X86_REG_EIP, UC_X86_REG_ESP
from extract_mean_stim import extract
from verify_retail_tracker_pcm import ROOT, GAME, TABLES, EXE_SHA

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--native',type=Path,required=True)
p.add_argument('--work',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--ticks',type=int,default=300)
p.add_argument('--table',choices=tuple(TABLES),help='Optional single table')
p.add_argument('--order',type=int,help='Optional order in the selected startup bank')
p.add_argument('--require-exact',action='store_true',help='Require exact period fields in the bounded cases')
p.add_argument('--differences',type=Path,help='Optional full period-difference records (no sample data)')
p.add_argument('--capture',type=Path,help='Optional period and effect records for every compared channel tick')
p.add_argument('--library',type=Path,help='Optional libxmp shared library to select for the native probe')
a=p.parse_args(); assert 1 <= a.ticks <= 2000 and (a.order is None or (a.table and a.order >= 0))
a.work.mkdir(parents=True,exist_ok=True)
exe=(GAME/'SLAMTILT.EXE').read_bytes();assert hashlib.sha256(exe).hexdigest()==EXE_SHA
pe=pefile.PE(data=exe);image=pe.get_memory_mapped_image();tables=[]; all_differences={}; all_capture={}
env=dict(os.environ)
if a.library:
 library=a.library.absolute();env['LD_LIBRARY_PATH']=str(library.parent)
 assert str(library) in subprocess.check_output(['ldd',str(a.native.resolve())],env=env,text=True)
for table,(dat_sha,offset,order) in TABLES.items():
 if a.table and table != a.table:continue
 if a.order is not None:order=a.order
 dat=(GAME/'DAT'/f'{table.upper()}.DAT').read_bytes();assert hashlib.sha256(dat).hexdigest()==dat_sha
 u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image)
 u.mem_map(0x1100000,0x200000);u.mem_write(0x1100000,dat);u.mem_map(0x3000000,0x60000);blocks=set()
 u.hook_add(UC_HOOK_BLOCK,lambda _u,addr,size,_: blocks.add((addr,size)))
 def put(addr,value):u.mem_write(addr,struct.pack('<I',value&0xffffffff))
 def run(addr,eax=0):
  put(0x3050000,0x305fff0)
  for reg,value in ((UC_X86_REG_ESP,0x3050000),(UC_X86_REG_EAX,eax),(UC_X86_REG_EDX,0),(UC_X86_REG_EBX,0)):u.reg_write(reg,value)
  u.emu_start(addr,0x305fff0,count=10000000);assert u.reg_read(UC_X86_REG_EIP)==0x305fff0
 for addr,size in ((0x467580,4*0xac),(0x46b2d8,6*32),(0x46b060,6*0x60)):u.mem_write(addr,bytes(size))
 for i in range(4):put(0x467580+i*0xac,i)
 for addr,value in ((0x467578,0x1100000+offset),(0x46757c,0x1100000),(0x46c72c,0x46b2a4),(0x46754c,64),(0x467554,1)):put(addr,value)
 run(0x44f138,order)
 states=[]
 for tick in range(a.ticks):
  run(0x44eaf8)
  states.append([struct.unpack('<8I',u.mem_read(0x46b2d8+i*32,32)) for i in range(4)])
 for addr,size in blocks:
  assert 0x401000 <= addr and addr+size <= 0x454000
  fileoff=pe.get_offset_from_rva(addr-0x400000)
  assert bytes(u.mem_read(addr,size))==exe[fileoff:fileoff+size]
 stim,_=extract(dat,0,(offset,));bank=a.work/f'{table}.stim';bank.write_bytes(stim)
 output=subprocess.check_output([str(a.native.resolve()),str(bank),str(order),str(a.ticks)],text=True,env=env)
 lines=[[int(x) for x in line.split()] for line in output.splitlines()];assert len(lines)==a.ticks and all(len(x)==27 for x in lines)
 compared=0; matches=0; differences=[]; capture=[]
 for tick,(original,native) in enumerate(zip(states,lines)):
  for ch,row in enumerate(original):
   if not row[5] or not row[6]:continue
   period=row[5];actual=native[ch*6]; compared+=1
   if a.capture:capture.append({'tick':tick,'channel':ch,'original_period':period,'native_period_q12':actual,'effect_type':native[ch*6+4],'effect_parameter':native[ch*6+5],'order':native[24],'row':native[25],'frame':native[26]})
   if actual==period*4096:matches+=1
   else:differences.append({'tick':tick,'channel':ch,'original_period':period,'native_period_q12':actual,'delta_q12':actual-period*4096,'original_volume':row[6],'native_volume':native[ch*6+1],'event_note':native[ch*6+3],'effect_type':native[ch*6+4],'effect_parameter':native[ch*6+5],'order':native[24],'row':native[25],'frame':native[26]})
 significant=[d for d in differences if abs(d['delta_q12'])>=2048]
 if a.require_exact:assert not differences,(table,len(differences),differences[:3])
 all_differences[table]=differences
 if a.capture:all_capture[table]=capture
 tables.append({'table':table,'ticks':a.ticks,'compared_channel_ticks':compared,'exact_period_ticks':matches,'sub_half_period_differences':len(differences)-len(significant),'at_least_half_period_differences':len(significant),'max_abs_delta_q12':max((abs(d['delta_q12']) for d in differences),default=0),'first_differences':differences[:10],'largest_differences':sorted(differences,key=lambda d:abs(d['delta_q12']),reverse=True)[:10],'executed_original_blocks':len(blocks),'dat_sha256':dat_sha})
 print(table,compared,'period observations,',matches,'exact',flush=True)
report={'status':'MEASURED_BOUNDED','scope':__doc__,'exe_sha256':EXE_SHA,'native_sha256':hashlib.sha256(a.native.read_bytes()).hexdigest(),'library_sha256':hashlib.sha256(library.read_bytes()).hexdigest() if a.library else None,'tables':tables}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
if a.differences:
 a.differences.parent.mkdir(parents=True,exist_ok=True);a.differences.write_text(json.dumps(all_differences,indent=2)+'\n')
if a.capture:
 a.capture.parent.mkdir(parents=True,exist_ok=True);a.capture.write_text(json.dumps(all_capture,indent=2)+'\n')
