#!/usr/bin/env python3
import argparse,json,struct,hashlib,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
p=argparse.ArgumentParser();p.add_argument('--native',required=True);a=p.parse_args();r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(ad,v):u.mem_write(ad,struct.pack('<I',v&0xffffffff))
def get(ad):return struct.unpack('<I',u.mem_read(ad,4))[0]
events={}
def hook(uc,ad,n,data):
 if ad==0x1000500:
  events.update(descriptor=uc.reg_read(UC_X86_REG_EAX),edx=uc.reg_read(UC_X86_REG_EDX),ebx=uc.reg_read(UC_X86_REG_EBX))
  sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,hook);put(0x100305c,0x1000500)
cases=[];expected=[]
for right in [False,True]:
 for stage in [0,1,2,3]:
  for field034 in [0,0x13ffff,0x140000,0x140001,0x7fffffff,0x80000000,0xffffffff]:
   for edge in [-1,0,1]:
    for service1c in [0,1]:
     f=bytearray((i*7)%256 for i in range(0x3c0));f[0x068:0x06c]=struct.pack('<I',0x1002000);f[0x0d0:0x0d4]=struct.pack('<I',0x1003000);f[0x3a4:0x3a6]=struct.pack('<H',2);f[0x01c:0x020]=struct.pack('<I',stage);f[0x034:0x038]=struct.pack('<I',field034)
     cases.append(dict(fields=list(f),edge=edge,service1c=service1c,engine44=1,right=right))
     u.mem_write(0x43f000,bytes(f));put(0x1002044,1);put(0x100301c,service1c);sp=0x100f000;put(sp,0x100fff0);u.reg_write(UC_X86_REG_ESP,sp);u.reg_write(UC_X86_REG_EAX,edge&0xffffffff);events=dict(descriptor=0,edx=0,ebx=0)
     u.emu_start(0x41766c if right else 0x417374,0x100fff0,count=1000)
     expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),**events))
actual=json.loads(subprocess.run([a.native],input=json.dumps(cases),capture_output=True,text=True,check=True).stdout)
for i,(x,y) in enumerate(zip(expected,actual)):
 if x!=y:raise AssertionError((i,[(hex(k),aa,bb) for k,(aa,bb) in enumerate(zip(x['fields'],y['fields'])) if aa!=bb],{k:v for k,v in x.items() if k!='fields'},{k:v for k,v in y.items() if k!='fields'}))
assert len(actual)==len(expected)
(r/'analysis/traces/mean-minigame2-input-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Registered417374/41766c actualEngine44=1 WORD3a4=2;5c recorded;integerwrap/negativeSAR included',cases=cases,expected=expected),separators=(',',':'))+'\n');print(len(cases),'original/native minigame2 input cases exact')
