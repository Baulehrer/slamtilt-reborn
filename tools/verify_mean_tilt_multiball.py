#!/usr/bin/env python3
"""Actual415330 callback5 Tilt release + continuation; no physics/startup claim."""
import json, struct, subprocess, sys, hashlib
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EDX, UC_X86_REG_EBX, UC_X86_REG_ESP
ROOT = Path(__file__).resolve().parents[1]
exec((ROOT/'tools/trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
image = bytes(u.mem_read(0x400000, 0x100000))
runtime = bytes(u.mem_read(0x1000000, 0x10000))
samples = []
def observe(uc,a,n,c):
    if uc.reg_read(UC_X86_REG_EAX) == 0x437dec:
        samples.append([uc.reg_read(UC_X86_REG_EDX), uc.reg_read(UC_X86_REG_EBX)])
u.hook_add(UC_HOOK_CODE,observe,begin=0x200ff00,end=0x200ff00)
cases=[];expected=[]
for mode,selected,flag in [(2,0,0),(5,0,0),(5,4,0),(6,4,0),(6,4,1)]:
    for secondary,tertiary in [(3,2),(2,0),(1,0),(0,2),(0,1),(0,0),(-1,0)]:
        for tilt in [False,True]:
            u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime)
            ball=bytearray((i*11+7)%256 for i in range(100));struct.pack_into('<HH',ball,0x58,3,5)
            u.mem_write(0x1000000,bytes(ball));put(0x1001030,mode);put(0x100201c,int(tilt))
            u.mem_write(0x43f1e6,struct.pack('<h',selected));u.mem_write(0x43f382,struct.pack('<h',flag));u.mem_write(0x43f3a6,struct.pack('<h',flag));u.mem_write(0x43f39e,b'\0\0');put(0x43f064,0x12345)
            for i,v in enumerate([19,secondary,tertiary]):put(0x438b8c+i*4,v)
            case=dict(op='release',ball=list(ball),mode=mode,selected=selected,flag=flag,bits=0,secondary=secondary,tertiary=tertiary,tilt=tilt)
            states=[]
            for tick in range(8):
                samples.clear();put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000)
                u.emu_start(0x415330,0x200fff0,count=10000)
                assert all(x==[6,5] for x in samples),samples
                states.append(dict(tick=tick+1,ball=list(u.mem_read(0x1000000,100)),slot=[get(0x438b8c+i*4) for i in range(3)],bits=word(0x43f39e),slot50=[get(0x438b50+i*4) for i in range(3)],samples=len(samples)))
                if word(0x1000058)==2:break
            cases.append(case);expected.append(states)
actual=json.loads(subprocess.check_output([sys.argv[1],str(ROOT/'build/mean-prepared/pe-data.bin'),str(ROOT/'build/mean-prepared/lookup.bin')],input=json.dumps(cases),text=True))
for i,(a,b) in enumerate(zip(actual,expected)):
    assert a==b,(i,cases[i],a,b)
assert len(actual)==len(expected)
report=dict(scope=__doc__,image_sha256=hashlib.sha256((ROOT/'build/mean-prepared/pe-data.bin').read_bytes()).hexdigest(),cases=len(cases),states=sum(map(len,expected)),differences=0,records=[dict(input=c,steps=e) for c,e in zip(cases,expected)])
(ROOT/'analysis/traces/mean-tilt-multiball-original.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
print('PASS',len(cases),'cases',report['states'],'states')
