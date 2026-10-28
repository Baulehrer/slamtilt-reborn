#!/usr/bin/env python3
"""Actual417ae0 table warning/Tilt effects. External services recorded, not run."""
import json,struct,subprocess,sys,itertools
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
r=Path(__file__).resolve().parents[1];u=Uc(UC_ARCH_X86,UC_MODE_32)
u.mem_map(0x400000,0x100000);u.mem_map(0x1000000,0x10000);u.mem_write(0x400000,(r/'build/mean-prepared/pe-data.bin').read_bytes())
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<i',u.mem_read(a,4))[0]
put(0x43f0d0,0x1001000);put(0x43f068,0x1002000)
for slot in [0x34,0x84,0x8c]:put(0x1001000+slot,0x1003000+slot)
events=[];result=0
regs=[UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ECX,UC_X86_REG_EBX]
def hook(uc,a,n,c):
 global events
 if a not in [0x1003034,0x1003084,0x100308c,0x40f754]:return
 sp=uc.reg_read(UC_X86_REG_ESP);ret=get(sp)&0xffffffff
 if a==0x100308c:events.append([0x8c]);extra=0
 elif a==0x1003084:events.append([0x84]+[uc.reg_read(k) for k in regs[:2]]);extra=0
 else:
  extra=12 if a==0x1003034 else 8
  events.append([0x34 if extra==12 else a]+[uc.reg_read(k) for k in regs]+[[get(sp+4+i*4) for i in range(extra//4)]])
  if extra==12:uc.reg_write(UC_X86_REG_EAX,result&0xffffffff)
 uc.reg_write(UC_X86_REG_ESP,sp+4+extra);uc.reg_write(UC_X86_REG_EIP,ret)
u.hook_add(UC_HOOK_CODE,hook)
cases=list(itertools.product([0,1,-1,2],[0,-1,255],[0,1,99],[0,-1,255]));expected=[]
for eax,f038,f14,result in cases:
 events=[];put(0x43f038,f038);put(0x1002014,f14);put(0x100f000,0x100fff0)
 for reg in regs:u.reg_write(reg,0x777)
 u.reg_write(UC_X86_REG_EAX,eax&0xffffffff);u.reg_write(UC_X86_REG_ESP,0x100f000);u.emu_start(0x417ae0,0x100fff0,count=200)
 expected.append([get(0x43f038),get(0x1002014),events])
actual=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases),text=True));assert actual==expected
(r/'analysis/traces/mean-nudge-table-original.json').write_text(json.dumps({'scope':__doc__,'cases':len(cases),'target':'0x417ae0','pointer_graph':['0x43e740','0x438ae4+4','0x4388d4+8','0x43f304+4'],'initializer':'0x40f0af/0x40f10c','limits':'Services34/84/8c and helper40f754 recorded only; no captured-ball state writes in bounded callback'},indent=2)+'\n');print('PASS',len(cases),'table callback contexts')
