#!/usr/bin/env python3
"""Original bounded side-capture mode6 decisions, after preceding timer/service work."""
import itertools,json,struct
from pathlib import Path
exec((Path(__file__).parent/'trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
from unicorn.x86_const import UC_X86_REG_EBX,UC_X86_REG_ECX,UC_X86_REG_EDX
calls=[]
def service(uc,a,n,ctx):calls.append(hex(a));stub(uc,a,n,ctx)
u.hook_add(UC_HOOK_CODE,service,begin=0x416fe0,end=0x416fe0)
cases=[]
for cb,upper,left,right,count in itertools.product([2,4],[-1,0],[-1,0],[-1,0],[1,2,3,4]):
 for a,v in [(0x43f38e,upper),(0x43f368,left),(0x43f36c,right),(0x43f364,-1),(0x1000058,3)]:u.mem_write(a,struct.pack('<h',v))
 put(0x1001000,count);calls.clear();put(0x200f000,0x200fff0);u.mem_write(0x200efe8,bytes(24));u.reg_write(UC_X86_REG_ESP,0x200efe8)
 for reg,v in [(UC_X86_REG_EBX,6),(UC_X86_REG_ECX,6),(UC_X86_REG_EDX,0x1000000)]:u.reg_write(reg,v)
 u.emu_start(0x4163d4 if cb==2 else 0x41666a,0x200fff0,count=2000)
 cases.append(dict(input=[cb,upper,left,right,count],output=[word(0x1000058),word(0x43f38e),word(0x43f368),word(0x43f36c),word(0x43f364)],calls=calls.copy()))
 for_case=cases[-1];expected=[3,upper,left,right,-1]
 if sum(v>=0 for v in [upper,left,right])-count<-1:expected[0]=6;expected[2 if cb==2 else 3]=2000
 if cb==2:expected[4]=0
 assert expected==for_case['output'],for_case
(ROOT/'analysis/traces/mean-mode6-side-capture-fixture.json').write_text(json.dumps(dict(scope='Actual4163d4 cb2 and41666a cb4 post-timer branch;416fe0 observed then stubbed; preceding timer/scoring excluded',cases=cases),separators=(',',':'))+'\n')
print(json.dumps(dict(cases=len(cases))))
