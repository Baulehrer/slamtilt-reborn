#!/usr/bin/env python3
"""Bounded4146ac total-page admission: exact register/stack request and control."""
import argparse,json,struct,hashlib,subprocess,itertools
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
p=argparse.ArgumentParser();p.add_argument('--native',required=True);a=p.parse_args();r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(ad,v):u.mem_write(ad,struct.pack('<I',v&0xffffffff))
def get(ad):return struct.unpack('<i',u.mem_read(ad,4))[0]
events={};handle=0
regs=[UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ECX,UC_X86_REG_EBX]
def hook(uc,ad,n,data):
 if ad==0x414710:uc.emu_stop();return
 if ad in [0x1000400,0x40f754]:
  sp=uc.reg_read(UC_X86_REG_ESP)
  values=[uc.reg_read(reg) for reg in regs]
  if ad==0x1000400:
   events['request']=values+[get(sp+4),get(sp+8),get(sp+12)];uc.reg_write(UC_X86_REG_EAX,handle)
  else:events['control']=values+[get(sp+4),get(sp+8)]
  uc.reg_write(UC_X86_REG_EIP,get(sp)&0xffffffff);uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if ad==0x1000400 else 8))
u.hook_add(UC_HOOK_CODE,hook);put(0x43f068,0x1002000);put(0x43f0d0,0x1003000);put(0x1003034,0x1000400)
cases=[];expected=[]
for pending,engine40,handle in itertools.product([0,-1,1,-32768],[-1,0,3],[0,-1]):
 c=dict(pending=pending,engine40=engine40,handle=handle);cases.append(c);events={}
 u.mem_write(0x43f366,struct.pack('<h',pending));put(0x1002040,engine40);put(0x43f038,123)
 put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.emu_start(0x4146ac,0x100fff0,count=1000)
 expected.append(dict(pending=struct.unpack('<h',u.mem_read(0x43f366,2))[0],engine40=get(0x1002040),returned=get(0x43f038),events=events))
actual=json.loads(subprocess.check_output([a.native],input=json.dumps(cases),text=True));assert actual==expected,[(i,x,y) for i,(x,y) in enumerate(zip(actual,expected)) if x!=y][:1]
report=dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Original4146ac..41470f; pending0 stops before subsequent idle work at414710; service34 admission return0/-1 controlled, actual fixed request and40f754 register/stack arguments recorded; delay application excluded',verified_cases=len(cases),records=[dict(input=c,expected=e) for c,e in zip(cases,expected)])
(r/'analysis/traces/mean-mode-total-idle-original.json').write_text(json.dumps(report,indent=2)+'\n');print(f'{len(cases)} original/native mode-total idle cases exact')
