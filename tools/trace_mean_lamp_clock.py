#!/usr/bin/env python3
import itertools,json,struct
from pathlib import Path
exec((Path(__file__).parent/'trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
from unicorn.x86_const import UC_X86_REG_EAX
for a,v in [(0x43d84c,0x1001000),(0x1001000,0x1002000),(0x43d850,0x1003000),(0x43e798,1),(0x43e7c0,0)]:put(a,v)
actions=[]
def render(uc,a,n,ctx):
 desc=uc.reg_read(UC_X86_REG_EAX);on=a==0x40a41c;actions.append(on);uc.mem_write(desc+8,struct.pack('<h',-1 if on else 0));stub(uc,a,n,ctx)
for a in [0x40a41c,0x40a654]:u.hook_add(UC_HOOK_CODE,render,begin=a,end=a)
cases=[]
for command,period,countdown,duration,on in itertools.product(range(7),[0,1,4],[0,1,4,128,255],[0,1,3],[False,True]):
 state=[command,period,countdown,duration];u.mem_write(0x1003000,bytes(state));u.mem_write(0x1002008,struct.pack('<h',-1 if on else 0));steps=[]
 for tick in range(8):
  actions.clear();put(0x43e72c,0);put(0x429ae8,0);put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.emu_start(0x408110,0x200fff0,count=1000)
  steps.append(dict(state=list(u.mem_read(0x1003000,4)),on=word(0x1002008)<0,update=bool(actions)))
 cases.append(dict(initial=state,on=on,steps=steps))
(ROOT/'analysis/traces/mean-lamp-clock-fixture.json').write_text(json.dumps(dict(scope='Actual408110 commandconsumer; actualon/off40a41c/40a654 pixelworkstubbed preservingregistersandwritingoriginaldescriptorWORD+8; one lamp periteration',cases=cases),separators=(',',':'))+'\n')
print(json.dumps(dict(cases=len(cases),states=len(cases)*8)))
