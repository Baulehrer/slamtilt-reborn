#!/usr/bin/env python3
"""Baseline switch3 proven no-op branches vs original demo41d94c."""
import json,random,struct,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import *
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'build/oracle/baseline_three_probe.cpp'
p.write_text('''#include "mean_baseline_three_bundle.h"
#include <nlohmann/json.hpp>
#include <iostream>
using nlohmann::json;
int main(){json a;std::cin>>a;json out=json::array();for(auto c:a){slam::MeanObject b;b.bytes=c["bytes"].get<decltype(b.bytes)>();bool ok=slam::mean_baseline_three_noop(b);out.push_back({{"bytes",b.bytes},{"accepted",ok}});}std::cout<<out;}
''')
exe=ROOT/'build/oracle/baseline_three_probe'
subprocess.run(['c++','-std=c++17','-I'+str(ROOT/'src/physics'),str(p),str(ROOT/'src/physics/mean_baseline_three_bundle.cpp'),str(ROOT/'src/physics/mean_step.cpp'),str(ROOT/'src/physics/mean_material_bundle.cpp'),'-o',str(exe)],check=True)
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000),(0x2100000,0x1000)]:u.mem_map(a,n)
u.mem_write(0x400000,(ROOT/'build/mean-prepared/pe-data.bin').read_bytes())
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
for a,v in [(0x43f078,0x309ba36),(0x43f074,0x30959f6),(0x43f07c,0x30b3b36),(0x43f06a,3<<16),(0x43f070,0x6040),(0x43f090,0x30cbb96)]:put(a,v)
rng=random.Random(0x41de71);cases=[];expected=[]
for i in range(480):
 b=bytearray(rng.randrange(256) for _ in range(100));struct.pack_into('<ii',b,0,rng.randrange(60*65536+1,320*65536),rng.randrange(608*65536));struct.pack_into('<H',b,0x5c,[0,1,11,19][i%4]);gate=i%3
 cases.append(dict(bytes=list(b),gate=gate));u.mem_write(0x1000000,bytes(b));u.mem_write(0x43f3b8,struct.pack('<H',gate));put(0x43f0d0,0x1002000);put(0x100201c,0);put(0x200f000,0x2100000)
 u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x41d94c,0x2100000,count=1000)
 expected.append(dict(bytes=list(u.mem_read(0x1000000,100)),accepted=True))
actual=json.loads(subprocess.check_output([str(exe)],input=json.dumps(cases),text=True));diff=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
report=dict(cases=len(cases),differences=diff,scope='Original41d94c x>60 and (x<260 or5c!=20); all100ballbytes; human mode; gate-independent no-op.')
(ROOT/'analysis/traces/mean-baseline-three-bundle-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert not diff
