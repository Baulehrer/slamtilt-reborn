#!/usr/bin/env python3
"""Actual408e70 coordinate/read and extra-plane loop, including row crossings."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import *
r=Path(__file__).resolve().parents[1]
exe=next((r/'build/corpus/win95/demo-1997').rglob('SLAMTILT.EXE'));datpath=next(exe.parent.rglob('MEAN.DAT'));dat=datpath.read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32)
u.mem_map(0x400000,0x100000);u.mem_write(0x400000,(r/'build/mean-prepared/pe-data.bin').read_bytes())
u.mem_map(0x1000000,0x10000);u.mem_map(0x1100000,(len(dat)+4095)&~4095);u.mem_write(0x1100000,dat);u.mem_map(0x2000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
put(0x4298c8,0x1000000);put(0x43e71c,0);put(0x43e410,0)
profiles=json.loads((r/'analysis/table-profiles.json').read_text())['tables']['mean']['layers']
cases=[];expected=[]
for p in profiles:
 for x in [-3,5,8,311,314,327]:
  for y in [-2,5,607,615,618,619]:
   c=dict(x=x,y=y,hit=p['hit_offset'],stride=p['stride'],planes=p['planes']);cases.append(c)
   put(0x1000000,x<<16);put(0x1000004,y<<16);put(0x1000040,0x1100000+c['hit']);put(0x100004c,c['stride']);put(0x1000050,c['planes'])
   u.reg_write(UC_X86_REG_EAX,0);u.reg_write(UC_X86_REG_ESP,0x200f000)
   u.emu_start(0x408e70,0x408ed5,count=100)
   hit=bool(u.reg_read(UC_X86_REG_EAX)&u.reg_read(UC_X86_REG_EDI))
   u.emu_start(0x408ede,0x408f0c,count=200)
   expected.append([hit,u.reg_read(UC_X86_REG_ESI)])
actual=json.loads(subprocess.check_output([sys.argv[1],str(datpath)],input=json.dumps(cases).encode()))
assert actual==expected,next(((i,a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b),None)
(r/'analysis/traces/mean-bitmap-linear-original.json').write_text(json.dumps(dict(scope=__doc__+'; synthetic queries, not whole physics',build_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),cases=len(cases),differences=0,records=[dict(input=c,output=e) for c,e in zip(cases,expected)]),separators=(',',':'))+'\n')
print('PASS',len(cases),'original bitmap/mask edge queries')
