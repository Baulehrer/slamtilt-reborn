#!/usr/bin/env python3
import json,random,struct,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import *
ROOT=Path(__file__).resolve().parents[1]
def main():
 base=ROOT/'build/mean-prepared';image=bytearray((base/'pe-data.bin').read_bytes());image.extend(bytes(0x100000-len(image)))
 g=(base/'engine-globals.bin').read_bytes();f=(base/'flipper-state.bin').read_bytes();image[0x3e700:0x3e700+len(g)]=g;image[0x3e850:0x3e850+len(f)]=f
 u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_map(0x1000000,0x1000);u.mem_map(0x2000000,0x10000);u.mem_map(0x2100000,0x1000)
 rng=random.Random(1996);cases=[];expected=[];hits=0
 for i in range(1500):
  desc=0x43e850+(i%3)*26;px,py=struct.unpack_from('<hh',image,desc-0x400000)
  b=bytearray(100);struct.pack_into('<ii',b,0,(px+rng.randrange(-65,66))<<16,(py+rng.randrange(-20,21))<<16)
  struct.pack_into('<ii',b,0x14,rng.randrange(-6*65536,6*65536),rng.randrange(-6*65536,6*65536));struct.pack_into('<H',b,0x28,40)
  case=dict(bytes=list(b),descriptor=desc,response=bool(i%2));cases.append(case)
  u.mem_write(0x400000,bytes(image));u.mem_write(0x1000000,bytes(b));u.mem_write(0x200f000,struct.pack('<I',0x2100000))
  u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.reg_write(UC_X86_REG_EDX,desc)
  u.emu_start(0x409050,0x2100000,count=20000);result=u.reg_read(UC_X86_REG_EAX)
  if result==0:
   hits+=1
   if case['response']:
    u.reg_write(UC_X86_REG_EAX,0x1000000);u.reg_write(UC_X86_REG_EDX,desc);u.reg_write(UC_X86_REG_ESP,0x200f000);u.mem_write(0x200f000,struct.pack('<I',0x2100000));u.emu_start(0x4096e8,0x2100000,count=20000)
  expected.append(dict(result=result,bytes=list(u.mem_read(0x1000000,100)),field_43e75c=struct.unpack('<I',u.mem_read(0x43e75c,4))[0]))
 casespath=ROOT/'build/oracle/flipper-cases.json';casespath.write_text(json.dumps(cases))
 native=json.loads(subprocess.check_output([str(ROOT/'build/native/flipper_probe'),str(base),str(casespath)],text=True))
 diffs=[i for i,(a,b) in enumerate(zip(expected,native)) if a!=b]
 report=dict(cases=len(cases),contact_cases=hits,differences=diffs,method='Generated bounded C++ vs original demo x86, all ball bytes/result/scratch value checked; captured rest poses')
 (ROOT/'analysis/traces/mean-flipper-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
 if diffs:raise SystemExit(1)
if __name__=='__main__':main()
