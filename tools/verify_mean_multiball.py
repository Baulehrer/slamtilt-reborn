#!/usr/bin/env python3
"""Original bounded pool/spawn/pair routines and frozen held-release fixtures."""
import json,struct,random,subprocess
from pathlib import Path
exec((Path(__file__).parent/'trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
from unicorn.x86_const import UC_X86_REG_EDX
image=bytes(u.mem_read(0x400000,0x100000));runtime=bytes(u.mem_read(0x1000000,0x10000));rng=random.Random(19)
cases=[];expected=[]
def run(a):
 put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.emu_start(a,0x200fff0,count=10000)
def balls():return [list(u.mem_read(0x1007000+k*128,100)) for k in range(8)]
for op in ['allocate','remove','spawn']:
 for n in range(9):
  for variant in range(16):
   u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime)
   source=[bytearray(rng.randrange(256) for _ in range(100)) for k in range(8)]
   for k,b in enumerate(source):
    struct.pack_into('<HH',b,0x58, [2,3,5,6][(variant+k)%4], 5 if variant%3==0 else 1)
    u.mem_write(0x1007000+k*128,bytes(b));put(0x4298c8+k*4,0x1007000+k*128)
   put(0x43e770,n);put(0x1001000,n);put(0x1002014,0x4298c8)
   c=dict(op=op,count=n,balls=[list(b) for b in source])
   if op=='allocate':
    run(0x408050);a=u.reg_read(UC_X86_REG_EAX);e=dict(count=get(0x43e770),index=(a-0x1007000)//128 if a else -1,balls=balls())
   elif op=='remove':
    put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.emu_start(0x4079dc,0x407a3d,count=10000);e=dict(count=get(0x43e770),balls=balls())
   else:
    remaining=[1,2,3,32767,-32768][variant%5];primary=-1 if variant%2 else 0
    c.update(remaining=remaining,primary=primary)
    put(0x1002020,0x408050);put(0x438b8c,primary);put(0x438b90,33);put(0x438b94,44)
    u.mem_write(0x43f36e,struct.pack('<h',remaining));u.mem_write(0x43f37e,struct.pack('<h',2))
    run(0x4151e4)
    e=dict(count=get(0x43e770),remaining=word(0x43f36e),stage=word(0x43f37e),slot=[get(0x438b8c+k*4) for k in range(3)],slot50=[get(0x438b50+k*4) for k in range(3)],balls=balls())
   cases.append(c);expected.append(e)
lut=(ROOT/'build/mean-prepared/lookup.bin').read_bytes()
for k in range(1024):
 u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime)
 put(0x43e728,0x42c9fc);put(0x43e764,0x1006000);u.mem_write(0x1006000,lut)
 pair=[]
 for j in range(2):
  b=bytearray(100);x=100+(rng.randrange(-20,21) if j else 0);y=300+(rng.randrange(-20,21) if j else 0)
  struct.pack_into('<ii',b,0,x*65536,y*65536);struct.pack_into('<ii',b,0x14,rng.randrange(-400000,400000),rng.randrange(-400000,400000))
  struct.pack_into('<HH',b,0x58,[2,3,6,7][(k+j)%4],5);struct.pack_into('<H',b,0x5c,18);struct.pack_into('<I',b,0x60,0x40000 if k%5 else 0)
  struct.pack_into('<ii',b,0x2c,rng.randrange(1000000),rng.randrange(300000));struct.pack_into('<H',b,0x34,k%2)
  u.mem_write(0x1000000+j*128,bytes(b));put(0x4298c8+j*4,0x1000000+j*128);pair.append(list(b))
 u.reg_write(UC_X86_REG_EAX,0);u.reg_write(UC_X86_REG_EDX,1);run(0x408bfc)
 cases.append(dict(op='pair',balls=pair));expected.append([list(u.mem_read(0x1000000+j*128,100)) for j in range(2)])
for x in [0,13,159,160,161,200,320]:
 for y in [0,306,378,379,380,532,533,534,608]:
  for field in [0,17,18,19]:
   b=bytearray(rng.randrange(256) for _ in range(100));struct.pack_into('<ii',b,0,x*65536,y*65536);struct.pack_into('<H',b,0x5c,field)
   u.mem_write(0x1000000,bytes(b));u.reg_write(UC_X86_REG_EAX,0x1000000);run(0x417238)
   cases.append(dict(op='guide',ball=list(b)));expected.append(list(u.mem_read(0x1000000,100)))
f=json.loads((ROOT/'analysis/traces/mean-multiball-release-original.json').read_text())
for c in f['cases']:cases.append(dict(op='release',**c['initial']));expected.append(c['steps'])
actual=json.loads(subprocess.check_output(['build/native/mean_multiball_probe',str(ROOT/'build/mean-prepared/pe-data.bin'),str(ROOT/'build/mean-prepared/lookup.bin')],input=json.dumps(cases),text=True))
diff=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
if diff:
 i=diff[0];print('Difference',i,cases[i]['op'],str(actual[i])[:500],str(expected[i])[:500])
assert not diff and len(actual)==len(expected)
(ROOT/'analysis/traces/mean-multiball-fixture.json').write_text(json.dumps(dict(build_sha256='31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00',scope='Original408050 allocator,4151e4 spawn,4079dc removal,408bfc pair/math,415330 callback5; excludes full original autonomous gameplay',cases=cases,expected=expected),separators=(',',':'))+'\n')
print(json.dumps(dict(cases=len(cases),pairs=1024,pool_spawn_remove=432,release_cases=49,guide_cases=252,differences=0)))
