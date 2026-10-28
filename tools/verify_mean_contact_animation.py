#!/usr/bin/env python3
"""Compare418030 state and frame submissions including renderer busy gates."""
import json,struct,subprocess,random
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESP,UC_X86_REG_EIP
ROOT=Path(__file__).resolve().parents[1]
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000),(0x2100000,0x2000)]:u.mem_map(a,n)
u.mem_write(0x400000,(ROOT/'build/mean-prepared/pe-data.bin').read_bytes())
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
put(0x43f0d0,0x1002000);put(0x1002060,0x2101000)
submitted=[]
def submit(uc,a,n,c):
 submitted.append(uc.reg_read(UC_X86_REG_EDX));sp=uc.reg_read(UC_X86_REG_ESP)
 ret=struct.unpack('<I',uc.mem_read(sp,4))[0];uc.reg_write(UC_X86_REG_ESP,sp+4);uc.reg_write(UC_X86_REG_EIP,ret)
u.hook_add(UC_HOOK_CODE,submit,begin=0x2101000,end=0x2101000)
rng=random.Random(1996);cases=[];expected=[]
for repetitions in [2,3,4]:
 for busy in [False,True]:
  availability=[not busy or rng.random()>.35 for _ in range(60)]
  cases.append(dict(operation='animation',bytes=[0]*100,repetitions=repetitions,availability=availability))
  u.mem_write(0x1000000,struct.pack('<iii',0,0,repetitions));seq=[]
  for available in availability:
   u.mem_write(0x43820a,struct.pack('<h',-1 if available else 0));submitted.clear()
   put(0x200f000,0x2100000);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.reg_write(UC_X86_REG_EDX,0)
   u.emu_start(0x418030,0x2100000,count=1000)
   seq.append(list(struct.unpack('<iii',u.mem_read(0x1000000,12)))+[submitted[0] if submitted else -1])
  expected.append(seq)
p=ROOT/'build/oracle/contact-animation-cases.json';p.write_text(json.dumps(cases))
actual=json.loads(subprocess.check_output([str(ROOT/'build/native/mean_probe'),str(p),str(ROOT/'build/mean-prepared/lookup.bin')],text=True));assert actual==expected
report=dict(steps=360,differences=0,scope='Original418030 triplet and submissions, repetitions2/3/4, renderer available/busy; native renderer consumes submitted frame immediately')
(ROOT/'analysis/traces/mean-contact-animation-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
