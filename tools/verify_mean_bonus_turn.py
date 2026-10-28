#!/usr/bin/env python3
"""Original arithmetic and turn boundary; score service/DMD intentionally observed/stubbed."""
import argparse, hashlib, json, random, struct, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--replay',action='store_true');a=p.parse_args()
fixture=ROOT/'analysis/traces/mean-bonus-turn-original.json'
if a.replay:
 data=json.loads(fixture.read_text())
else:
 from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
 from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_EIP,UC_X86_REG_ESP
 image=(ROOT/'build/mean-prepared/pe-data.bin').read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_32)
 u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
 def put(address,value):u.mem_write(address,struct.pack('<I',value&0xffffffff))
 def get(address):return struct.unpack('<I',u.mem_read(address,4))[0]
 score=[]
 def hook(uc,address,size,ctx):
  if address==0x1000100:
   score.append(uc.reg_read(UC_X86_REG_EAX));sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
  elif address in (0x40737a,0x407808):uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);rng=random.Random(199607794);cases=[];expected=[]
 for i in range(1024):
  count=1+i%4;current=1+(i//4)%count
  c=dict(field_player_08=rng.choice([0,500000,10000000,0x7fffffff,0x80000000,0xffffffff,rng.randrange(2**32)]),field_player_0e=rng.choice([1,3,65535]),field_player_10=rng.choice([0,1,2,32767,32768,65535]),field_player_12=rng.choice([0,1,2,10,32767,32768,65535]),field_player_14=rng.choice([0,1,65535]),current_player=current,player_count=count,field_43d864=i%2)
  b=bytearray(24);struct.pack_into('<I',b,8,c['field_player_08']);struct.pack_into('<HHHH',b,14,*[c[k] for k in ['field_player_0e','field_player_10','field_player_12','field_player_14']]);u.mem_write(0x1000000,bytes(b))
  put(0x43d858,0x1000000);put(0x43d8a0,0x1000100);put(0x43d864,c['field_43d864']);put(0x43e774,current);put(0x43e778,count)
  score.clear();u.reg_write(UC_X86_REG_ESP,0x100f000);u.emu_start(0x40734b,0,count=100)
  u.reg_write(UC_X86_REG_ESP,0x100f000);u.emu_start(0x407794,0,count=100)
  out=bytes(u.mem_read(0x1000000,24));words=struct.unpack_from('<HHHH',out,14)
  expected.append(dict(score_argument=score[0] if score else 0,field_player_08=struct.unpack_from('<I',out,8)[0],field_player_0e=words[0],field_player_10=words[1],field_player_12=words[2],field_player_14=words[3],current_player=get(0x43e774),extra_ball=get(0x43e7d0)==0xffffffff));cases.append(c)
 data=dict(image_sha256=hashlib.sha256(image).hexdigest(),addresses=['0x40734b','0x40735b','0x407374','0x407794','0x407808'],scope='Arithmetic low32 score argument, bonus retention, signed extra-ball counter and player rotation. DMD and score accumulation external; game-over threshold not established.',cases=cases,expected=expected)
 fixture.write_text(json.dumps(data,separators=(',',':'))+'\n')
actual=json.loads(subprocess.check_output([str(a.native)],input=json.dumps(dict(cases=data['cases'])),text=True))
assert actual==data['expected'],next((i,x,y) for i,(x,y) in enumerate(zip(actual,data['expected'])) if x!=y)
print(json.dumps(dict(cases=len(actual),differences=0)))
