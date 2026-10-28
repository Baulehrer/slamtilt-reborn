#!/usr/bin/env python3
import json,struct,subprocess,sys,hashlib
from pathlib import Path
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_32)
u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
events={}
def hook(uc,a,n,d):
 if a==0x41d0f5:uc.emu_stop();return
 if a in [0x1000400,0x1000500,0x416fe0,0x41b8d0,0x40f754]:
  sp=uc.reg_read(UC_X86_REG_ESP)
  if a==0x1000400:events['callback']=get(sp+12);uc.reg_write(UC_X86_REG_EAX,0)
  if a==0x1000500:events['score']=uc.reg_read(UC_X86_REG_EAX)
  if a==0x416fe0:events['reset']=True
  uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if a==0x1000400 else 8 if a==0x40f754 else 0))
u.hook_add(UC_HOOK_CODE,hook);put(0x43f068,0x1002000);put(0x43f0d0,0x1003000);put(0x1003034,0x1000400);put(0x1003058,0x1000500)
cases=[];expected=[]
for mode in [1,2,3,4,5,6]:
 for stage in [0,1,2]:
  for timer in [-1,0,400]:
   for count in [0,1,32767,65535]:
    for extra in [0,4,5]:
     f=bytearray(0x3c0)
     for o,v in [(0x3bc,stage),(0x3b0,timer),(0x39a,count),(0x1f2,extra),(0x3a2,65535)]:struct.pack_into('<H',f,o,v&65535)
     struct.pack_into("<I",f,0x068,0x1002000);struct.pack_into("<I",f,0x0d0,0x1003000)
     u.mem_write(0x43f000,bytes(f));put(0x43f068,0x1002000);put(0x43f0d0,0x1003000);put(0x1002030,mode)
     events=dict(score=0,callback=0,reset=False);sp=0x100f000
     for i in range(5):put(sp+i*4,0)
     put(sp+20,0x100fff0);u.reg_write(UC_X86_REG_ESP,sp);u.emu_start(0x41cb28,0x100fff0,count=3000)
     cases.append(dict(fields=list(f),mode=mode));expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),**events))
actual=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases),text=True));assert actual==expected,next((i,[k for k in a if a[k]!=b[k]],[(hex(o),x,y) for o,(x,y) in enumerate(zip(a['fields'],b['fields'])) if x!=y]) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b)
(r/'analysis/traces/mean-right-progress-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='41cb28..41cd50;41b8d0/common scheduler and416fe0 external adapters;validlampindices0..2',cases=cases,expected=expected),separators=(',',':'))+'\n');print(len(cases),'original progress states exact')
