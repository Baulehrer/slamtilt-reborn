#!/usr/bin/env python3
"""Original mode6 capture boundaries; transfer/lamp reset observed then stubbed."""
import itertools,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
exec((ROOT/'tools/trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_ESP
requests=[]
def service(uc,a,n,ctx):
 requests.append(hex(a));sp=uc.reg_read(UC_X86_REG_ESP)
 uc.reg_write(UC_X86_REG_EIP,struct.unpack('<I',uc.mem_read(sp,4))[0]);uc.reg_write(UC_X86_REG_ESP,sp+4)
for a in [0x417068,0x416b28,0x416fe0]:u.hook_add(UC_HOOK_CODE,service,begin=a,end=a)
image=bytes(u.mem_read(0x400000,0x100000));runtime=bytes(u.mem_read(0x1000000,0x10000))
cases=[]
for state,cb,upper,left,right,count,timer in itertools.product([3,6],[1,2,4],[-2,-1,0,1,2000],[-1,0],[-1,0],[1,2,3],[-2,-1]):
 if state==3 and cb!=1:continue
 u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime)
 b=bytearray(100);struct.pack_into('<HH',b,88,state,cb);u.mem_write(0x1000000,bytes(b))
 put(0x1001030,6);put(0x1001000,count);put(0x100201c,0)
 for a,v in [(0x43f38e,upper),(0x43f368,left),(0x43f36c,right),(0x43f36a,timer),(0x43f364,0)]:u.mem_write(a,struct.pack('<h',v))
 requests.clear();put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000)
 u.emu_start(0x415330,0x200fff0,count=4000)
 cases.append(dict(input=[state,cb,upper,left,right,count,timer],output=[word(0x1000058),word(0x43f38e),word(0x43f368),word(0x43f36c),word(0x43f36a)],calls=requests.copy()))
# Ready upper slot has already completed; compare stage-specific actual branches.
ready=[]
for stage in [0,1,2,3]:
 u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime);b=bytearray(100);struct.pack_into('<HH',b,88,3,1);u.mem_write(0x1000000,bytes(b));put(0x1001030,6)
 for a,v in [(0x43f36a,-2),(0x43f37e,stage)]:u.mem_write(a,struct.pack('<h',v))
 for a,v in [(0x438b5c,-1),(0x438b60,0),(0x438b64,0)]:put(a,v)
 requests.clear();put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x415330,0x200fff0,count=4000)
 ready.append(dict(stage=stage,calls=requests.copy(),result_stage=word(0x43f37e),field_438b90=get(0x438b90),field_43f3ae=word(0x43f3ae),bytes_43f260=list(u.mem_read(0x43f260,4))))
payload=dict(scope='Original415330 mode6;417068/416b28 transfer and416fe0 lamp reset observed then stubbed; fields and call order exact',cases=cases,ready=ready)
(ROOT/'analysis/traces/mean-mode6-capture-fixture.json').write_text(json.dumps(payload,separators=(',',':'))+'\n')
print(json.dumps(dict(cases=len(cases),ready=ready)))
