#!/usr/bin/env python3
"""Execute41d153 reward continuation; stop at actual presentation call40f754."""
import hashlib,json,random,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP,UC_X86_REG_EIP
ROOT=Path(__file__).resolve().parents[1];image=(ROOT/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000),(0x2100000,0x2000)]:u.mem_map(a,n)
u.mem_write(0x400000,image)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
put(0x43f0d0,0x1002000);put(0x1002010,0x1003000);put(0x1002058,0x2101000);put(0x1002034,0x2101010)
points=0;pending=False
def hook(uc,a,n,c):
 global points,pending
 if a==0x40f754:pending=True;uc.emu_stop();return
 sp=uc.reg_read(UC_X86_REG_ESP);ret=struct.unpack('<I',uc.mem_read(sp,4))[0]
 if a==0x2101000:points+=uc.reg_read(UC_X86_REG_EAX);size=4
 else:size=16;uc.reg_write(UC_X86_REG_EAX,1)
 uc.reg_write(UC_X86_REG_ESP,sp+size);uc.reg_write(UC_X86_REG_EIP,ret)
u.hook_add(UC_HOOK_CODE,hook,begin=0x2101000,end=0x2101010)
u.hook_add(UC_HOOK_CODE,hook,begin=0x40f754,end=0x40f754)
rng=random.Random(0x41d153);cases=[]
for player in range(8):
 for count in [0,1,-1,32767,-32768]:
  for i in range(8):
   c=dict(field_player_12=player,field_43f1fa=count,command_43f2f4=list(rng.randbytes(4)))
   u.mem_write(0x1003010,struct.pack('<HH',rng.randrange(65536),player));u.mem_write(0x43f1fa,struct.pack('<h',count));u.mem_write(0x43f2f4,bytes(c['command_43f2f4']))
   put(0x200f010,0x2100000);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1002000);points=0;pending=False
   u.emu_start(0x41d153,0x2100000,count=2000)
   c['expected']=dict(field_player_12=struct.unpack('<h',u.mem_read(0x1003012,2))[0],field_43f1fa=struct.unpack('<h',u.mem_read(0x43f1fa,2))[0],command_43f2f4=list(u.mem_read(0x43f2f4,4)),score_points=points,services_pending=pending)
   cases.append(c)
report=dict(image_sha256=hashlib.sha256(image).hexdigest(),entry='0x41d153',presentation_boundary='0x40f754',cases=cases)
(ROOT/'analysis/traces/mean-top-target-reward-original.json').write_text(json.dumps(report,separators=(',',':'))+'\n');print(len(cases))
