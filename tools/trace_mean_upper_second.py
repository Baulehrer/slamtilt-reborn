#!/usr/bin/env python3
"""Full bounded human callback2->3->active cycle, excluding engine wrapper."""
import json, struct, subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ESP, UC_X86_REG_EIP
ROOT=Path(__file__).resolve().parents[1]
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000)]:u.mem_map(a,n)
u.mem_write(0x400000,(ROOT/'build/mean-prepared/pe-data.bin').read_bytes())
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<i',u.mem_read(a,4))[0]
def word(a):return struct.unpack('<h',u.mem_read(a,2))[0]
for layer,values in enumerate([(3,0x6040,0x959f6,0x9ba36,0xb3b36),(1,0x60e0,0xb98f6,0xbf9d6,0xcbb96)]):
 for i,v in enumerate(values):put(0x43f06c+layer*20+i*4,v+(0x1100000 if i>=2 else 0))
put(0x43f068,0x1001000);put(0x1001000,1);put(0x1001030,2)
put(0x43f0d0,0x1002000);put(0x1002010,0x1003000);put(0x1002014,0x1004000);put(0x1004000,0x1000000)
put(0x1002058,0x200ff00);put(0x100205c,0x200ff00)
put(0x438b5c,-1);put(0x438b60,100);put(0x438b64,0)
put(0x438b68,-1);put(0x438b6c,100);put(0x438b70,0)
put(0x438b74,-1);put(0x438b78,0);put(0x438b7c,0)
u.mem_write(0x43f36a,struct.pack('<h',50))
put(0x1002034,0x200ff10);put(0x1002084,0x200ff00)
def svc34(uc,a,n,ctx):
 sp=uc.reg_read(UC_X86_REG_ESP);target=struct.unpack('<I',uc.mem_read(sp,4))[0]
 uc.reg_write(UC_X86_REG_ESP,sp+16);uc.reg_write(UC_X86_REG_EAX,1);uc.reg_write(UC_X86_REG_EIP,target)
u.hook_add(UC_HOOK_CODE,svc34,begin=0x200ff10,end=0x200ff10)
scores=[]
def stub(uc,a,n,ctx):
 if uc.reg_read(UC_X86_REG_EAX)==500000:scores.append(500000)
 sp=uc.reg_read(UC_X86_REG_ESP);target=struct.unpack('<I',uc.mem_read(sp,4))[0]
 uc.reg_write(UC_X86_REG_ESP,sp+4);uc.reg_write(UC_X86_REG_EIP,target)
u.hook_add(UC_HOOK_CODE,stub,begin=0x200ff00,end=0x200ff00)
def skip_rules(uc,a,n,ctx):uc.reg_write(UC_X86_REG_EIP,0x4169db)
u.hook_add(UC_HOOK_CODE,skip_rules,begin=0x4161bb,end=0x4161bb)
u.hook_add(UC_HOOK_CODE,stub,begin=0x41b8d0,end=0x41b8d0)
b=bytearray(100)
struct.pack_into('<ii',b,0,14*65536,14*65536)
struct.pack_into('<HH',b,0x58,3,1)
u.mem_write(0x1000000,bytes(b));expected=[]
for tick in range(400):
 before=len(scores);put(0x200f000,0x200fff0)
 u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000)
 u.emu_start(0x415330,0x200fff0,count=4000)
 if tick%4==3:
  for address in [0x438b5c,0x438b68,0x438b74]:
   if get(address)>=0:put(address,get(address)-1)
 expected.append(dict(ball=list(u.mem_read(0x1000000,100)),slot2=[get(0x438b68+i*4) for i in range(3)],slot3=[get(0x438b74+i*4) for i in range(3)],slot50=[get(0x438b50+i*4) for i in range(3)],timer=word(0x43f36a),mode=get(0x1001030),field1f2=word(0x43f1f2),field394=word(0x43f394),slot1=[get(0x438b5c+i*4) for i in range(3)],gate=word(0x43f364),field204=word(0x43f204),score=sum(scores[before:])))
 if word(0x1000058)==2:break

put(0x438b5c,-1);put(0x438b60,100);put(0x438b64,0)
u.mem_write(0x43f36a,struct.pack('<h',50));u.mem_write(0x1000000,bytes(b));expected=[]
for tick in range(1000):
 before=len(scores);put(0x200f000,0x200fff0)
 u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000)
 u.emu_start(0x415330,0x200fff0,count=4000)
 if tick%4==3:
  for address in [0x438b5c,0x438b68,0x438b74]:
   if get(address)>=0:put(address,get(address)-1)
 expected.append(dict(ball=list(u.mem_read(0x1000000,100)),slot2=[get(0x438b68+i*4) for i in range(3)],slot3=[get(0x438b74+i*4) for i in range(3)],slot50=[get(0x438b50+i*4) for i in range(3)],timer=word(0x43f36a),mode=get(0x1001030),field1f2=word(0x43f1f2),field394=word(0x43f394),slot1=[get(0x438b5c+i*4) for i in range(3)],gate=word(0x43f364),field204=word(0x43f204),score=sum(scores[before:])))
 if word(0x1000058)==2:break

report={'scope':'Original415330 SECOND upper capture preservingfirstcycle field394=-1; service34 stubbed nonzero DMD handle with actual40f754 executed; score/sound services stubbed; no fabricated DMD completion; slot0 display every4steps','steps':len(expected),'states':[{'tick':i+1,'state':e['ball'][88],'callback':e['ball'][90],'timer':e['timer'],'mode':e['mode'],'field394':e['field394'],'slot1':e['slot1'],'score':e['score']} for i,e in enumerate(expected) if i==0 or any(e[k]!=expected[i-1][k] for k in ['mode','field394','score']) or e['ball'][90]!=expected[i-1]['ball'][90] or e['ball'][88]!=expected[i-1]['ball'][88]]}
(ROOT/'analysis/traces/mean-upper-second-original-cycle.json').write_text(json.dumps(expected,indent=2)+'\n')
(ROOT/'analysis/traces/mean-upper-second-original-summary.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
