#!/usr/bin/env python3
"""Verify launch init/action and layer material mutations against original x86."""
import json, random, struct, subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ESP
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'build/mean-prepared'
image=bytearray((base/'pe-data.bin').read_bytes());image.extend(bytes(0x100000-len(image)))
u=Uc(UC_ARCH_X86,UC_MODE_32)
for address,size in [(0x400000,0x100000),(0x1000000,0x400000),(0x2000000,0x10000),(0x2100000,0x2000)]:u.mem_map(address,size)
u.mem_write(0x400000,bytes(image))
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
put(0x43e764,0x42a1f8);put(0x43e744,0x42a9f8)
put(0x43f078,0x1100000+0x9ba36);put(0x43f074,0x1100000+0x959f6);put(0x43f07c,0x1100000+0xb3b36);put(0x43f06c,3);put(0x43f070,0x6040)
put(0x43f068,0x1001000);put(0x1001000,1);put(0x43f0d0,0x1002000);put(0x100205c,0x2101000);put(0x1002058,0x2101000)
put(0x4298c8,0x1000000);put(0x43e740,0x1003000);put(0x1003004,0x1003100);put(0x1003104,0x1003200)
# Original4388c0 owns the dispatch table, including identical layer3/4 callbacks.
callbacks=struct.unpack_from('<5I',image,0x4388c0-0x400000)
for i,callback in enumerate(callbacks):put(0x1003200+i*4,callback)
def ret(uc,a,n,ctx):
 sp=uc.reg_read(UC_X86_REG_ESP);target=struct.unpack('<I',uc.mem_read(sp,4))[0]
 uc.reg_write(UC_X86_REG_ESP,sp+4)
 from unicorn.x86_const import UC_X86_REG_EIP
 uc.reg_write(UC_X86_REG_EIP,target)
u.hook_add(UC_HOOK_CODE,ret,begin=0x2101000,end=0x2101000)
u.hook_add(UC_HOOK_CODE,ret,begin=0x409d78,end=0x409d78)
rng=random.Random(1996);cases=[];expected=[];launch_locks=[]
for operation in ['reset','kick','wall','lower_switch']:
 for i in range(300):
  b=bytearray(100)
  x=rng.choice([294,295,296,301,302,303,307]);y=rng.choice([570,579,580,581,582,583])
  if operation=='lower_switch':x=rng.randrange(320);y=rng.randrange(450,608)
  struct.pack_into('<ii',b,0,x*65536+rng.randrange(65536),y*65536+rng.randrange(65536))
  struct.pack_into('<ii',b,0x14,rng.randrange(-500000,500000),rng.randrange(-500000,500000))
  layer=1+i%4
  struct.pack_into('<H',b,0x48,layer);struct.pack_into('<H',b,0x3c,i%3);struct.pack_into('<H',b,0x1e,rng.randrange(4096))
  struct.pack_into('<I',b,0x40,0x1100000+[0x9ba36,0xbf9d6,0xd4ce6,0xe2936,0xd5466][layer])
  case=dict(operation=operation,bytes=list(b),pressed=bool(i%2),offset_x=0,offset_y=0);cases.append(case)
  initial_lock=[0,0x7fff,0xffff][i%3];u.mem_write(0x43f35c,struct.pack('<H',initial_lock))
  u.mem_write(0x1000000,bytes(b));put(0x1001030,1 if case['pressed'] else 0);put(0x200f000,0x2100000)
  u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0 if operation=='wall' else 0x1000000)
  start={'reset':0x41ab94,'kick':0x41ac30,'wall':0x409bec,'lower_switch':0x41c974}[operation]
  u.emu_start(start,0x2100000,count=20000)
  if operation=='kick':
   kicked=struct.unpack_from('<i',b,0)[0]>0x12e0000 and struct.unpack_from('<i',b,4)[0]>0x2440000 and case['pressed']
   observed=struct.unpack('<H',u.mem_read(0x43f35c,2))[0]
   assert observed==(0xffff if kicked else initial_lock)
   launch_locks.append(dict(case=i,initial=initial_lock,kicked=kicked,final=observed))
  if operation=='reset':u.mem_write(0x1000058,b'\0\0') # caller408943
  expected.append(list(u.mem_read(0x1000000,100)))
path=ROOT/'build/oracle/launch-cases.json';path.write_text(json.dumps(cases))
native=json.loads(subprocess.check_output([str(ROOT/'build/native/mean_probe'),str(path),str(base/'lookup.bin')],text=True))
differences=[i for i,(a,b) in enumerate(zip(expected,native)) if a!=b]
report=dict(launch_locks=launch_locks,lock_scope='Actual41ac6f write; successfulkick locksffff, failedkick preservesword; native scheduler integration tested separately by mean_skillshot_launch',cases=len(cases),differences=differences,wall_cases_by_layer={str(layer):sum(case['operation']=='wall' and struct.unpack_from('<H',bytes(case['bytes']),0x48)[0]==layer for case in cases) for layer in range(1,5)},original_material_callbacks=[hex(callback) for callback in callbacks],scope='Initializer+caller state0; gated launch kick; human-mode layer1/2/3/4 wall responses, separation omitted both sides; notification/score service stubbed; lower switch4 ball unchanged in initial mode')
(ROOT/'analysis/traces/mean-launch-component-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!="launch_locks"}))
if differences:
 i=differences[0];print('first mismatch',i,[(n,a,b) for n,(a,b) in enumerate(zip(expected[i],native[i])) if a!=b]);raise SystemExit(1)
