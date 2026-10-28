#!/usr/bin/env python3
import json,struct,hashlib,subprocess,argparse
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
p=argparse.ArgumentParser();p.add_argument('--native',required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];image=(root/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def word(a,v):u.mem_write(a,struct.pack('<H',v&65535))
def read(a,n):return list(u.mem_read(a,n))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
calls=[]
def hook(uc,address,n,data):
 if address in [0x41e71a,0x41e343,0x41e415,0x41e3d5,0x41e4c0,0x41e563,0x41e5fb,0x100fff0]:uc.emu_stop();return
 if address in [0x1000400,0x1000500,0x1000600,0x1000700,0x40f754]:
  sp=uc.reg_read(UC_X86_REG_ESP);ea=uc.reg_read(UC_X86_REG_EAX)
  calls.append((address,get(sp+12) if address==0x1000400 else ea))
  uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if address==0x1000400 else 8 if address==0x40f754 else 0))
u.hook_add(UC_HOOK_CODE,hook)
put(0x43f0d0,0x1003000);put(0x43f068,0x1002000)
for offset,target in [(0x34,0x1000400),(0x5c,0x1000500),(0x58,0x1000600),(0x80,0x1000700)]:put(0x1003000+offset,target)
cases=[];expected=[]
for x,y in [(80,270),(81,270),(160,270),(161,270),(161,271),(161,350),(161,351)]:
 for mask in range(16):
  for cooldown in [-1,0,1]:
   for mode in [2,4]:
    for field37a in [-1,0]:
     commands=[[11+i,12+i,13+i,14+i] for i in range(4)];flags=[(mask>>i)&1 for i in range(4)];c=dict(x=x*65536,y=y*65536,flags=flags,cooldowns=[cooldown]*4,commands=commands,mode=mode,field37a=field37a)
     u.mem_write(0x43f1dc,bytes(flags));u.mem_write(0x43f26c,bytes(sum(commands,[])));u.mem_write(0x43f268,bytes([9,8,7,6]));u.mem_write(0x43f300,bytes([9,8,7,6]));word(0x43f1da,7);word(0x43f37a,field37a);put(0x43f054,12345);put(0x1002030,mode)
     for i in range(4):word(0x43ee1c+i*2,cooldown)
     put(0x1001000,c['x']);put(0x1001004,c['y']);put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.reg_write(UC_X86_REG_ESI,0x1001000);calls.clear()
     u.emu_start(0x41e269,0x100fff0,count=500)
     callback=next((v for address,v in calls if address==0x1000400),0)
     out=dict(flags=read(0x43f1dc,4),cooldowns=list(struct.unpack('<4h',u.mem_read(0x43ee1c,8))),commands=[read(0x43f26c+i*4,4) for i in range(4)],command268=read(0x43f268,4),command300=read(0x43f300,4),field1da=struct.unpack('<h',u.mem_read(0x43f1da,2))[0],field37a=struct.unpack('<h',u.mem_read(0x43f37a,2))[0],sample=any(address==0x1000500 for address,v in calls),group=callback==0x413958,callback=callback,score_add=sum(v for address,v in calls if address==0x1000600),stop84=any(address==0x1000700 for address,v in calls))
     cases.append(c);expected.append(out)
actual=json.loads(subprocess.run([a.native],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout)
for i,(original,native) in enumerate(zip(expected,actual)):
 assert original==native,(i,cases[i],original,native)
assert len(actual)==len(cases)
(root/'analysis/traces/mean-material5-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Original41e269..41e7fe; presentation externalcalls recorded, common50000score/normal prior boundary excluded',cases=cases,expected=expected),separators=(',',':'))+'\n')
print(f'{len(cases)} material5 original/native cases exact')
