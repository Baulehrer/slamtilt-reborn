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
put(0x438b68,-1);put(0x438b6c,100);put(0x438b70,0)
put(0x438b74,-1);put(0x438b78,0);put(0x438b7c,0)
u.mem_write(0x43f380,struct.pack('<h',50))
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
struct.pack_into('<ii',b,0,26*65536,279*65536)
struct.pack_into('<HH',b,0x58,3,2)
u.mem_write(0x1000000,bytes(b));expected=[]
for tick in range(400):
 before=len(scores);put(0x200f000,0x200fff0)
 u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000)
 u.emu_start(0x415330,0x200fff0,count=4000)
 if tick%4==3:
  for address in [0x438b68,0x438b74]:
   if get(address)>=0:put(address,get(address)-1)
 expected.append(dict(ball=list(u.mem_read(0x1000000,100)),slot2=[get(0x438b68+i*4) for i in range(3)],slot3=[get(0x438b74+i*4) for i in range(3)],slot50=[get(0x438b50+i*4) for i in range(3)],timer=word(0x43f380),gate=word(0x43f364),field204=word(0x43f204),score=sum(scores[before:])))
 if word(0x1000058)==2:break
probe=ROOT/'build/oracle/mean_capture_tick_probe'
subprocess.run(['c++','-std=c++17','-Isrc','-Ibuild/native/_deps/json-src/include','tests/mean_capture_tick_probe.cpp','src/physics/mean_capture_tick.cpp','src/physics/mean_step.cpp','src/physics/mean_material_bundle.cpp','-o',str(probe)],cwd=ROOT,check=True)
actual=json.loads(subprocess.check_output([str(probe)],input=json.dumps({'ball':list(b)}),text=True))
diff=[i for i,(a,b) in enumerate(zip(expected,actual)) if a!=b]
report={'scope':'Original415330 callbacks2->3->active; engine integration/hold omitted; rule-only4161bb skipped after local writes;41b8d0 service stubbed; original416235..4162cc mode/gate branch executed; score service observed; display slot0 decremented every4 steps','steps':len(expected),'native_steps':len(actual),'differences':diff,'states':[{'tick':i+1,'state58':struct.unpack_from('<H',bytes(s['ball']),0x58)[0],'callback5a':struct.unpack_from('<H',bytes(s['ball']),0x5a)[0],'timer':s['timer'],'score':s['score']} for i,s in enumerate(expected) if i==0 or s['score'] or s['ball'][0x5a]!=expected[i-1]['ball'][0x5a] or s['ball'][0x58]!=expected[i-1]['ball'][0x58]]}
(ROOT/'analysis/traces/mean-capture-tick-validation.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'analysis/traces/mean-capture-release-cycle.json').write_text(json.dumps(expected,indent=2)+'\n')
print(json.dumps(report))
if diff:
 i=diff[0];print('first',i,{k:(expected[i][k],actual[i][k]) for k in expected[i] if expected[i][k]!=actual[i][k]})
assert not diff and len(actual)==len(expected) and expected[-1]['ball'][0x58]==2
