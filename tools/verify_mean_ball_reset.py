#!/usr/bin/env python3
"""Actual419b00/419da4;416fe0 lamp rebuild andservice90 observed boundaries."""
import argparse,json,random,struct,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def original():
 from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
 from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_ESP
 u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_map(0x1000000,0x10000)
 image=(ROOT/'build/mean-prepared/pe-data.bin').read_bytes();u.mem_write(0x400000,image)
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 calls=[]
 def stub(uc,a,n,x):
  calls.append(hex(a));sp=uc.reg_read(UC_X86_REG_ESP);target=struct.unpack('<I',uc.mem_read(sp,4))[0];uc.reg_write(UC_X86_REG_ESP,sp+4);uc.reg_write(UC_X86_REG_EIP,target)
 for a in [0x416fe0,0x100fff4]:u.hook_add(UC_HOOK_CODE,stub,begin=a,end=a)
 u.mem_write(0x100fff4,b"\xc3")
 rng=random.Random(41900);cases=[]
 for n in range(512):
  u.mem_write(0x400000,image)
  fields=bytearray(rng.randbytes(0x3c0));record=bytearray(rng.randbytes(52));record[12:17]=bytes(rng.randrange(2) for _ in range(5));struct.pack_into('<h',record,18,rng.randrange(5));struct.pack_into('<h',record,30,rng.randrange(7))
  c=dict(fields=list(fields),record=list(record),ee1c=list(rng.randbytes(8)),a40=rng.randrange(-32768,32768),af4=rng.choice([0,1,-1]),af8=rng.randrange(0x7fffffff),b44=71,b4c=72,mode=rng.choice([2,4,5,6]),engine3c=rng.randrange(0x100000000),player=rng.randrange(8))
  u.mem_write(0x43f000,bytes(fields));u.mem_write(0x43ee24+c['player']*52,bytes(record));u.mem_write(0x43ee1c,bytes(c['ee1c']))
  put(0x43f068,0x1001000);put(0x43f0d0,0x1002000);put(0x1002090,0x100fff4);put(0x1001030,c['mode']);put(0x100103c,c['engine3c'])
  # Pointer bytes are valid runtime values, preserved by reset.
  c['fields']=list(u.mem_read(0x43f000,0x3c0))
  for k,a,size in [('a40',0x438a40,2),('af4',0x438af4,2),('af8',0x438af8,4),('b44',0x438b44,4),('b4c',0x438b4c,4)]:u.mem_write(a,struct.pack('<h' if size==2 else '<i',c[k]))
  put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.reg_write(UC_X86_REG_EAX,c['player']);calls.clear();
  try:u.emu_start(0x419b00,0x100fff0,count=20000)
  except Exception:
   print(n,hex(u.reg_read(UC_X86_REG_EIP)),calls);raise
  out=dict(fields=list(u.mem_read(0x43f000,0x3c0)),ee1c=list(u.mem_read(0x43ee1c,8)),calls=calls.copy())
  for k,a,size in [('a40',0x438a40,2),('af4',0x438af4,2),('af8',0x438af8,4),('b44',0x438b44,4),('b4c',0x438b4c,4)]:out[k]=struct.unpack('<h' if size==2 else '<i',u.mem_read(a,size))[0]

  # Paired save419ad8 must write exactly this player's52bytes.
  put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.reg_write(UC_X86_REG_EAX,c['player']);u.emu_start(0x419ad8,0x100fff0,count=100)
  out['saved_record']=list(u.mem_read(0x43ee24+c['player']*52,52))
  cases.append(dict(input=c,output=out))
 return dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Actual419b00 and419da4;416fe0 presentation rebuild observed/stubbed, service90 observed/stubbed',cases=cases)
def main():
 p=argparse.ArgumentParser();p.add_argument('--oracle',action='store_true');p.add_argument('--probe',default=str(ROOT/'build/mean_ball_reset_probe'));a=p.parse_args();path=ROOT/'analysis/traces/mean-ball-reset-original.json'
 if a.oracle:path.write_text(json.dumps(original(),separators=(',',':'))+'\n')
 cases=json.loads(path.read_text())['cases'];out=json.loads(subprocess.check_output([a.probe],input=json.dumps([c['input'] for c in cases]).encode()))
 for i,(c,n) in enumerate(zip(cases,out)):
  if c['output']!=n:
   diff={k:([j for j,(x,y) in enumerate(zip(c['output'][k],n[k])) if x!=y] if k=='fields' else [c['output'][k],n[k]]) for k in n if c['output'][k]!=n[k]};raise AssertionError((i,diff))
 assert len(out)==len(cases);print(f'{len(cases)} original full ball resets matched')
if __name__=='__main__':main()
