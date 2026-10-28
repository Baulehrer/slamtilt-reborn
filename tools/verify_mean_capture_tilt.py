#!/usr/bin/env python3
"""Actual415330 Tilt callback2/3 release before continued timer/slot logic."""
import json,struct,subprocess,sys,itertools,random,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
exec((R/'tools/verify_mean_capture_tick.py').read_text().split('b=bytearray(100)')[0])
base=bytes(u.mem_read(0x400000,0x100000));samples=[]
def sample(uc,a,n,c):
 if a==0x200ff00 and uc.reg_read(UC_X86_REG_EAX)==0x437dec:samples.append([uc.reg_read(UC_X86_REG_EDX),uc.reg_read(UC_X86_REG_EBX)])
u.hook_add(UC_HOOK_CODE,sample,begin=0x200ff00,end=0x200ff00)
from unicorn.x86_const import UC_X86_REG_EDX,UC_X86_REG_EBX
rng=random.Random(0x416d08);cases=[];expected=[]
for cb,timer,delay2,delay3,occupied in itertools.product([2,3],[1,2,50,-3,-4,-10],[-1,0,1,5],[0,1,7],[-1,0]):
 u.mem_write(0x400000,base);put(0x100201c,1);put(0x1001030,2);samples.clear()
 b=bytearray(rng.randbytes(100));struct.pack_into('<HH',b,0x58,3,cb)
 slots2=[-1,delay2,0];slots3=[occupied,delay3,0];slot50=[0,0,0]
 for a,v in [(0x438b68,slots2),(0x438b74,slots3),(0x438b50,slot50)]:u.mem_write(a,struct.pack('<3i',*v))
 u.mem_write(0x43f380,struct.pack('<h',timer));u.mem_write(0x43f364,b'\0\0');u.mem_write(0x43f392,b'\0\0');u.mem_write(0x1000000,bytes(b))
 put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x415330,0x200fff0,count=6000)
 assert u.reg_read(UC_X86_REG_EIP)==0x200fff0
 assert all(x==[6,5] for x in samples),samples
 cases.append(dict(ball=list(b),slot2=slots2,slot3=slots3,timer=timer,gate=0));expected.append(dict(ball=list(u.mem_read(0x1000000,100)),slot2=list(struct.unpack('<3i',u.mem_read(0x438b68,12))),slot3=list(struct.unpack('<3i',u.mem_read(0x438b74,12))),slot50=list(struct.unpack('<3i',u.mem_read(0x438b50,12))),timer=word(0x43f380),gate=word(0x43f364),samples=len(samples)))
actual=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases),text=True));assert len(actual)==len(expected)
for i,(a,b) in enumerate(zip(actual,expected)):
 if a!=b:raise AssertionError((i,{k:(a[k],b[k]) for k in a if a[k]!=b[k]}))
(R/'analysis/traces/mean-capture-tilt-original.json').write_text(json.dumps(dict(scope=__doc__,cases=len(cases),image_sha256=hashlib.sha256(base).hexdigest(),limits='Mode2,cb2/3,positive or <=-3 timers; score/DMD rule-boundary ticks excluded; original helper/register sound parameters known437dec/6/5; actual415330with cached geometry pointers, services58/5c adapted; other callbacks excluded'),indent=2)+'\n');print('PASS',len(cases),'Tilt capture2/3 original/native cases')
