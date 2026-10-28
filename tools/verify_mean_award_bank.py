#!/usr/bin/env python3
import argparse, json, struct, subprocess, hashlib
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import *
a=argparse.ArgumentParser();a.add_argument('--native',required=True);a=a.parse_args()
root=Path(__file__).resolve().parents[1];image=(root/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
callbacks=[]
def hook(uc,address,size,data):
 if address in [0x100fff0,0x41d0f5,0x41ceb3,0x41cf49,0x41cfde,0x41d074]:uc.emu_stop();return
 if address in [0x1000400,0x1000500,0x1000600,0x40f754,0x41d220]:
  sp=uc.reg_read(UC_X86_REG_ESP)
  if address==0x1000400:callbacks.append(get(sp+12))
  uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if address==0x1000400 else 8 if address==0x40f754 else 0))
u.hook_add(UC_HOOK_CODE,hook)
put(0x43f0d0,0x1003000);put(0x43f068,0x1002000)
for offset,target in [(0x34,0x1000400),(0x58,0x1000500),(0x84,0x1000600),(0x80,0x1000600)]:put(0x1003000+offset,target)
cases=[];expected=[]
for mask in range(32):
 for x in [22,23,44,45,159,160,274,275]:
  for mode in [2,4,5]:
   for timer in [-1,0]:cases.append(dict(kind='target',flags=[(mask>>i)&1 for i in range(5)],x=x*65536,mode=mode,timer=timer,value=12345))
for timer in [0,1,2,3,4,999,1000,1001,2999,3000,3001,5999,6000,32767]:
 cases.append(dict(kind='tick',flags=[0]*5,timer=timer,value=12345))
for c in cases:
 u.mem_write(0x43f1ec,bytes(c['flags']));u.mem_write(0x43f208,bytes([9,8,7,6])*63)
 u.mem_write(0x43f37a,struct.pack('<h',c['timer']));put(0x43f054,c['value']);put(0x1002030,c.get('mode',2));u.mem_write(0x43f1fc,b'\0\0')
 put(0x1001000,c.get('x',0));put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.reg_write(UC_X86_REG_EAX,0x1003000);u.reg_write(UC_X86_REG_ECX,0x1001000);u.reg_write(UC_X86_REG_EBX,450*65536);callbacks.clear()
 u.emu_start(0x4150b8 if c['kind']=='tick' else 0x41ce03,0x100fff0,count=1000)
 expected.append(dict(flags=list(u.mem_read(0x43f1ec,5)),timer=struct.unpack('<h',u.mem_read(0x43f37a,2))[0],value=get(0x43f054),lamps=[list(u.mem_read(0x43f28c+4*i,4)) for i in range(5)],lamp62=list(u.mem_read(0x43f300,4)),callback=callbacks[0] if callbacks else 0))
actual=json.loads(subprocess.run([a.native],input=json.dumps(cases),capture_output=True,text=True,check=True).stdout)
assert len(actual)==len(expected)
for i,(x,y) in enumerate(zip(expected,actual)):assert x==y,(i,cases[i],x,y)
(root/'analysis/traces/mean-award-bank-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='41ce03..41d0fa target chain plus41d294 and4150b8; score/service34 recorded,41d220 secondaryreward excluded',cases=cases,expected=expected),separators=(',',':'))+'\n')
print(len(cases),'original/native bank target/timer cases exact')
