#!/usr/bin/env python3
"""Actual4172a8 Return callback; service34 admission and40f754 are recorded boundaries."""
import json,struct,subprocess,sys,hashlib,itertools
from pathlib import Path
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_32)
u.mem_map(0x400000,0x100000);u.mem_map(0x1000000,0x10000);u.mem_write(0x400000,image)
def put(a,v,n=4):u.mem_write(a,int(v&((1<<(n*8))-1)).to_bytes(n,'little'))
def get(a,n=4,signed=False):return int.from_bytes(u.mem_read(a,n),'little',signed=signed)
put(0x43f068,0x1000100);put(0x43f0d0,0x1000200);put(0x1000234,0x100fff0);u.mem_write(0x100fff0,b'\xc3')
events=[];admission=0
regs=[UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ECX,UC_X86_REG_EBX]
def hook(uc,a,n,c):
 if a not in [0x100fff0,0x40f754]:return
 sp=uc.reg_read(UC_X86_REG_ESP);stack=[get(sp+4+i*4,4,True) for i in range(3 if a==0x100fff0 else 2)]
 events.append([0x34 if a==0x100fff0 else a,*[uc.reg_read(x) for x in regs],stack])
 uc.reg_write(UC_X86_REG_EAX,admission if a==0x100fff0 else 0);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+len(stack)*4)
u.hook_add(UC_HOOK_CODE,hook)
cases=[];expected=[]
for svc,mode,eng44,locked,a6,a9,ret in itertools.product([0,1],[-1,1,2,3,4,5,6],[0,1],[0,0xffff],[0,1],[0,3],[0,1]):
 c=[svc,mode,eng44,locked,a6,a9,0,10,1234,5678,ret,0x24000];cases.append(c);admission=ret;events.clear()
 for a,v,n in [(0x100021c,svc,4),(0x1000130,mode,4),(0x1000144,eng44,4),(0x43f384,locked,2),(0x43f3a6,a6,2),(0x43f39e,a9,2),(0x43f3a8,0,2),(0x43f030,10,4),(0x43f064,1234,4),(0x43f038,5678,4),(0x43f1e4,0,4),(0x438bdc,0x24000,4)]:put(a,v,n)
 u.mem_write(0x43f2bc,bytes([9,8,7,6]));put(0x100f000,0x100ffe0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.emu_start(0x4172a8,0x100ffe0,count=2000)
 expected.append([get(0x43f384,2),get(0x43f39e,2),get(0x43f064,4,True),get(0x43f038,4,True),list(u.mem_read(0x43f2bc,4)),list(events)])
actual=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases),text=True))
for i,(a,e) in enumerate(zip(actual,expected)):
 if a!=e:raise AssertionError((cases[i],a,e))
(r/'analysis/traces/mean-mode-lock-original.json').write_text(json.dumps(dict(scope=__doc__,cases=len(cases),image_sha256=hashlib.sha256(image).hexdigest(),callback='0x4172a8',keyboard='0x404404 Return -> descriptor+40',limitations='Service34 and40f754 side effects caller-owned; mode4 zero divisor preserves original failure; indexed438bdc supplied from original table'),indent=2)+'\n');print('PASS',len(cases),'Original Return Mode Lock cases')
