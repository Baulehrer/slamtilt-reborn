#!/usr/bin/env python3
"""Bounded original reset/background request proof; no mocked tracker semantics."""
import hashlib,json,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESP,UC_X86_REG_EIP
root=Path(__file__).resolve().parents[1]
image=(root/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
calls=[]
def hook(uc,a,n,c):
 if a in [0x419d9b,0x41957c,0x100fff0]:uc.emu_stop()
 if a==0x1000600:
  calls.append(dict(service=service,order=uc.reg_read(UC_X86_REG_EAX),bank=uc.reg_read(UC_X86_REG_EDX)))
  sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,hook)
put(0x43f0d0,0x1001000);put(0x1001090,0x1000600);put(0x1001088,0x1000600)
results=[]
for service,start in [(0x90,0x419d88),(0x88,0x419561)]:
 calls.clear();put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000)
 u.emu_start(start,0x100fff0,count=20)
 assert calls==[dict(service=service,order=4 if service==0x90 else 49,bank=0 if service==0x90 else 1)],calls
 results.append(dict(start=hex(start),requests=list(calls)))
for order,bank in [(0,0),(4,0),(23,0),(49,1),(79,0)]:
 u.reg_write(UC_X86_REG_ESP,0x100f000);put(0x100f000,0x100fff0)
 u.reg_write(UC_X86_REG_EAX,order);u.reg_write(UC_X86_REG_EDX,bank)
 for address in [0x4297b4,0x4297b0,0x4297bc]:put(address,0x12345678)
 u.emu_start(0x405824,0x100fff0,count=30)
 state={hex(a):get(a) for a in [0x4297c4,0x4297c8,0x42979c,0x429798,0x4297b4,0x4297b0,0x4297bc]}
 assert list(state.values())==[order,bank,order,bank,0,0xffffffff,0xffffffff]
 results.append(dict(service90_input=[order,bank],state=state))
report=dict(image_sha256=hashlib.sha256(image).hexdigest(),confidence='VERIFIED_BOUNDED',cases=results)
(root/'analysis/traces/mean-audio-base-original.json').write_text(json.dumps(report,indent=2)+'\n')
print('7 original reset/bonus/request90 cases passed')
