#!/usr/bin/env python3
import argparse,json,struct,hashlib,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
p=argparse.ArgumentParser();p.add_argument('--native',required=True);a=p.parse_args();r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(ad,v):u.mem_write(ad,struct.pack('<I',v&0xffffffff))
def get(ad):return struct.unpack('<I',u.mem_read(ad,4))[0]
requests=[]
def hook(uc,ad,n,data):
 if ad==0x1000500:
  requests.append(uc.reg_read(UC_X86_REG_EAX))
  assert (uc.reg_read(UC_X86_REG_EDX),uc.reg_read(UC_X86_REG_EBX))==(2,1)
  sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,hook);put(0x100305c,0x1000500)
cases=[];expected=[]
for right in [False,True]:
 for mode in [1,2,3,4,5,6]:
  for side in [-1,0,1,2]:
   for edge in [-1,0,1]:
    for service in [0,1]:
     for seed in range(6):
      f=bytearray((i*7+seed)%256 for i in range(0x3c0))
      def word(o,v):f[o:o+2]=struct.pack('<H',v&65535)
      f[0x068:0x06c]=struct.pack('<I',0x1002000);f[0x0d0:0x0d4]=struct.pack('<I',0x1003000)
      if mode==4:word(0x3a6,2) # Isolate common human actions; phase0/1 tested separately.
      word(0x1fc,side);word(0x358,0x7fff if seed&1 else 0);word(0x35c,0xffff if seed>=4 else seed>>1)
      for i in range(3):f[0x1e8+i]=(seed>>i)&1
      for i in range(5):f[0x1ec+i]=(seed>>(i%3))&1
      c=dict(fields=list(f),right=right,mode=mode,edge=edge,service=service);cases.append(c)
      u.mem_write(0x43f000,bytes(f));put(0x1002030,mode);put(0x1002044,0);put(0x100301c,service);put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.reg_write(UC_X86_REG_EAX,edge&0xffffffff);requests.clear()
      u.emu_start(0x41766c if right else 0x417374,0x100fff0,count=1000)
      expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),descriptor=requests[0] if requests else 0))
actual=json.loads(subprocess.run([a.native],input=json.dumps(cases),capture_output=True,text=True,check=True).stdout)
assert len(actual)==len(expected)
for i,(x,y) in enumerate(zip(expected,actual)):
 if x!=y:raise AssertionError((i,[(hex(k),aa,bb) for k,(aa,bb) in enumerate(zip(x['fields'],y['fields'])) if aa!=bb],x['descriptor'],y['descriptor']))
(r/'analysis/traces/mean-flipper-actions-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Registered417374/41766c humanengine44zero,mode4phase0/1separatelyverified,commonphase2included;actual40f8ec;service5crecorded',cases=cases,expected=expected),separators=(',',':'))+'\n');print(len(cases),'original/native flipper action cases exact')
