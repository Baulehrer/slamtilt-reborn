#!/usr/bin/env python3
"""Bounded actual4199a6 tail, gated at41989f; original50Hz display callback."""
import argparse,json,random,struct,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def original():
 from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
 from unicorn.x86_const import UC_X86_REG_ESP
 u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_map(0x1000000,0x10000)
 image=(ROOT/'build/mean-prepared/pe-data.bin').read_bytes();u.mem_write(0x400000,image)
 rng=random.Random(4199);cases=[]
 for n in range(1024):
  c={k:rng.choice([-32768,-2,-1,0,1,2,49,50,51,149,150,151,400,32767]) for k in ['3ae','390','35a','3b0']};c['af4']=rng.choice([-1,0,1]);c['service1c']=rng.choice([0,0,0,1,-1]);c['ee1c']=[rng.choice([-1,0,1,2,32767]) for _ in range(4)]
  for k in ['260','268','258']:c[k]=list(rng.randbytes(4))
  for k in ['3ae','390','35a','3b0']:u.mem_write(0x43f000+int(k,16),struct.pack('<h',c[k]))
  u.mem_write(0x438af4,struct.pack('<h',c['af4']));u.mem_write(0x43ee1c,struct.pack('<4h',*c['ee1c']))
  for k in ['260','268','258']:u.mem_write(0x43f000+int(k,16),bytes(c[k]))
  u.mem_write(0x100f000,struct.pack('<I',0x100fff0));u.reg_write(UC_X86_REG_ESP,0x100efec)
  # Gate proven41989f; puretail has no branch-dependent service calls.
  if c['service1c']==0:u.emu_start(0x4199a6,0x100fff0,count=200)
  out={k:struct.unpack('<h',u.mem_read(0x43f000+int(k,16),2))[0] for k in ['3ae','390','35a','3b0']};out['af4']=struct.unpack('<h',u.mem_read(0x438af4,2))[0];out['ee1c']=list(struct.unpack('<4h',u.mem_read(0x43ee1c,8)))
  for k in ['260','268','258']:out[k]=list(u.mem_read(0x43f000+int(k,16),4))
  cases.append(dict(input=c,output=out))
 return dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Actual4199a6..419a97, entrygate41989f service1c;50Hzcallback419890 original404a88..404b15',cases=cases)
def main():
 p=argparse.ArgumentParser();p.add_argument('--oracle',action='store_true');p.add_argument('--probe',default=str(ROOT/'build/mean_turn_clock_probe'));a=p.parse_args();path=ROOT/'analysis/traces/mean-turn-clock-original.json'
 if a.oracle:path.write_text(json.dumps(original(),separators=(',',':'))+'\n')
 cases=json.loads(path.read_text())['cases'];out=json.loads(subprocess.check_output([a.probe],input=json.dumps([c['input'] for c in cases]).encode()))
 assert len(cases)==len(out)
 for i,(c,n) in enumerate(zip(cases,out)):assert c['output']==n,(i,c,n)
 print(f'{len(cases)} original turn-clock cases matched')
if __name__=='__main__':main()
