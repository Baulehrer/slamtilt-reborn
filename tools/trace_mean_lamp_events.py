#!/usr/bin/env python3
"""Original top-target caller through its proven lamp/reward boundary."""
import hashlib,json,random,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP,UC_X86_REG_EIP
ROOT=Path(__file__).resolve().parents[1]
image=(ROOT/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000),(0x2100000,0x2000)]:u.mem_map(a,n)
u.mem_write(0x400000,image)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
put(0x43f0d0,0x1002000);put(0x1002058,0x2101000);put(0x1002010,0x1003000)
continuation=False
def hook(uc,a,n,c):
 global continuation
 if a==0x41d177:continuation=True;uc.emu_stop();return
 sp=uc.reg_read(UC_X86_REG_ESP);ret=struct.unpack('<I',uc.mem_read(sp,4))[0]
 uc.reg_write(UC_X86_REG_ESP,sp+4);uc.reg_write(UC_X86_REG_EIP,ret)
u.hook_add(UC_HOOK_CODE,hook,begin=0x2101000,end=0x2101000)
u.hook_add(UC_HOOK_CODE,hook,begin=0x41d177,end=0x41d177)
rng=random.Random(0x41c974);cases=[]
for x in [-65536,0,64*65536-1,64*65536,91*65536-1,91*65536,319*65536]:
 for flags in range(8):
  for services in [0,1,-1]:
   for y in [-65536,0,80*65536-1]:
    c=dict(x=x,y=y,flags=[(flags>>i)&1 for i in range(3)],commands=[list(rng.randbytes(4)) for i in range(3)],field_services_1c=services)
    put(0x1000000,x);put(0x1000004,y);put(0x100201c,services)
    u.mem_write(0x43f1e8,bytes(c['flags']));u.mem_write(0x43f280,bytes(sum(c['commands'],[])))
    put(0x200f000,0x2100000);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);continuation=False
    u.emu_start(0x41c974,0x2100000,count=2000)
    c['expected']=dict(flags=list(u.mem_read(0x43f1e8,3)),commands=[list(u.mem_read(0x43f280+i*4,4)) for i in range(3)],request_41d153=continuation)
    cases.append(c)
report=dict(image_sha256=hashlib.sha256(image).hexdigest(),entry='0x41c974',reward_boundary='0x41d177',cases=cases)
(ROOT/'analysis/traces/mean-lamp-events-original.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
print(len(cases))
