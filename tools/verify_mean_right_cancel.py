#!/usr/bin/env python3
"""Actual armed-route cancellation41c611 with actual416fe0 gate updates."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP,UC_X86_REG_EIP
r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
events={};service_result=0
service=0x1000400;engine=0x1002000;api=0x1003000
put(api+0x34,service)
def hook(uc,a,n,c):
 if a in [0x41c6de,0x41c8af]:uc.emu_stop();return
 if a in [service,0x40f754]:
  sp=uc.reg_read(UC_X86_REG_ESP)
  if a==service:
   events['cancelled']=True;events['callback']=get(sp+12)
   uc.reg_write(UC_X86_REG_EAX,service_result)
  uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if a==service else 8))
u.hook_add(UC_HOOK_CODE,hook);cases=[];expected=[]
for mode in [1,2,3,4]:
 for armed in [0,1,0xffff]:
  for counter in [0,1,0x7fff,0xfff8,0xffff]:
   for service_result in [0,0x12345678,0xffffffff]:
    raw=bytearray((i*37+19)&255 for i in range(0x3c0))
    struct.pack_into('<H',raw,0x3a2,armed);struct.pack_into('<H',raw,0x38a,counter);struct.pack_into('<I',raw,0x68,engine)
    c=dict(fields=list(raw),mode=mode,b2c=17,b34=19,service_result=service_result);cases.append(c)
    u.mem_write(0x43f000,bytes(raw));put(engine+0x30,mode);put(0x438b2c,17);put(0x438b34,19)
    events=dict(cancelled=False,callback=0)
    u.reg_write(UC_X86_REG_EAX,api);u.reg_write(UC_X86_REG_ESP,0x100f000)
    u.emu_start(0x41c611,0,count=1000)
    expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),b2c=struct.unpack('<i',u.mem_read(0x438b2c,4))[0],b34=struct.unpack('<i',u.mem_read(0x438b34,4))[0],**events))
if len(sys.argv)>1:probe=Path(sys.argv[1])
else:
 probe=r/'build/oracle/mean_right_cancel_probe'
 subprocess.run(['c++','-std=c++17','-Isrc','-Ibuild/native/_deps/json-src/include','tests/mean_right_cancel_probe.cpp','src/rules/mean_right_cancel.cpp','src/physics/mean_right_gate.cpp','src/physics/mean_step.cpp','src/physics/mean_material_bundle.cpp','-o',str(probe)],cwd=r,check=True)
actual=json.loads(subprocess.check_output([str(probe)],input=json.dumps(cases),text=True))
for i,(a,b) in enumerate(zip(actual,expected)):
 if a!=b:
  print('FAIL',i,{k:(a[k],b[k]) for k in a if k!='fields' and a[k]!=b[k]},[(hex(o),x,y) for o,(x,y) in enumerate(zip(a['fields'],b['fields'])) if x!=y]);raise SystemExit(1)
assert len(actual)==len(expected)
(r/'analysis/traces/mean-right-cancel-original.json').write_text(json.dumps(dict(prepared_sha256=hashlib.sha256(image).hexdigest(),scope='Actual41c611..41c6d9 with actual416fe0 gate, modes1..4. External scheduler34 return explicit, DMD40f754 stubbed. Caller owns layer1mask1/y<60.',cases=len(cases),differences=0,records=[dict(input=c,output=e) for c,e in zip(cases,expected)]),separators=(',',':'))+'\n')
print('PASS',len(cases),'original cancellation states byteexact')
