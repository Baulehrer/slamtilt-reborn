#!/usr/bin/env python3
"""Validate capture-exit +7 bitmap pointers against original normal evaluator."""
import json, random, struct
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ESP
ROOT=Path(__file__).resolve().parents[1]
u=Uc(UC_ARCH_X86,UC_MODE_32)
for address,size in [(0x400000,0x100000),(0x1000000,0x400000),(0x2000000,0x10000),(0x2100000,0x1000)]:u.mem_map(address,size)
u.mem_write(0x400000,(ROOT/'build/mean-prepared/pe-data.bin').read_bytes())
dat=(ROOT/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT').read_bytes()
u.mem_write(0x1100000,dat)
for address in [0x43e71c,0x43e410]:u.mem_write(address,bytes(4))
raw=(ROOT/'build/mean-prepared/normals-1.bin').read_bytes();cache=struct.unpack('<'+str(320*616)+'h',raw[12:])
rng=random.Random(0x416e28);cases=[]
while len(cases)<512:
 x=rng.randrange(8,256);y=rng.randrange(8,608)
 if not dat[0xbf9d6+7+y*40+x//8] & (128>>(x&7)):continue
 b=bytearray(100);struct.pack_into('<ii',b,0,x<<16,y<<16);struct.pack_into('<I',b,0x44,0x1100000+0xb98f6+7)
 u.mem_write(0x1000000,bytes(b));u.mem_write(0x200f000,struct.pack('<I',0x2100000));u.reg_write(UC_X86_REG_EAX,0x1000000);u.reg_write(UC_X86_REG_ESP,0x200f000)
 u.emu_start(0x40e1d0,0x2100000,count=10000)
 actual=u.reg_read(UC_X86_REG_EAX);actual=actual if actual<0x80000000 else actual-0x100000000
 expected=cache[y*320+x+56];cases.append(dict(x=x,y=y,original=actual,native=expected))
differences=[c for c in cases if c['original']!=c['native']]
r=dict(cases=len(cases),differences=differences,scope='Original40e1d0 layer1 normal pointer+7 equals base cache at X+56; shifted hit pixels, cache interior only')
(ROOT/'analysis/traces/mean-pointer-shift-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));assert not differences
