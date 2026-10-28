#!/usr/bin/env python3
"""Bounded actual414e79 mode6 clock; stage2 spawn helper observed separately."""
import itertools,json,struct
from pathlib import Path
exec((Path(__file__).parent/'trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
from unicorn.x86_const import UC_X86_REG_EBP,UC_X86_REG_ECX
calls=[]
def observe(uc,a,n,ctx):calls.append(hex(a))
for a in [0x419da4,0x419f6c,0x4194e4,0x416fe0]:u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a)
def stage2(uc,a,n,ctx):
 calls.append(hex(a));stub(uc,a,n,ctx)
u.hook_add(UC_HOOK_CODE,stage2,begin=0x4151e4,end=0x4151e4)
for off in [0x80,0x84]:put(0x1002000+off,0x200ff00)
image=bytes(u.mem_read(0x400000,0x100000));runtime=bytes(u.mem_read(0x1000000,0x10000));cases=[]
for stage,timer,count,selected,flags in itertools.product([0,1,2,3],[-2,-1,0,1,2,800],[1,2],[0,4],[[0]*5,[1]*5]):
 u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime);put(0x1001030,6);put(0x1001000,count)
 for a,v in [(0x43f37e,stage),(0x43f376,timer),(0x43f1e6,selected),(0x43f384,0),(0x43f366,77),(0x43f37a,-1)]:u.mem_write(a,struct.pack('<h',v))
 u.mem_write(0x43f1e0,bytes(flags));calls.clear();put(0x200f000,0x200fff0);u.mem_write(0x200efe8,bytes(24));u.reg_write(UC_X86_REG_ESP,0x200efe8);u.reg_write(UC_X86_REG_EBP,6);u.reg_write(UC_X86_REG_ECX,0x1001000)
 u.emu_start(0x414e79,0x200fff0,count=20000)
 cases.append(dict(input=dict(stage=stage,timer=timer,count=count,selected=selected,flags=flags),output=dict(timer=word(0x43f376),mode=get(0x1001030),selected=word(0x43f1e6),field366=word(0x43f366),engine40=get(0x1001040),flags=list(u.mem_read(0x43f1e0,5))),calls=calls.copy()))
report=dict(scope='Actual414e79→41504f mode6; actual419da4 selection and419f6c/4194e4/416fe0 reset helpers. Stage2 helper4151e4 observed then stubbed because spawn already isolated.',cases=cases)
(ROOT/'analysis/traces/mean-mode6-clock-fixture.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
print(json.dumps(dict(cases=len(cases),reset_cases=sum(c['output']['mode']==2 for c in cases),example=next(c for c in cases if c['output']['mode']==2))))
