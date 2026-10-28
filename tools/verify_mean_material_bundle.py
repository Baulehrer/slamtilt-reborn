#!/usr/bin/env python3
"""Bounded material6/7 callback mutations against original demo x86."""
import json, random, struct, subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import *
ROOT=Path(__file__).resolve().parents[1]
probe=ROOT/'build/oracle/material_bundle_probe.cpp'
probe.write_text('''#include "mean_material_bundle.h"
#include <nlohmann/json.hpp>
#include <iostream>
using nlohmann::json;
int main(){json cases; std::cin>>cases;json out=json::array();for(auto c:cases){slam::MeanObject b;b.bytes=c["bytes"].get<decltype(b.bytes)>();slam::MeanMaterialBundleState s;s.field_services_1c=c["mode"];s.field_43f1da=c["gate"];s.field_43f390=c["timer"];int n=c["normal"],t=c["tangent"];bool request;slam::mean_material_bundle(b,c["material"],n,t,s,request);out.push_back({{"bytes",b.bytes},{"normal",n},{"tangent",t},{"gate",s.field_43f1da},{"timer",s.field_43f390},{"state",s.field_43f268},{"request",request}});}std::cout<<out;}
''')
exe=ROOT/'build/oracle/material_bundle_probe'
subprocess.run(['c++','-std=c++17','-I'+str(ROOT/'src/physics'),str(probe),str(ROOT/'src/physics/mean_material_bundle.cpp'),str(ROOT/'src/physics/mean_step.cpp'),'-o',str(exe)],check=True)
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000),(0x2100000,0x1000)]:u.mem_map(a,n)
u.mem_write(0x400000,(ROOT/'build/mean-prepared/pe-data.bin').read_bytes())
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<i',u.mem_read(a,4))[0]
put(0x43f0d0,0x1002000)
rng=random.Random(602625);cases=[];expected=[]
for i in range(512):
 b=bytes(rng.randrange(256) for _ in range(100));mode=i%3;gate=rng.randrange(2);timer=rng.choice([-32768,-1,0,250,32767]);normal=rng.randrange(-2**31,2**31);tangent=rng.randrange(-2**31,2**31)
 c=dict(bytes=list(b),mode=mode,gate=gate,timer=timer,normal=normal,tangent=tangent,material=6+i%2);cases.append(c)
 u.mem_write(0x1000000,b);put(0x100201c,mode);u.mem_write(0x43f1da,struct.pack('<H',gate));u.mem_write(0x43f390,struct.pack('<h',timer));u.mem_write(0x43f268,bytes(4));put(0x1000100,normal);put(0x1000104,tangent)
 put(0x200f000,0x2100000)
 for reg,val in [(UC_X86_REG_ESP,0x200f000),(UC_X86_REG_EAX,0x1000000),(UC_X86_REG_EDX,c['material']),(UC_X86_REG_ECX,0x1000100),(UC_X86_REG_EBX,0x1000104)]:u.reg_write(reg,val)
 # Stop before external notification/music requests after all local mutations.
 u.emu_start(0x41e00c,0x41e6e6 if mode==0 and c['material']==7 and (gate or timer>=0) else 0x2100000,count=1000)
 expected.append(dict(bytes=list(u.mem_read(0x1000000,100)),normal=get(0x1000100),tangent=get(0x1000104),gate=struct.unpack('<H',u.mem_read(0x43f1da,2))[0],timer=struct.unpack('<h',u.mem_read(0x43f390,2))[0],state=list(u.mem_read(0x43f268,4)),request=u.reg_read(UC_X86_REG_EIP)==0x41e6e6))
actual=json.loads(subprocess.check_output([str(exe)],input=json.dumps(cases),text=True))
diff=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
report=dict(cases=len(cases),differences=diff,scope='41e00c material6/7 callback-local ball100bytes, normal/tangent, gates43f1da/43f390 and state43f268. Stops before external service call41e6e6.',service_requests=sum(x['request'] for x in expected))
(ROOT/'analysis/traces/mean-material-bundle-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report));assert not diff
