#!/usr/bin/env python3
"""Bounded switch mutations/base awards vs original callbacks; initial mode only."""
import json,random,struct,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP,UC_X86_REG_EIP
ROOT=Path(__file__).resolve().parents[1]
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000),(0x2100000,0x2000)]:u.mem_map(a,n)
u.mem_write(0x400000,(ROOT/'build/mean-prepared/pe-data.bin').read_bytes())
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
put(0x43f0d0,0x1002000);put(0x1002058,0x2101000);put(0x43f068,0x1003000);put(0x1003030,1)
for layer,values in enumerate([(3,0x6040,0x959f6,0x9ba36,0xb3b36),(1,0x60e0,0xb98f6,0xbf9d6,0xcbb96),(1,0x3390,0xd1956,0xd4ce6,0xdb406),(1,0x41a0,0xde796,0xe2936,0xeac76)]):
 for i,value in enumerate(values):put(0x43f06c+layer*20+i*4,value+(0x1100000 if i>=2 else 0))
points=[]
def score(uc,a,n,c):
 points.append(uc.reg_read(UC_X86_REG_EAX));sp=uc.reg_read(UC_X86_REG_ESP)
 ret=struct.unpack('<I',uc.mem_read(sp,4))[0];uc.reg_write(UC_X86_REG_ESP,sp+4);uc.reg_write(UC_X86_REG_EIP,ret)
u.hook_add(UC_HOOK_CODE,score,begin=0x2101000,end=0x2101000)
rng=random.Random(1996);cases=[];expected=[]
for variant in range(7):
 for i in range(128):
  b=bytearray(rng.randbytes(100));layer=0 if variant<2 else 2;mask=4 if variant<2 else 1 if variant in (2,4,5,6) else 0
  x=rng.randrange(320*65536) if variant!=2 else rng.randrange(160*65536)
  y=rng.randrange(80*65536) if variant==0 else rng.randrange(120*65536,450*65536) if variant==1 else rng.randrange(150*65536,600*65536)
  if variant==4:x=rng.randrange(160*65536,234*65536);y=rng.randrange(60*65536,150*65536)
  if variant==5:x=rng.randrange(234*65536,320*65536);y=rng.randrange(60*65536,150*65536)
  if variant==6:x=rng.randrange(320*65536);y=rng.randrange(60*65536)
  struct.pack_into('<ii',b,0,x,y);struct.pack_into('<H',b,0x48,layer);struct.pack_into('<H',b,0x38,mask);struct.pack_into('<H',b,0x5c,rng.choice([0,3,8,9,10,14,15,16,17]))
  cases.append(dict(operation='switch_bundle',bytes=list(b)));u.mem_write(0x1000000,bytes(b));u.mem_write(0x43f1e8,bytes(4));points.clear()
  put(0x200f000,0x2100000);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000)
  u.emu_start(0x41c974 if layer==0 else 0x41bdd0,0x41be5d if variant==6 else 0x41c0a3 if variant==5 else 0x2100000,count=20000)
  if variant not in (5,6):assert u.reg_read(UC_X86_REG_ESP)==0x200f004
  expected.append(dict(bytes=list(u.mem_read(0x1000000,100)),points=sum(points),handled=True))
p=ROOT/'build/oracle/switch-bundle-cases.json';p.write_text(json.dumps(cases))
actual=json.loads(subprocess.check_output([str(ROOT/'build/native/mean_probe'),str(p),str(ROOT/'build/mean-prepared/lookup.bin')],text=True))
differences=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
report=dict(cases=len(cases),differences=differences,scope='Layer0mask4 Y<80 and120..450 initialfield43f3b8=0; layer2mask1 X<160 Y>=150; layer2mask0; layer2mask1 X160..234 Y60..150 directedtarget; X>=234 Y60..150 layer3 ball-local transfer; Y<60 velocity reduction before external rules. All100ball bytes + base awards, other rule effects excluded')
(ROOT/'analysis/traces/mean-switch-bundle-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert actual==expected
