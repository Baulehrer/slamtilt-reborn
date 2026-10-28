#!/usr/bin/env python3
"""Bounded 408b04 switch-dispatch boundary, synthetic bitmap planes."""
import hashlib,json,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP
r=Path(__file__).resolve().parents[1]
image=(r/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32)
u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image)
u.mem_map(0x1000000,0x300000)
def put(a,v):u.mem_write(a,struct.pack('<I',v))
ball=0x1000000;bitmap=0x1100000;desc=0x1200000;target=desc+0x100;stack=desc+0x1000;stop=desc+0x200
put(0x4298c8,ball);put(0x43e740,desc);put(desc+4,desc+0x20);put(desc+0x20,desc+0x40)
for layer in range(5):put(desc+0x40+4*layer,target)
u.mem_write(target,b'\xc3')
seen=[]
def hook(uc,a,n,c):
 if a==target:seen.append(a)
u.hook_add(UC_HOOK_CODE,hook,begin=target,end=target)
rows=[]
for solid in [False,True]:
 for mask in range(8):
  for previous in [0,1,3,7,0xffff]:
   for layer in [0,3]:
    b=bytearray(100)
    for off,val in [(0,273*65536),(4,288*65536),(0x40,bitmap),(0x4c,24640),(0x50,3)]:struct.pack_into('<I',b,off,val)
    struct.pack_into('<HH',b,0x38,previous,0x1234);struct.pack_into('<H',b,0x48,layer)
    u.mem_write(ball,bytes(b))
    idx=288*40+(273>>3);bit=0x80>>(273&7)
    for plane in range(4):u.mem_write(bitmap+idx+plane*24640,bytes([bit if (solid if plane==0 else bool(mask&(1<<(plane-1)))) else 0]))
    put(stack,stop);u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_EAX,0);seen.clear();u.emu_start(0x408b04,stop,count=500)
    actual_previous,actual_old=struct.unpack('<HH',u.mem_read(ball+0x38,4))
    expected=(previous,0x1234,False) if solid else (mask,previous,mask!=previous)
    actual=(actual_previous,actual_old,bool(seen));assert actual==expected,(solid,mask,previous,layer,actual,expected)
    rows.append(dict(solid=solid,mask=mask,previous=previous,layer=layer,dispatch=bool(seen),field38=actual_previous,field3a=actual_old))
out=dict(build_sha256='31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00',prepared_sha256=hashlib.sha256(image).hexdigest(),confidence='VERIFIED',addresses=dict(solid_skip='0x408b47..0x408b49',history='0x408b76..0x408b82',unchanged_skip='0x408b86..0x408b89',callback='0x408ba6',step_call='0x408a09'),scope='Original408b04, synthetic 3-plane bitmap and callback directory; verifies dispatch boundary and fields38/3a, not table callback effects or bitmap provenance',native_result='Matches native switch_step solid return and unchanged-mask return. No correction necessary.',cases=rows)
(r/'analysis/traces/mean-switch-boundary-original.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
print(f'PASS {len(rows)} original switch-boundary cases')
