#!/usr/bin/env python3
"""Original left capture slot tick and callback, including other-ball gates."""
import json,random,struct,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'build/oracle/capture_probe.cpp'
p.write_text('''#include "mean_capture_bundle.h"
#include <nlohmann/json.hpp>
#include <iostream>
using nlohmann::json;
int main(){json a;std::cin>>a;json out=json::array();for(auto c:a){slam::MeanObject b;b.bytes=c["bytes"].get<decltype(b.bytes)>();slam::MeanLeftCaptureState s;s.field_438b68=c["slot"];s.field_438b6c=c["slot4"];s.field_43f380=c["timer"];if(c["tick"].get<bool>())slam::mean_left_capture_slot_tick(s);bool captured;bool ok=slam::mean_left_capture(b,s,c["mode"],c["blocked"],captured);out.push_back({{"bytes",b.bytes},{"slot",s.field_438b68},{"slot4",s.field_438b6c},{"timer",s.field_43f380},{"captured",captured},{"accepted",ok}});}std::cout<<out;}
''')
exe=ROOT/'build/oracle/capture_probe'
subprocess.run(['c++','-std=c++17','-I'+str(ROOT/'src/physics'),str(p),str(ROOT/'src/physics/mean_capture_bundle.cpp'),str(ROOT/'src/physics/mean_step.cpp'),str(ROOT/'src/physics/mean_material_bundle.cpp'),'-o',str(exe)],check=True)
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000),(0x2100000,0x1000)]:u.mem_map(a,n)
image=(ROOT/'build/mean-prepared/pe-data.bin').read_bytes();u.mem_write(0x400000,image)
assert struct.unpack_from('<i',image,0x38b68)[0]==0
assert list(struct.unpack_from('<5I',image,0x38b98))==[0x438b5c,0x438b68,0x438b74,0x438b80,0x438b8c]
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<i',u.mem_read(a,4))[0]
put(0x43f0d0,0x1002000);put(0x43f068,0x1003000);put(0x1002014,0x1004000);put(0x100205c,0x2100100);put(0x1004000,0x1000000);put(0x1004004,0x1000100)
notifications=[]
def skip(uc,a,n,c):
 notifications.append(a);sp=uc.reg_read(UC_X86_REG_ESP);ret=struct.unpack('<I',uc.mem_read(sp,4))[0];uc.reg_write(UC_X86_REG_ESP,sp+4);uc.reg_write(UC_X86_REG_EIP,ret)
u.hook_add(UC_HOOK_CODE,skip,begin=0x2100100,end=0x2100100)
rng=random.Random(0x41d9e3);cases=[];expected=[]
for i in range(512):
 b=bytearray(rng.randrange(256) for _ in range(100));struct.pack_into('<ii',b,0,rng.randrange(60*65536+1),rng.randrange(170*65536,608*65536));struct.pack_into('<HH',b,0x58,2,0)
 slot=rng.choice([-100,-1,0,1,100]);tick=bool(i%2);blocked=bool(i%3==0);mode=i%5==0;slot4=rng.randrange(-100,101);timer=rng.randrange(65536)
 c=dict(bytes=list(b),slot=slot,tick=tick,blocked=blocked,mode=int(mode),slot4=slot4,timer=timer);cases.append(c)
 u.mem_write(0x1000000,bytes(b));other=bytearray(100);struct.pack_into('<HH',other,0x58,3 if blocked else 2,2);u.mem_write(0x1000100,bytes(other));put(0x1003000,2);put(0x100201c,int(mode));put(0x438b68,slot);put(0x438b6c,slot4);u.mem_write(0x43f380,struct.pack('<H',timer));notifications.clear()
 if tick:
  u.reg_write(UC_X86_REG_EAX,0);u.emu_start(0x4198b3,0x4198ce,count=100)
 put(0x200f000,0x2100000);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x41d94c,0x2100000,count=1000)
 expected.append(dict(bytes=list(u.mem_read(0x1000000,100)),slot=get(0x438b68),slot4=get(0x438b6c),timer=struct.unpack('<H',u.mem_read(0x43f380,2))[0],captured=bool(notifications),accepted=True))
actual=json.loads(subprocess.check_output([str(exe)],input=json.dumps(cases),text=True));diff=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
report=dict(cases=len(cases),differences=diff,captures=sum(x['captured'] for x in expected),scope='Original4198b3 slot countdown +41d94c left branch+41db1c gate, all100ballbytes,438b68/438b6c/43f380; service5c notification skipped')
(ROOT/'analysis/traces/mean-capture-bundle-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert not diff
