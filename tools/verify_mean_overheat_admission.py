#!/usr/bin/env python3
"""Bounded Original Overheat service34 -> raw038 ->40f754 contract."""
import argparse, hashlib, json, struct, subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX, UC_X86_REG_EDX, UC_X86_REG_ESI, UC_X86_REG_ESP, UC_X86_REG_EIP
p=argparse.ArgumentParser();p.add_argument('--native',required=True);a=p.parse_args()
r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes();records=[]
for kind,start,timer in [('activation',0x41d294,-1),('halfway',0x4150b8,3001),('timeout',0x4150b8,0),('collection',0x41e269,123)]:
 for handle in [0,-1]:
  u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
  def put(ad,v):u.mem_write(ad,struct.pack('<I',v&0xffffffff))
  def get(ad):return struct.unpack('<i',u.mem_read(ad,4))[0]
  put(0x43f0d0,0x1003000);put(0x43f068,0x1002000);put(0x1002030,2);put(0x43f054,12345678);u.mem_write(0x43f37a,struct.pack('<h',timer));put(0x1001000,161*65536);put(0x1001004,351*65536)
  for o in [0x34,0x58,0x5c,0x80,0x84]:put(0x1003000+o,0x1004000+o)
  put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.reg_write(UC_X86_REG_ESI,0x1001000);calls=[];callbacks=[]
  def hook(uc,ad,n,data):
   if ad in [0x100fff0,0x41e343]:uc.emu_stop();return
   if ad==0x40f754 or 0x1004000<=ad<=0x1004100:
    sp=uc.reg_read(UC_X86_REG_ESP)
    if ad==0x1004034:callbacks.append(get(sp+12));uc.reg_write(UC_X86_REG_EAX,handle)
    if ad==0x40f754:
     calls.append(dict(handle=get(0x43f038),selectors=[get(sp+4),uc.reg_read(UC_X86_REG_ECX),uc.reg_read(UC_X86_REG_EBX),uc.reg_read(UC_X86_REG_EDX),uc.reg_read(UC_X86_REG_EAX)],delay=get(sp+8)))
    uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if ad==0x1004034 else 8 if ad==0x40f754 else 0))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(start,0x100fff0,count=2000)
  assert len(calls)==1,(kind,handle,calls)
  assert calls[0]==dict(handle=handle,selectors=[1]*5,delay=0),(kind,handle,calls)
  records.append(dict(kind=kind,callback=callbacks[0],**calls[0],field024=0 if handle else 77,result=[0]*5 if handle else [101,102,103,104,105]))
fixture=r/'analysis/traces/mean-overheat-admission-original.json';fixture.write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),cases=len(records),records=records),indent=2)+'\n')
subprocess.run([a.native,str(fixture)],check=True)
print('8 Original Overheat admission/capture boundaries exact')
