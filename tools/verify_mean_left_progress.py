#!/usr/bin/env python3
"""Bounded actual41b31f progression, after original shared reward; no geometry injection claim."""
import json,struct,hashlib,subprocess,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
R=Path(__file__).resolve().parents[1];image=(R/'build/mean-prepared/pe-data.bin').read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
events={};admitted=0
def hook(uc,a,size,data):
 if a==0x100fff0:uc.emu_stop()
 elif a in [0x1000400,0x40f754]:
  sp=uc.reg_read(UC_X86_REG_ESP)
  if a==0x1000400:
   events['callback']=get(sp+12);events['display']=True
   assert [uc.reg_read(r) for r in [UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ECX,UC_X86_REG_EBX]]==[6,5,2,0]
   assert [get(sp+4),get(sp+8)]==[11,1]
   uc.reg_write(UC_X86_REG_EAX,admitted)
  else:
   events['delay']=True
   assert [uc.reg_read(r) for r in [UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ECX,UC_X86_REG_EBX]]==[1,1,1,1]
   assert [get(sp+4),get(sp+8)]==[1,0]
  uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if a==0x1000400 else 8))
u.hook_add(UC_HOOK_CODE,hook);cases=[];expected=[]
for mode in range(1,7):
 for stage in range(3):
  for count in [0,1,4,5]:
   for admitted in [0,1,7]:
    f=bytearray((i*3+17)%256 for i in range(0x3c0))
    for o,v in [(0x3ba,stage),(0x1f2,count),(0x392,-1)]:struct.pack_into('<H',f,o,v&65535)
    struct.pack_into('<I',f,0x0d0,0x1003000);u.mem_write(0x43f000,bytes(f));put(0x1003034,0x1000400)
    sp=0x100f000
    for i in range(6):put(sp+i*4,0)
    put(sp+24,0x100fff0);u.reg_write(UC_X86_REG_ESP,sp);u.reg_write(UC_X86_REG_EBX,mode);u.reg_write(UC_X86_REG_EDX,4)
    events=dict(callback=0,display=False,delay=False);u.emu_start(0x41b31f,0x100fff0,count=1000)
    cases.append(dict(fields=list(f),mode=mode,admitted=admitted));expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),**events))
actual=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases),text=True));assert actual==expected,next((i,[(hex(k),a,b) for k,(a,b) in enumerate(zip(x['fields'],y['fields'])) if a!=b],x['callback'],y['callback']) for i,(x,y) in enumerate(zip(actual,expected)) if x!=y)
(R/'analysis/traces/mean-left-progress-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Actual41b31f..41b491 after shared event and slotwrites; geometry guard41b2c9=layer3/mask1/Y140..159/X<160 caller boundary; exact34/40f754 parameters, external helpers stubbed. Validstage0..2/count0..5.',cases=cases,expected=expected),separators=(',',':'))+'\n')
print(len(cases),'original left progress raw states and display/delay parameters exact')
