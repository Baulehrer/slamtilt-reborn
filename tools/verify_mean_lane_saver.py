#!/usr/bin/env python3
"""Bounded actual417dd4 slot timing, service60 request and collision patch.
Usage: --native path/to/mean_lane_saver_probe (does not build).
"""
import argparse,hashlib,itertools,json,struct,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_EIP,UC_X86_REG_ESP
p=argparse.ArgumentParser();p.add_argument('--native',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];image=(root/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32)
for base,size in [(0x400000,0x100000),(0x1000000,0x200000)]:u.mem_map(base,size)
u.mem_write(0x400000,image)
def put(address,value):u.mem_write(address,struct.pack('<I',value&0xffffffff))
def get(address):return struct.unpack('<I',u.mem_read(address,4))[0]
draw=[]
def hook(uc,address,size,data):
 if address==0x1000400:
  assert uc.reg_read(UC_X86_REG_EAX)==5
  draw.append(uc.reg_read(UC_X86_REG_EDX))
  sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,hook)
put(0x43f0d0,0x1003000);put(0x1003060,0x1000400)
put(0x438230+5*4,0x1004000)
put(0x43efd8,0x1100000);put(0x43f074,0x1110000);put(0x43f078,0x1130000)
dat=bytes((i*17+(i>>8))&255 for i in range(0x100000))
cases=[];expected=[]
for timer,frame,target,idle in itertools.product([-2,-1,0,1,3,4],[-1,0,1,2,3],[-1,0,1],[False,True]):
 c=dict(slot=[timer,frame,target],idle=idle);cases.append(c)
 u.mem_write(0x1100000,dat);u.mem_write(0x438b44,struct.pack('<iii',timer,frame,target));u.mem_write(0x1004002,struct.pack('<h',-1 if idle else 0))
 put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.reg_write(UC_X86_REG_EAX,0x438b44);u.reg_write(UC_X86_REG_EDX,5);draw.clear()
 u.emu_start(0x417dd4,0x100fff0,count=2000)
 patch=[]
 for y in range(30):patch.extend(u.mem_read(0x11149e1+y*40,4))
 hit=[]
 for plane in range(4):
  for y in range(32):hit.extend(u.mem_read(0x11349e1+plane*0x6040+y*40,4))
 expected.append(dict(slot=list(struct.unpack('<iii',u.mem_read(0x438b44,12))),draw=draw[0] if draw else None,patch=patch,hit=hit))
actual=json.loads(subprocess.run([a.native],input=json.dumps(cases),capture_output=True,text=True,check=True).stdout)
assert len(actual)==len(expected)
differences=[i for i,(x,y) in enumerate(zip(expected,actual)) if x!=y]
report=dict(scope='Actual417dd4;service60 draw observed/stubbed; original collision and four-plane terminal copies execute; synthetic DAT; full slot, normal and all four hit/material planes compared',image_sha256=hashlib.sha256(image).hexdigest(),cases=cases,expected=expected,differences=differences)
(root/'analysis/traces/mean-lane-saver-original.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
assert not differences,(differences[:3],cases[differences[0]],expected[differences[0]],actual[differences[0]])
print(len(cases),'original/native lane saver cases exact')
