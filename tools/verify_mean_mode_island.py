#!/usr/bin/env python3
"""Original timer, mode selection and terminal award vs native; bounded services."""
from pathlib import Path
import json,subprocess
exec((Path(__file__).parent/'trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
from unicorn.x86_const import UC_X86_REG_EBP,UC_X86_REG_ECX
# Score service separated from notification; reset/lamp routines execute unchanged.
put(0x1002058,0x200ff20)
awards=[]
def score_hook(uc,a,n,c):
 awards.append(uc.reg_read(UC_X86_REG_EAX));sp=uc.reg_read(UC_X86_REG_ESP)
 uc.reg_write(UC_X86_REG_EIP,get(sp)&0xffffffff);uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,score_hook,begin=0x200ff20,end=0x200ff20)
cases=[dict(operation='clock',timer=t) for t in [*range(-3,1003),8400,32767,-32768]]
cases += [dict(operation='clock',timer=t,selected=s,award=12345678) for s in [1,2] for t in [*range(-3,1003),9400,6400,32767,-32768]]
cases += [dict(operation='reset',selected=i,mask=mask,guard=g) for i in range(5) for mask in range(32) for g in [-1,0,1]]
cases += [dict(operation='award',award=a,counter=c) for a in [10000000,75000000] for c in [0,1,2,32767]]
cases += [dict(operation='cycle',award=a,counter=2) for a in [10000000,75000000]]
cases += [dict(operation=op,selected=s,award=75000000,counter=2) for s in [1,2] for op in ['award','cycle']]
expected=[]
for c in cases:
 put(0x438b68,-1);put(0x438b6c,100);put(0x438b70,0);put(0x438b74,-1);put(0x438b78,0);put(0x438b7c,0);put(0x43f364,0);put(0x43f392,0);put(0x43f204,0)
 put(0x1001030,5);put(0x43f05c,c.get('award',0));put(0x43f058,20000000)
 for address,value in [(0x43f39c,c.get('timer',8400)),(0x43f3b4,c.get('counter',2)),(0x43f366,123),(0x43f1e6,c.get('selected',0)),(0x43f384,c.get('guard',0)),(0x43f380,-1)]:u.mem_write(address,struct.pack('<H',value&65535))
 u.mem_write(0x43f1e0,bytes((c.get('mask',1)>>i)&1 for i in range(5)))
 b=bytearray(100);struct.pack_into('<ii',b,0,26*65536,279*65536);struct.pack_into('<HH',b,0x58,3,2);u.mem_write(0x1000000,bytes(b));awards.clear()
 put(0x200f000,0x200fff0)
 op=c['operation']
 if op in ('award','cycle'):
  u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);start=0x415330
 else:
  u.mem_write(0x200efe8,bytes(24));u.reg_write(UC_X86_REG_ESP,0x200efe8)
  u.reg_write(UC_X86_REG_EBP,5);u.reg_write(UC_X86_REG_ECX,0x1001000)
  start=0x414e79 if op=='clock' else 0x41635f
 steps=1
 if op=='cycle':
  u.mem_write(0x43f380,struct.pack('<h',50))
  for steps in range(1,401):
   put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000)
   u.emu_start(0x415330,0x200fff0,count=20000)
   if steps%4==0:
    for address in [0x438b68,0x438b74]:
     if get(address)>=0:put(address,get(address)-1)
   if word(0x1000058)==2:break
 else:
  u.emu_start(start,0x200fff0,count=20000)
 expected.append(dict(steps=steps,award=get(0x43f05c)&0xffffffff,timer=word(0x43f39c),mode=get(0x1001030),selected=word(0x43f1e6),counter=word(0x43f3b4),field366=word(0x43f366),sum=get(0x43f058)&0xffffffff,score=sum(awards),capture_timer=word(0x43f380),ball=list(u.mem_read(0x1000000,100))))
actual=json.loads(subprocess.check_output([str(ROOT/'build/native/mean_mode_island_probe')],input=json.dumps(cases),text=True))
diff=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
fixture=dict(scope='Original414e79 clock,41635f reset and415330 terminal award; reset/selection/lamp code executes; DMD/audio services bounded; no engine wrapper',cases=cases,expected=expected)
(ROOT/'analysis/traces/mean-mode-island-fixture.json').write_text(json.dumps(fixture,separators=(',',':'))+'\n')
report=dict(cases=len(cases),clock_cases=sum(c['operation']=='clock' for c in cases),selection_cases=480,award_cases=sum(c['operation']=='award' for c in cases),reset_cycle_cases=sum(c['operation']=='cycle' for c in cases),differences=diff)
(ROOT/'analysis/traces/mean-mode-island-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if diff:
 i=diff[0];print(cases[i],{k:(actual[i][k],expected[i][k]) for k in expected[i] if actual[i][k]!=expected[i][k]})
assert not diff and len(actual)==len(expected)
