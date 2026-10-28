#!/usr/bin/env python3
"""Original419f6c/41a54c vs native command writers; untouched bytes sentinel-tested."""
import argparse,json,random,struct,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FIELDS=['398','3ba','3bc','392','3a2','3b0','374','3ae','1da','394','38a','1f2','1e6','384','204','1fa','202','200','1fc','37a']
def original_cases():
 from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
 from unicorn.x86_const import UC_X86_REG_ESP
 u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_map(0x1000000,0x10000)
 image=(ROOT/'build/mean-prepared/pe-data.bin').read_bytes();u.mem_write(0x400000,image)
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 put(0x43f068,0x1001000);put(0x43f0d0,0x1002000);put(0x1002010,0x1003000)
 rng=random.Random(419);cases=[]
 for n in range(1024):
  c={k:rng.choice([-1,0,1,5]) for k in FIELDS}
  c.update({'3ba':rng.randrange(3),'3bc':rng.randrange(3),'1e6':rng.randrange(5),'204':rng.randrange(6),'1f2':rng.randrange(6),'1fc':rng.randrange(3),'3ae':rng.choice([0,49,50,149,150,1000]),'mode':rng.choice([0,2,4,5,6]),'service10':rng.choice([-1,0,1])})
  for k,z in [('1d4',4),('060',4),('1dc',4),('1e0',5),('1ec',5),('1e8',3)]:c[k]=[rng.randrange(2) for _ in range(z)]
  c['commands']=[[rng.randrange(256) for _ in range(4)] for _ in range(63)]
  for k in FIELDS:u.mem_write(0x43f000+int(k,16),struct.pack('<h',c[k]))
  for k in ['1d4','060','1dc','1e0','1ec','1e8']:u.mem_write(0x43f000+int(k,16),bytes(c[k]))
  # 1e0[4] overlaps low byte1e4, but WORD1e6 is the selection read.
  put(0x1001030,c['mode']);u.mem_write(0x1003010,struct.pack('<h',c['service10']))
  u.mem_write(0x43f208,bytes(x for row in c['commands'] for x in row));put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000)
  u.emu_start(0x419f6c,0x100fff0,count=10000)
  b=list(u.mem_read(0x43f208,252));cases.append({'input':c,'output':[b[i:i+4] for i in range(0,252,4)]})
 return {'image_sha256':hashlib.sha256(image).hexdigest(),'addresses':['0x419f6c','0x41a54c'],'cases':cases}
def main():
 p=argparse.ArgumentParser();p.add_argument('--oracle',action='store_true');p.add_argument('--probe',default=str(ROOT/'build/mean_lamp_mode_probe'));a=p.parse_args();path=ROOT/'analysis/traces/mean-lamp-mode-original.json'
 if a.oracle:path.write_text(json.dumps(original_cases(),separators=(',',':'))+'\n')
 data=json.loads(path.read_text());cases=data['cases'];out=json.loads(subprocess.check_output([a.probe],input=json.dumps([c['input'] for c in cases]).encode()))
 for i,(c,n) in enumerate(zip(cases,out)):
  if c['output']!=n:
   diff=[(j,c['output'][j],n[j]) for j in range(63) if c['output'][j]!=n[j]];raise AssertionError((i,diff,c['input']))
 assert len(cases)==len(out);print(f'{len(cases)} original lamp-mode cases matched')
if __name__=='__main__':main()
