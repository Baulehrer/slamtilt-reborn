#!/usr/bin/env python3
"""Compare Original41455c with native centered Skillshot DMD, actual bitmap/text services."""
import argparse, hashlib, json, struct, subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_ESP, UC_X86_REG_EIP
p=argparse.ArgumentParser(); p.add_argument('--native',required=True); a=p.parse_args()
r=Path(__file__).resolve().parents[1]
dat=next((r/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
mean=dat.read_bytes(); main=(dat.parent/'MAIN.DAT').read_bytes()
image=(r/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32)
u.mem_map(0x400000,0x100000); u.mem_write(0x400000,image)
u.mem_map(0x1000000,0x100000); u.mem_map(0x1100000,0x200000)
u.mem_write(0x1100000,mean); u.mem_write(0x1010000,main)
def put(ad,v): u.mem_write(ad,struct.pack('<I',v&0xffffffff))
def call(ad):
 put(0x10ff000,0x10ffff0); u.reg_write(UC_X86_REG_ESP,0x10ff000)
 u.emu_start(ad,0x10ffff0,count=100000)
 assert u.reg_read(UC_X86_REG_EIP)==0x10ffff0
call(0x40af14)
for ad,value in [(0x43e3e8,0x1000000),(0x43e82c,0x1010000),
                 (0x43efd8,0x1100000),(0x43f0d0,0x1003000),
                 (0x100303c,0x406680),(0x1003048,0x4060f8)]: put(ad,value)
cases=[]; expected=[]
for selection in [0,0x7fff,0xffff]:
 for index in range(8 if selection==0 else 7):
  for counter in [0,1,2,3,126,127,255,0x7fffffff,-1]:
   tier=index if selection==0 else 0
   reward=index if selection else 0
   case=dict(selection=selection,tier=tier,reward=reward,counter=counter)
   cases.append(case)
   put(0x438af8,counter)
   for off,value in [(0x358,selection),(0x206,tier),(0x362,reward)]:
    u.mem_write(0x43f000+off,struct.pack('<H',value))
   u.mem_write(0x1000000,bytes(i%4 for i in range(1920)))
   call(0x41455c)
   expected.append(dict(counter=struct.unpack('<i',u.mem_read(0x438af8,4))[0],
                        pixels=list(u.mem_read(0x1000000,1920)),valid=True))
active_count=len(cases)
# Original414b60 preserves scratch outside the two visible tile rectangles.
background=[(i*13+i//96)%4 for i in range(1920)]
packed=bytearray(480)
for i,value in enumerate(background):
 for plane in range(2):
  packed[plane*240+i//8] |= ((value>>plane)&1) << (7-i%8)
for selection in [0,0x7fff,0xffff]:
 for tier in range(8):
  for reward in range(7):
   for counter in [0,1,2,3]:
    cases.append(dict(pair=True,selection=selection,tier=tier,reward=reward,counter=counter))
    put(0x438af8,counter)
    for off,value in [(0x358,selection),(0x206,tier),(0x362,reward)]:
     u.mem_write(0x43f000+off,struct.pack('<H',value))
    u.mem_write(0x43ec3c,bytes(packed))
    u.mem_write(0x1000000,bytes(1920))
    call(0x414b60)
    expected.append(dict(counter=struct.unpack('<i',u.mem_read(0x438af8,4))[0],
                         pixels=list(u.mem_read(0x1000000,1920)),valid=True))
actual=json.loads(subprocess.run([a.native,str(dat)],input=json.dumps(cases),
                               capture_output=True,text=True,check=True).stdout)
assert len(actual)==len(expected)
for i,(x,y) in enumerate(zip(expected,actual)):
 assert x==y,(i,cases[i],[(j,v,y['pixels'][j]) for j,v in enumerate(x['pixels']) if v!=y['pixels'][j]][:20])
report=dict(scope='Original41455c active skillshot and414b60 prelaunch choicepair; actual406680 and4060f8 bitmap/text services; generic idle HUD/scheduler excluded',
            image_sha256=hashlib.sha256(image).hexdigest(),
            mean_dat_sha256=hashlib.sha256(mean).hexdigest(),
            main_dat_sha256=hashlib.sha256(main).hexdigest(),
            verified_cases=len(cases),active_cases=active_count,choice_pair_cases=len(cases)-active_count,cases=cases)
(r/'analysis/traces/mean-skillshot-display-original.json').write_text(json.dumps(report,indent=2)+'\n')
print(active_count,'active +',len(cases)-active_count,'choicepair original/native Skillshot pixel/counter cases exact')
