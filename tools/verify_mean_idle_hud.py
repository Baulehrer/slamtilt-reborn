#!/usr/bin/env python3
"""Bounded41472e Original idle HUD: actual bitmap, small-number and BCD score services."""
import argparse,json,struct,hashlib,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import *
p=argparse.ArgumentParser();p.add_argument('--native');a=p.parse_args();root=Path(__file__).resolve().parents[1]
directory=next((root/'build/corpus/win95/demo-1997').rglob('MEAN.DAT')).parent
mean=(directory/'MEAN.DAT').read_bytes();main=(directory/'MAIN.DAT').read_bytes();image=(root/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x100000);u.mem_map(0x1100000,0x200000);u.mem_write(0x1100000,mean);u.mem_write(0x1010000,main)
def put(ad,v):u.mem_write(ad,struct.pack('<I',v&0xffffffff))
def word(ad,v):u.mem_write(ad,struct.pack('<H',v&0xffff))
def get(ad):return struct.unpack('<I',u.mem_read(ad,4))[0]
def call(ad,stack_words=0):
 sp=0x10ff000;u.reg_write(UC_X86_REG_ESP,sp);u.mem_write(sp,bytes(stack_words*4));put(sp+stack_words*4,0x10ffff0);u.emu_start(ad,0x10ffff0,count=100000);assert u.reg_read(UC_X86_REG_EIP)==0x10ffff0
call(0x40af14)
for ad,value in [(0x43e3e8,0x1000000),(0x43e82c,0x1010000),(0x43efd8,0x1100000),(0x43f068,0x1002000),(0x43f0d0,0x1003000),(0x1003010,0x1006000),(0x100303c,0x406680),(0x1003040,0x406280),(0x1003044,0x40617c)]:put(ad,value)
cases=[]
# Thresholds and complete frame cycles, valid five puncture levels, full uint32 counters.
for pit,bank in [(-1,-1),(-1,0),(-1,3000),(-1,3001),(0,-1),(49,-1),(50,0),(399,2999),(32767,32767)]:
 for counter in list(range(36))+[63,64,79,80,127,128,0x7fffffff,0xffffffff]:
  for punctures in ([0,1,2,3,4] if pit>=0 else [0]):
   cases.append(dict(counter=counter,field_398=pit,field_37a=bank,field_3ac=punctures,field_054=[0,123456789,4294967294][counter%3],score=[0,194839960,999999999999][counter%3]))
expected=[]
for c in cases:
 put(0x438af8,c['counter']);word(0x43f398,c['field_398']);word(0x43f37a,c['field_37a']);word(0x43f3ac,c['field_3ac']);put(0x43f054,c['field_054'])
 digits=f'{c["score"]:012d}';u.mem_write(0x1006000,bytes(int(digits[i:i+2],16) for i in range(0,12,2)))
 u.mem_write(0x1000000,bytes(i%4 for i in range(1920)));call(0x41472e,4)
 expected.append(dict(counter=get(0x438af8),pixels=list(u.mem_read(0x1000000,1920))))
if not a.native:print(len(cases),'Original idle HUD cases captured');raise SystemExit(0)
actual=json.loads(subprocess.run([a.native,str(directory/'MEAN.DAT'),str(directory/'MAIN.DAT')],input=json.dumps(cases),capture_output=True,text=True,check=True).stdout)
assert len(actual)==len(expected)
for n,(x,y) in enumerate(zip(expected,actual)):
 if x!=y:
  differing=[(i,v,y['pixels'][i]) for i,v in enumerate(x['pixels']) if y['pixels'][i]!=v]
  raise AssertionError((n,cases[n],x['counter'],y['counter'],differing[:12],len(differing)))
report=dict(entry='0x41472e',image_sha256=hashlib.sha256(image).hexdigest(),mean_dat_sha256=hashlib.sha256(mean).hexdigest(),main_dat_sha256=hashlib.sha256(main).hexdigest(),scope='Actual idle HUD bitmap3c, small numeric44 and BCD player score40; counter and1920 pixels exact; scheduler excluded',verified_cases=len(cases),cases=cases)
(root/'analysis/traces/mean-idle-hud-original.json').write_text(json.dumps(report,indent=2)+'\n');print(len(cases),'Original/native idle HUD pixel/counter cases exact')
