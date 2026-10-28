#!/usr/bin/env python3
"""Original41d3e4 Skillshot request/capture ordering, independent of scalar oracle."""
import argparse,hashlib,json,struct,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
p=argparse.ArgumentParser();p.add_argument('--native',required=True);a=p.parse_args()
r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes();records=[]
for cash,selector in [(0,0)]+[(1,s) for s in range(7)]:
 for handle in [0,-1]:
  u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
  def put(ad,v):u.mem_write(ad,struct.pack('<I',v&0xffffffff))
  def get(ad):return struct.unpack('<i',u.mem_read(ad,4))[0]
  put(0x43f0d0,0x1003000);put(0x43f068,0x1002000);put(0x1002030,2)
  u.mem_write(0x43f358,struct.pack('<h',cash));u.mem_write(0x43f362,struct.pack('<h',selector));u.mem_write(0x43f35c,b'\xff\xff')
  for o in [0x34,0x58,0x84]:put(0x1003000+o,0x1004000+o)
  put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);calls=[]
  def hook(uc,ad,n,data):
   if ad==0x40f754 or 0x1004000<=ad<=0x1004100:
    sp=uc.reg_read(UC_X86_REG_ESP)
    if ad==0x1004034:
     calls.append(dict(kind='display',request=[uc.reg_read(reg) for reg in [UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ECX,UC_X86_REG_EBX]]+[get(sp+4),get(sp+8),get(sp+12)]));uc.reg_write(UC_X86_REG_EAX,handle)
    elif ad==0x40f754:
     calls.append(dict(kind='capture',handle=get(0x43f038),selectors=[get(sp+4),uc.reg_read(UC_X86_REG_ECX),uc.reg_read(UC_X86_REG_EBX),uc.reg_read(UC_X86_REG_EDX),uc.reg_read(UC_X86_REG_EAX)],delay=get(sp+8)))
    else:calls.append(dict(kind='score' if ad==0x1004058 else 'service84',eax=uc.reg_read(UC_X86_REG_EAX),edx=uc.reg_read(UC_X86_REG_EDX)))
    uc.reg_write(UC_X86_REG_EIP,get(sp)&0xffffffff);uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if ad==0x1004034 else 8 if ad==0x40f754 else 0))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x41d3e4,0x100fff0,count=2000)
  assert calls[0]==dict(kind='display',request=[7,6,2,0,48,1,0x40fdec]),calls
  capture=dict(kind='capture',handle=handle,selectors=[1]*5,delay=0)
  assert calls[1]==capture,calls
  assert sum(c['kind']=='capture' for c in calls)==1,calls
  assert get(0x43f038)==handle
  assert struct.unpack('<h',u.mem_read(0x43f35c,2))[0]==0
  records.append(dict(cash=cash,selector=selector,calls=calls,**{k:v for k,v in capture.items() if k!='kind'},field024=0 if handle else 77,result=[0]*5 if handle else [101,102,103,104,105]))
fixture=r/'analysis/traces/mean-skillshot-admission-original.json';fixture.write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),cases=len(records),scope='Actual41d3e4..41d8af; service34/58/84 and40f754 intercepted. Exact request, ordering, raw038, capture selectors; capture helper verified natively separately. Scheduler/voice internals not re-executed.',records=records),indent=2)+'\n')
subprocess.run([a.native,str(fixture)],check=True)
print(f'{len(records)} Original Skillshot request/capture boundaries exact')
