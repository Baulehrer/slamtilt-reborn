#!/usr/bin/env python3
"""Original414970 player/ball/score/prelaunch HUD with actual display services."""
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
for ad,value in [(0x43e3e8,0x1000000),(0x43e82c,0x1010000),(0x43efd8,0x1100000),(0x43f068,0x1002000),(0x43f0d0,0x1003000),(0x1003010,0x1006000),(0x100303c,0x406680),(0x1003040,0x406280),(0x1003044,0x40617c),(0x1003048,0x4060f8),(0x100304c,0x4060a4)]:put(ad,value)
cases=[]
def case(**kw):
 c=dict(counter=0,field_engine_5c=0,field_engine_60=0,field_engine_04=1,field_engine_08=1,field_360=100,field_35c=0,field_358=0,field_206=0,field_362=0,player_0e=1,score=0,steps=1)
 c.update(kw);cases.append(c)
# All supported choices, both blink phases, actual player/ball and score pages.
for selection in [0,0x7fff,0xffff]:
 for tier in range(8):
  for reward in range(7):
   for counter in [0,1,63,64,125,126,127,0xffffffff]:
    case(counter=counter,field_358=selection,field_206=tier,field_362=reward,score=194839960,player_0e=3,field_engine_04=4)
# Active Skillshot supersedes countdown and player page.
for selection in [0,0xffff]:
 for index in range(8 if selection==0 else 7):
  case(field_35c=0xffff,field_358=selection,field_206=index if selection==0 else 0,field_362=index if selection else 0,field_engine_60=1,steps=8)
# Countdown signed boundary, wrapping counter and retained packed scratch across calls.
for counter in [0,1,2,125,126,127,0x7fffffff,0xffffffff]:
 for countdown in [-32768,-1,0,1,100,32767]:
  case(counter=counter,field_engine_60=1,field_360=countdown,steps=106 if countdown==100 else 4)
# Engine5c branch does not increment counter, including arbitrary decimal widths.
for player,ball,balls in [(1,1,3),(2,2,4),(4,99,127),(12,123,1000)]:
 for counter in [0,127,0xffffffff]:
  case(counter=counter,field_engine_5c=1,player_0e=player,field_engine_04=ball,field_engine_08=balls,steps=2)
# Score requires real packed-BCD score and live scratch suffix (clear loop119 DWORDs).
for score in [0,9,10,999,1000,123456789,999999999999]:
 case(counter=62,score=score,steps=132)
expected=[]
for c in cases:
 put(0x438af8,c['counter'])
 for off,name in [(0x360,'field_360'),(0x35c,'field_35c'),(0x358,'field_358'),(0x206,'field_206'),(0x362,'field_362')]:word(0x43f000+off,c[name])
 for off,name in [(0x5c,'field_engine_5c'),(0x60,'field_engine_60'),(4,'field_engine_04'),(8,'field_engine_08')]:put(0x1002000+off,c[name])
 digits=f'{c["score"]:012d}';u.mem_write(0x1006000,bytes(int(digits[i:i+2],16) for i in range(0,12,2)));word(0x100600e,c['player_0e'])
 u.mem_write(0x1000000,bytes(i%4 for i in range(1920)));u.mem_write(0x43ec3c,bytes((i*13+i//12)%256 for i in range(480)))
 frames=[]
 for tick in range(c['steps']):
  call(0x414970)
  frames.append(dict(counter=get(0x438af8),field_360=struct.unpack('<h',u.mem_read(0x43f360,2))[0],pixels=list(u.mem_read(0x1000000,1920)),scratch=list(u.mem_read(0x43ec3c,480)),valid=True))
 expected.append(frames)
if not a.native:print(sum(map(len,expected)),'Original player HUD frames captured');raise SystemExit(0)
actual=json.loads(subprocess.run([a.native,str(directory/'MEAN.DAT'),str(directory/'MAIN.DAT')],input=json.dumps(cases),capture_output=True,text=True,check=True).stdout)
assert len(actual)==len(expected)
for n,(x,y) in enumerate(zip(expected,actual)):
 assert len(x)==len(y),(n,len(x),len(y))
 for tick,(original,native) in enumerate(zip(x,y)):
  if original!=native:
   keys=[k for k in original if original[k]!=native[k]]
   diff={k:[(i,v,native[k][i]) for i,v in enumerate(original[k]) if v!=native[k][i]][:12] if isinstance(original[k],list) else (original[k],native[k]) for k in keys}
   raise AssertionError((n,tick,cases[n],diff))
report=dict(entry='0x414970',image_sha256=hashlib.sha256(image).hexdigest(),mean_dat_sha256=hashlib.sha256(mean).hexdigest(),main_dat_sha256=hashlib.sha256(main).hexdigest(),scope='Actual414970 including41455c,414b60 and bitmap3c/numeric44/text48/fill4c services; pixels, packed scratch, counter and WORD360 exact; scheduler excluded',verified_cases=sum(map(len,expected)),series=len(cases),cases=cases)
(root/'analysis/traces/mean-player-hud-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['verified_cases'],'Original/native player HUD frames exact')
