#!/usr/bin/env python3
"""Actual40554c common effects; table callback+4 recorded, not implemented."""
import json,struct,subprocess,sys,hashlib
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000)]:u.mem_map(a,n)
u.mem_write(0x400000,image)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<i',u.mem_read(a,4))[0]
put(0x43e740,0x1000000);put(0x1000004,0x1000100);put(0x1000008,0x1000200);put(0x1000108,0x1000300);put(0x1000204,0x1000400);put(0x1000304,0x100fff0)
callback=[-1]
def hook(uc,a,n,c):callback[0]=uc.reg_read(UC_X86_REG_EAX)
u.hook_add(UC_HOOK_CODE,hook,begin=0x100fff0,end=0x100fff0);u.mem_write(0x100fff0,b'\xc3')
fields=[0x43d864,0x43e7a0,0x43e7d4,0x43e7c4,0x43e7c8,0x4298b8,0x4298bc,0x4298c0];cases=[];expected=[]
for mode in [-1,0,1,2,3,4,5,6]:
 for tilted in [0,1]:
  for value in [-2147483648,-1,0,1,2,40,41,42,80,81,2147483640]:
   for count in [0,1,8]:
    vals=[tilted,mode,value,17,19,21,23,25];status=list(range(8));callback[0]=-1
    for a,v in zip(fields,vals):put(a,v)
    put(0x43e798,count)
    for i,v in enumerate(status):put(0x1000400+i*4,v)
    put(0x100f000,0x100ffe0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.emu_start(0x40554c,0x100ffe0,count=1000)
    cases.append(dict(fields=vals,count=count,status=status));expected.append(dict(fields=[get(a) for a in fields],status=[u.mem_read(0x1000400+i*4,1)[0] for i in range(8)],callback=callback[0]))
actual=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases),text=True));assert actual==expected
(r/'analysis/traces/mean-nudge-tilt-original.json').write_text(json.dumps(dict(scope=__doc__,cases=len(cases),image_sha256=hashlib.sha256(image).hexdigest(),address='0x40554c..0x405609',limits='Table callback warning/tilt presentation, captured-ball consequences and new-ball reset integration remain unverified'),indent=2)+'\n');print('PASS',len(cases),'original common tilt cases')
