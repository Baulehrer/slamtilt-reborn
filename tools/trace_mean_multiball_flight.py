#!/usr/bin/env python3
"""Bounded original release flight with cached poses and point forces disabled."""
import json,struct
from pathlib import Path
exec((Path(__file__).parent/'trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
from unicorn.x86_const import *
from unicorn import UC_HOOK_MEM_INVALID
prep=ROOT/'build/mean-prepared'
u.mem_write(0x43e700,(prep/'engine-globals.bin').read_bytes());u.mem_write(0x43e850,(prep/'flipper-state.bin').read_bytes())
def bad(uc,access,a,n,v,c):print('INVALID',hex(uc.reg_read(UC_X86_REG_EIP)),hex(a));return False
u.hook_add(UC_HOOK_MEM_INVALID,bad)
dat=next((ROOT/'build/corpus/win95/demo-1997').rglob('MEAN.DAT')).read_bytes();u.mem_map(0x1100000,(len(dat)+4095)//4096*4096);u.mem_write(0x1100000,dat)
u.mem_write(0x1006000,(prep/'lookup.bin').read_bytes())
for a,v in [(0x43e764,0x1006000),(0x43e744,0x1006800),(0x43e728,0x42c9fc),(0x43d860,0),(0x43d864,0),(0x4298a4,0),(0x43e740,0x1005000),(0x1005004,0x1005100),(0x1005108,0x1005200),(0x100522c,0x4152fc),(0x1005204,0x1005300),(0x4298c8,0x1000000),(0x43e770,1),(0x43f068,0x1001000),(0x43f0d0,0x1002000)]:put(a,v)
for k,a in enumerate([0x41e00c,0x41e800,0x41e8b8,0x41e828,0x41e828]):put(0x1005300+k*4,a)
for k,a in enumerate([0x41c938,0x41c464,0x41bdd0,0x41ad84,0x41ac7c]):put(0x1005250+k*4,a)
# Bitmap dispatch reads descriptor switcharray at+0; adjust after first trace if necessary.
put(0x1005200,0x1005500)
for k,a in enumerate([0x41c938,0x41c464,0x41bdd0,0x41ad84,0x41ac7c]):put(0x1005500+k*4,a)
put(0x1005100,0x1005500);put(0x1005104,0x1005300)
put(0x1005000,0x1005600);u.mem_write(0x100561c,struct.pack("<H",1))
put(0x100205c,0x200ff00);put(0x1001030,5);u.mem_write(0x43f1e6,struct.pack('<h',4))
def run(a,eax):
 put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,eax);u.emu_start(a,0x200fff0,count=50000)
u.mem_write(0x1000000,bytes(100));run(0x416e78,0x1000000)
records=[list(u.mem_read(0x1000000,100))]
for i in range(120):
 run(0x4088f0,0);records.append(list(u.mem_read(0x1000000,100)))
 if i%25==0:print(i+1,get(0x1000000)/65536,get(0x1000004)/65536,word(0x1000048))
(ROOT/'analysis/traces/mean-multiball-flight-original.json').write_text(json.dumps(dict(scope='Original4088f0 after actual416e78; cachedrestflippers, no pointforces; syntheticenginepointers and bounded services',states=records),separators=(',',':'))+'\n')
