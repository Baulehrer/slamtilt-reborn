#!/usr/bin/env python3
"""Regression: original41cbc4 reward runs before right-progression mode test."""
import hashlib,json,struct,subprocess,sys,itertools
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_32)
u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
services=[0x419da4,0x419f6c,0x4194e4,0x4169e4]
def hook(uc,a,n,d):
 if a==0x41d0f5:uc.emu_stop();return
 if a not in services+[0x1000400,0x1000500,0x40f754,0x416fe0]:return
 sp=uc.reg_read(UC_X86_REG_ESP);extra=0
 if a==0x1000400:uc.reg_write(UC_X86_REG_EAX,0 if get(sp+12) in [0x411544,0x412df0] else returned);extra=12
 elif a==0x1000500:events['scores'].append(uc.reg_read(UC_X86_REG_EAX))
 elif a==0x40f754:extra=8
 elif a==0x416fe0:events['reset']=True
 else:events['services'][services.index(a)]=True
 uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+extra)
u.hook_add(UC_HOOK_CODE,hook);cases=[];expected=[]
for mode,selected,count,stage,timer in itertools.product([5,6],[1,2,4],[0,5],range(3),[-1,0]):
 f=bytearray(0x3c0);returned=0x1000123
 for o,v in [(0x1e6,selected),(0x372,count),(0x386,count),(0x388,1),(0x38c,4),(0x39c,2200),(0x3bc,stage),(0x3b0,timer),(0x39a,2),(0x1f2,4),(0x35e,-1),(0x368,0),(0x36c,-1),(0x38e,0)]:struct.pack_into('<H',f,o,v&65535)
 for j in range(6):struct.pack_into('<H',f,0x044+j*2,1)
 struct.pack_into('<I',f,0x068,0x1002000);struct.pack_into('<I',f,0x0d0,0x1003000)
 u.mem_write(0x43f000,bytes(f));put(0x1002030,mode);put(0x1003034,0x1000400);put(0x1003058,0x1000500)
 events=dict(scores=[],reset=False,services=[False]*4);sp=0x100f000
 for j in range(5):put(sp+j*4,0)
 put(sp+20,0x100fff0);u.reg_write(UC_X86_REG_ESP,sp);u.emu_start(0x41cb28,0x100fff0,count=3000);assert u.reg_read(UC_X86_REG_EIP) in [0x100fff0,0x41d0f5]
 cases.append(dict(fields=list(f),mode=mode,returned=returned));expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),mode=get(0x1002030),**events))
actual=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases),text=True));assert len(actual)==len(expected)
for i,(a,b) in enumerate(zip(actual,expected)):assert a==b,(i,{k:(a[k],b[k]) for k in a if a[k]!=b[k] and k!='fields'},[(hex(o),x,y) for o,(x,y) in enumerate(zip(a['fields'],b['fields'])) if x!=y])
(r/'analysis/traces/mean-right-common-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='41cb28 with actual41b8d0;external service adapters;Monster/Rally completionmode transition beforeprogression',cases=cases,expected=expected),separators=(',',':'))+'\n');print(len(cases),'combined reward/progression original states exact')
