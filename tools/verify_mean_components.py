#!/usr/bin/env python3
"""Compare native bounded components against execution of actual original x86."""
import hashlib,json,random,struct,subprocess
from pathlib import Path
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
ROOT=Path(__file__).resolve().parents[1]
def main():
 exe=ROOT/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/SLAMTILT.EXE'
 raw=exe.read_bytes();image=pefile.PE(data=raw).get_memory_mapped_image();u=Uc(UC_ARCH_X86,UC_MODE_32)
 u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000);u.mem_map(0x2000000,0x10000);u.mem_map(0x2100000,0x1000)
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 put(0x4298c8,0x1000000);put(0x43e764,0x42a1f8);put(0x43e744,0x42a9f8);put(0x43d860,0);put(0x43d864,0);put(0x4298a4,0)
 put(0x43e740,0x1001000);put(0x1001004,0x1001100);put(0x1001104,0x1001200);put(0x1001200,0x41e00c)
 def skip_separation(uc,a,n,ctx):
  sp=uc.reg_read(UC_X86_REG_ESP);ret=struct.unpack('<I',uc.mem_read(sp,4))[0];uc.reg_write(UC_X86_REG_ESP,sp+4);uc.reg_write(UC_X86_REG_EIP,ret)
 u.hook_add(UC_HOOK_CODE,skip_separation,begin=0x409d78,end=0x409d78)
 rng=random.Random(1996);cases=[];expected=[]
 for operation in ['integrate','free','wall']:
  for i in range(300):
   b=bytearray(0x64)
   for offset in [0,4,8,12,0x14,0x18]:struct.pack_into('<i',b,offset,rng.randint(-10*65536,620*65536) if offset<16 else rng.randint(-8*65536,8*65536))
   struct.pack_into('<H',b,0x28,rng.randrange(256));struct.pack_into('<H',b,0x2a,rng.randrange(4096));struct.pack_into('<H',b,0x1e,rng.randrange(4096));struct.pack_into('<H',b,0x3c,i%3)
   ox,oy=rng.randint(-65536,65536),rng.randint(-65536,65536)
   case=dict(operation=operation,bytes=list(b),offset_x=ox,offset_y=oy);cases.append(case)
   u.mem_write(0x1000000,bytes(b));put(0x43e724,ox);put(0x43e564,oy);put(0x200f000,0x2100000)
   u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0 if operation in ['integrate','wall'] else 0x1000000)
   start={'integrate':0x40a010,'free':0x409e18,'wall':0x409bec}[operation]
   u.emu_start(start,0x2100000,count=10000)
   if u.reg_read(UC_X86_REG_ESP)!=0x200f004:raise RuntimeError('Original component did not return')
   expected.append(list(u.mem_read(0x1000000,0x64)))
 fixture=ROOT/'build/oracle/component-cases.json';fixture.write_text(json.dumps(cases))
 native=json.loads(subprocess.check_output([str(ROOT/'build/native/mean_probe'),str(fixture),str(ROOT/'build/mean-prepared/lookup.bin')],text=True))
 differences=[]
 for i,(a,b) in enumerate(zip(expected,native)):
  if a!=b:differences.append(dict(case=i,operation=cases[i]['operation'],offsets=[j for j in range(0x64) if a[j]!=b[j]]))
 out=dict(build_sha256=hashlib.sha256(raw).hexdigest(),method='Native C++ vs original demo x86 through Unicorn',cases=len(cases),differences=differences,scope='Integration without point forces/debug override; free velocity field22==0; material0/1/2 response, original separation skipped in both sides')
 (ROOT/'analysis/traces/mean-component-validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));
 if differences:raise SystemExit(1)
if __name__=='__main__':main()
