#!/usr/bin/env python3
import argparse,json,struct,hashlib,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
p=argparse.ArgumentParser();p.add_argument('--native',required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];image=(root/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
def hook(uc,address,n,data):
 if address in [0x41ce3a,0x41d093,0x41d0f5,0x100fff0]:uc.emu_stop();return
 if address in [0x1000400,0x1000500,0x40f754]:
  sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if address==0x1000400 else 8 if address==0x40f754 else 0))
u.hook_add(UC_HOOK_CODE,hook);put(0x43f0d0,0x1003000);put(0x1003010,0x1004000);put(0x1003034,0x1000400);put(0x1003058,0x1000500)
cases=[];expected=[]
for x in [22*65536,23*65536-1,23*65536,160*65536,275*65536-1,275*65536]:
 for field in [-1,0,1,2,3]:
  for player in [0,1,32767,32768,65535]:
   c=dict(x=x,field=field,player=player);cases.append(c)
   u.mem_write(0x43f1fc,struct.pack('<h',field));u.mem_write(0x1004010,struct.pack('<H',player));u.mem_write(0x43f208,bytes([9,8,7,6])*63);put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000)
   # The middle targets do not call41d220; gate is originalcaller code.
   if x<23*65536:u.emu_start(0x41ce2b,0x100fff0,count=200)
   elif x>=275*65536:u.emu_start(0x41d084,0x100fff0,count=200)
   new=struct.unpack('<H',u.mem_read(0x1004010,2))[0]
   expected.append(dict(field=struct.unpack('<h',u.mem_read(0x43f1fc,2))[0],player=new,hit=new!=player,lamps=[list(u.mem_read(0x43f208+i*4,4)) for i in [23,60,61]]))
actual=json.loads(subprocess.run([a.native],input=json.dumps(cases),capture_output=True,text=True,check=True).stdout)
assert len(actual)==len(expected)
for i,(x,y) in enumerate(zip(expected,actual)):assert x==y,(i,cases[i],x,y)
(root/'analysis/traces/mean-side-extra-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Original41ce2b/41d084 gates and41d220;servicesstubbed,DMD410e4cexcluded',cases=cases,expected=expected),separators=(',',':'))+'\n')
print(len(cases),'original/native side extra ball cases exact')
