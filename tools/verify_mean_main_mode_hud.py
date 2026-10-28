#!/usr/bin/env python3
"""Bounded main-mode and SPEED HUDs: actual Original services and full pixels."""
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
for ad,value in [(0x43e3e8,0x1000000),(0x43e82c,0x1010000),(0x43efd8,0x1100000),(0x43f068,0x1002000),(0x43f0d0,0x1003000),(0x1003010,0x1006000),(0x100303c,0x406680),(0x1003040,0x406280),(0x1003044,0x40617c),(0x100304c,0x4060a4)]:put(ad,value)
cases=[]
def add(mode,selected,counter,**kw):
 c=dict(mode=mode,selected=selected,counter=counter,field_39c=12345,field_38c=0,field_38e=-1,field_368=-1,field_36c=-1,field_05c=123456789,score=194839960)
 c.update(kw);cases.append(c)
for selected in [0,1,2,3,4]:
 for counter in list(range(201))+[511,512,575,576,999,2147483647]:
  add(5,selected,counter,field_39c=[0,199,200,32767][counter%4],field_38c=counter%6,score=[0,194839960,999999999999][counter%3])
# Signed division paths are only exercised with valid Original frame indices.
for counter in [0,1,3,4,7,8,15,16,31,32,127,128,0x7fffffff,0xffffffff]:
 for flags in range(8):
  add(6,0,counter,field_38e=0 if flags&1 else -1,field_368=32767 if flags&2 else -32768,field_36c=1 if flags&4 else -1)
for target in range(6):
 for counter in range(88):add(5,2,counter,field_38c=target)
for selected in [0,1,2,4]:
 for timer in [0,1,199,200,32767]:add(5,selected,0,field_39c=timer)
expected=[]
entries={0:0x414084,1:0x413f68,2:0x413e3c,4:0x413da8}
for c in cases:
 put(0x438af8,c['counter']);word(0x43f39c,c['field_39c']);word(0x43f38c,c['field_38c']);word(0x43f38e,c['field_38e']);word(0x43f368,c['field_368']);word(0x43f36c,c['field_36c']);put(0x43f05c,c['field_05c'])
 digits=f'{c["score"]:012d}';u.mem_write(0x1006000,bytes(int(digits[i:i+2],16) for i in range(0,12,2)))
 u.mem_write(0x1000000,bytes(i%4 for i in range(1920)))
 entry=0x413c94 if c['mode']==6 else entries.get(c['selected'])
 if entry:
  try:call(entry)
  except Exception as exc:raise RuntimeError((c,hex(u.reg_read(UC_X86_REG_EIP)))) from exc
 expected.append(dict(active=entry is not None,counter=get(0x438af8),pixels=list(u.mem_read(0x1000000,1920))))
if not a.native:print(len(cases),'Original main-mode HUD cases captured');raise SystemExit(0)
actual=json.loads(subprocess.run([a.native,str(directory/'MEAN.DAT'),str(directory/'MAIN.DAT')],input=json.dumps(cases),capture_output=True,text=True,check=True).stdout)
assert len(actual)==len(expected)
for n,(x,y) in enumerate(zip(expected,actual)):
 if x!=y:
  differing=[(i,v,y['pixels'][i]) for i,v in enumerate(x['pixels']) if y['pixels'][i]!=v]
  raise AssertionError((n,cases[n],x['counter'],y['counter'],differing[:12],len(differing)))
report=dict(entries={str(k):hex(v) for k,v in entries.items()},speed_entry='0x413c94',image_sha256=hashlib.sha256(image).hexdigest(),mean_dat_sha256=hashlib.sha256(mean).hexdigest(),main_dat_sha256=hashlib.sha256(main).hexdigest(),scope='Actual bitmap3c, small numeric44 and clear4c services; full1920 pixels/counter exact; Formula selection3 is no-op here, separate minigame renderer; scheduler excluded',verified_cases=len(cases),cases=cases)
(root/'analysis/traces/mean-main-mode-hud-original.json').write_text(json.dumps(report,indent=2)+'\n');print(len(cases),'Original/native main-mode HUD pixel/counter cases exact')
