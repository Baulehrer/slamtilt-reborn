#!/usr/bin/env python3
"""Bounded original random406840 + release416be4, all100 ball bytes."""
import json,random,struct,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP,UC_X86_REG_EIP
ROOT=Path(__file__).resolve().parents[1]
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000)]:u.mem_map(a,n)
u.mem_write(0x400000,(ROOT/'build/mean-prepared/pe-data.bin').read_bytes())
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
def ret(uc,a,n,c):
 if a==0x422f36:uc.reg_write(UC_X86_REG_EAX,0x1005000)
 sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,ret,begin=0x422f36,end=0x422f36)
u.hook_add(UC_HOOK_CODE,ret,begin=0x200ff00,end=0x200ff00)
put(0x43f068,0x43e770);put(0x43f0d0,0x1002000);put(0x100205c,0x200ff00)
for i,v in enumerate([3,0x6040,0x1100000+0x959f6,0x1100000+0x9ba36,0x1100000+0xb3b36]):put(0x43f06c+i*4,v)
def run(pc):
 put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(pc,0x200fff0,count=1000)
rng=random.Random(0x416be4);cases=[];expected=[]
for i,v in enumerate([1,0x60e0,0x1100000+0xb98f6,0x1100000+0xbf9d6,0x1100000+0xcbb96]):put(0x43f080+i*4,v)
for i in range(1024):
 c=dict(ball=list(rng.randbytes(100)),seed=rng.getrandbits(32),accumulator=rng.getrandbits(32),field_43e834=rng.getrandbits(32),transfer=i>=512);cases.append(c)
 u.mem_write(0x1000000,bytes(c['ball']));put(0x1005000,c['seed']);put(0x43e7a8,c['accumulator']);put(0x43e834,c['field_43e834']);put(0x438b74,-1);put(0x43e770,0);run(0x406840);run(0x417068 if c["transfer"] else 0x416be4)
 expected.append(dict(ball=list(u.mem_read(0x1000000,100)),seed=get(0x1005000),accumulator=get(0x43e7a8),field_43e7ac=get(0x43e7ac)))
probe=ROOT/'build/oracle/mean_upper_release_probe'
subprocess.run(['c++','-std=c++17','-Isrc','-Ibuild/native/_deps/json-src/include','tests/mean_upper_release_probe.cpp','src/physics/mean_upper_release.cpp','src/physics/mean_step.cpp','src/physics/mean_material_bundle.cpp','-o',str(probe)],cwd=ROOT,check=True)
actual=json.loads(subprocess.check_output([str(probe)],input=json.dumps(cases),text=True));diff=[i for i,(a,b) in enumerate(zip(expected,actual)) if a!=b]
report=dict(cases=len(cases),differences=diff,scope='Original406840 actualCRT422f40 (TLS pointer stub only), then416be4 or417068 (actualgate, zerootherballs); sound service stubbed; all100ballbytes and full32bit randomstate compared')
(ROOT/'analysis/traces/mean-upper-release-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert not diff
