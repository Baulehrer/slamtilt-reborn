#!/usr/bin/env python3
"""Actual415330 Tilt callback1 human1..3 and positive-timer modes4..6: earlyrelease then bounded timer/events."""
import json,struct,subprocess,sys,hashlib
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EDX,UC_X86_REG_EBX
ROOT=Path(__file__).resolve().parents[1]
exec((ROOT/'tools/trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
image=bytes(u.mem_read(0x400000,0x100000));runtime=bytes(u.mem_read(0x1000000,0x10000));samples=[]
def audio(uc,a,n,c):
 if uc.reg_read(UC_X86_REG_EAX)==0x437dec:samples.append([uc.reg_read(UC_X86_REG_EDX),uc.reg_read(UC_X86_REG_EBX)])
u.hook_add(UC_HOOK_CODE,audio,begin=0x200ff00,end=0x200ff00)
cases=[];expected=[]
for mode in [1,2,3,4,5,6]:
 for timer in ([-3,-2,-1,0,1,50] if mode<=3 else [1,50]):
  for gate in [0,-1]:
   for slot in [[-1,3,1],[-1,1,0],[-1,0,0]]:
    for random in [0,0xffffffff]:
     u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime);put(0x100201c,1);put(0x1001030,mode);put(0x100103c,random)
     for a,v in [(0x43f36a,timer),(0x43f364,gate),(0x43f394,0),(0x43f1f2,0),(0x43f200,0),(0x43f202,0),(0x43f1fa,0)]:u.mem_write(a,struct.pack('<h',v))
     for i,v in enumerate(slot):put(0x438b5c+i*4,v)
     put(0x1003008,0);ball=bytearray((i*11+7)%256 for i in range(100));struct.pack_into('<HH',ball,0x58,3,1);u.mem_write(0x1000000,bytes(ball))
     samples.clear();scores.clear();put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000)
     u.emu_start(0x415330,0x200fff0,count=10000)
     assert all(x==[6,5] for x in samples)
     cases.append(dict(mode=mode,timer=timer,gate=gate,slot=slot,random=random,ball=list(ball)))
     expected.append(dict(ball=list(u.mem_read(0x1000000,100)),timer=word(0x43f36a),gate=word(0x43f364),field394=word(0x43f394),field1f2=word(0x43f1f2),mode=get(0x1001030),slot=[get(0x438b5c+i*4) for i in range(3)],score=sum(scores),bonus=get(0x1003008),samples=len(samples)))
a=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases).encode()))
assert len(a)==len(expected)
for i,(x,y) in enumerate(zip(a,expected)):
 assert x==y,(i,cases[i],{k:(x[k],y[k]) for k in x if x[k]!=y[k]})
report=dict(scope=__doc__+'; raw fields36a/364/394/1f2 and slot exact; service34 presentation handle adapter; no full table mode5/6 entry claim',cases=len(cases),differences=0,image_sha256=hashlib.sha256((ROOT/'build/mean-prepared/pe-data.bin').read_bytes()).hexdigest(),records=[dict(input=c,output=e) for c,e in zip(cases,expected)])
(ROOT/'analysis/traces/mean-tilt-upper-capture-original.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
print('PASS',len(cases),'cases')
