#!/usr/bin/env python3
import json,struct,subprocess,sys
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP
ROOT=Path(__file__).resolve().parents[1]
exe=ROOT/'build/oracle/mean_upper_reward_cycle_probe'
subprocess.run(['c++','-std=c++17','-Isrc','-Ibuild/native/_deps/json-src/include','tests/mean_upper_reward_cycle_probe.cpp',*[f'src/physics/{x}.cpp' for x in ['mean_upper_capture','mean_upper_release','mean_capture_tick','mean_step','mean_material_bundle','mean_reward_display']],'-o',str(exe)],cwd=ROOT,check=True)
allcases=[]
for reward in [1,2]:
 env={'__file__':str(ROOT/'tools/trace_mean_upper_capture.py')};exec((ROOT/'tools/trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0],env)
 u=env['u'];put=env['put'];get=env['get'];word=env['word'];scores=env['scores']
 put(0x43f068,0x43e770);put(0x43e7a0,2);put(0x43e7b0,0);put(0x43e780,0)
 put(0x43e81c,0);put(0x43e7b4,0)
 put(0x43e740,0x1005000);put(0x1005004,0x1006000);put(0x1006008,0x1007000);put(0x1007034,0x413b04)
 put(0x1002034,0x200ff20);put(0x100203c,0x200ff00)
 def service(uc,a,n,ctx):
  sp=uc.reg_read(UC_X86_REG_ESP);callback=struct.unpack('<I',uc.mem_read(sp+12,4))[0]
  if callback in [0x410a34,0x410910]:uc.reg_write(UC_X86_REG_EIP,0x405f98)
  else:
   target=struct.unpack('<I',uc.mem_read(sp,4))[0];uc.reg_write(UC_X86_REG_ESP,sp+16);uc.reg_write(UC_X86_REG_EAX,1);uc.reg_write(UC_X86_REG_EIP,target)
 u.hook_add(UC_HOOK_CODE,service,begin=0x200ff20,end=0x200ff20)
 u.hook_add(UC_HOOK_CODE,env['stub'],begin=0x40f91c,end=0x40f91c)
 def idle(uc,a,n,ctx):
  if word(0x43f364)==0:env['stub'](uc,a,n,ctx)
 u.hook_add(UC_HOOK_CODE,idle,begin=0x413b04,end=0x413b04)
 b=bytearray(100);struct.pack_into('<ii',b,0,14*65536,14*65536);struct.pack_into('<HH',b,0x58,3,1);u.mem_write(0x1000000,bytes(b))
 u.mem_write(0x43f200 if reward==1 else 0x43f202,struct.pack('<h',-1))
 rows=[]
 for tick in range(1200):
  before=len(scores);put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000)
  u.emu_start(0x415330,0x200fff0,count=10000)
  if tick%4==3:
   for address in [0x438b5c,0x438b68,0x438b74]:
    if get(address)>=0:put(address,get(address)-1)
   put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.emu_start(0x4071e8,0x200fff0,count=5000)
  rows.append(dict(ball=list(u.mem_read(0x1000000,100)),slot2=[get(0x438b68+i*4) for i in range(3)],slot3=[get(0x438b74+i*4) for i in range(3)],slot50=[get(0x438b50+i*4) for i in range(3)],timer=word(0x43f36a),mode=get(0x43e7a0),field1f2=word(0x43f1f2),field394=word(0x43f394),slot1=[get(0x438b5c+i*4) for i in range(3)],gate=word(0x43f364),field204=word(0x43f204),score=sum(scores[before:]),field200=word(0x43f200),field202=word(0x43f202),field378=word(0x43f378),field1fc=word(0x43f1fc)))
  if word(0x1000058)==2:break
 actual=json.loads(subprocess.check_output([str(exe),*(['reward2'] if reward==2 else [])],text=True))
 differences=[i+1 for i,(a,b) in enumerate(zip(actual,rows)) if a!=b]
 allcases.append(dict(reward=reward,states=rows,differences=differences,native_steps=len(actual)))
 print(json.dumps(dict(reward=reward,steps=len(rows),native_steps=len(actual),differences=differences[:5])))
 if differences:print(actual[differences[0]-1],rows[differences[0]-1])
 assert len(actual)==len(rows) and not differences
(ROOT/'analysis/traces/mean-upper-reward-cycle-original.json').write_text(json.dumps(dict(scope='Original415330 all100bytes + actual405f98 reward starts + actual410a34/410910 via4071e8 at50Hz + actual413b60 gate completion +416be4 release. Graphics stubbed; nonreward DMD announcements handle1; idle presentation only skipped when gate0. No freephysics/engine wrapper.',cases=allcases),separators=(',',':'))+'\n')
