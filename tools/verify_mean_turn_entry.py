#!/usr/bin/env python3
import argparse,hashlib,json,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--replay',action='store_true');a=p.parse_args();fixture=ROOT/'analysis/traces/mean-turn-entry-original.json'
if a.replay:data=json.loads(fixture.read_text())
else:
 from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
 from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESP,UC_X86_REG_EIP
 image=(ROOT/'build/mean-prepared/pe-data.bin').read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def word(a):return struct.unpack('<h',u.mem_read(a,2))[0]
 calls=[]
 def hook(uc,a,n,c):
  if a in [0x41b260,0x4199fe,0x100fff0]:uc.emu_stop()
  elif a in [0x1000600,0x40f754]:
   calls.append(hex(a));sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if a==0x1000600 and services==0 and timer>=0 else 0 if a==0x1000600 else 8))
 u.hook_add(UC_HOOK_CODE,hook)
 put(0x43f068,0x1001000);put(0x43f0d0,0x1002000);put(0x1002034,0x1000600);put(0x1002024,0x1000600)
 cases=[];expected=[]
 for op in ['entry','drain','clock']:
  for mode in [0,1,2,3,5,6]:
   for timer in [-32768,-1,0,1,50,51,150,151,400,32767]:
    for count in ([1,2,8] if op=='drain' else [1]):
     for services in ([0,1] if op=='drain' else [0]):
      c=dict(operation=op,mode=mode,field_43f3ae=timer,field_43f35a=-17,command258=[9,8,7,6],command260=[5,4,3,2],ball=[i for i in range(100)],count=count,services=services)
      u.mem_write(0x1000000,bytes(c['ball']));put(0x1001030,mode);put(0x1001000,count);put(0x100201c,services);u.mem_write(0x43f3ae,struct.pack('<h',timer));u.mem_write(0x43f35a,struct.pack('<h',-17));u.mem_write(0x43f258,bytes(c['command258']));u.mem_write(0x43f260,bytes(c['command260']));put(0x438af4,0)
      calls.clear();put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.reg_write(UC_X86_REG_EDX,0x1001000)

      try:u.emu_start({'entry':0x41b201,'drain':0x41aaac,'clock':0x4199a6}[op],0x100fff0,count=300)
      except Exception:
       print(op,mode,timer,count,services,hex(u.reg_read(UC_X86_REG_EIP)),calls);raise
      event=(mode==1) if op=='entry' else (word(0x1000058)==-1) if op=='drain' else word(0x438af4)==-1
      expected.append(dict(mode=get(0x1001030),field_43f3ae=word(0x43f3ae),field_43f35a=word(0x43f35a),command258=list(u.mem_read(0x43f258,4)),command260=list(u.mem_read(0x43f260,4)),ball=list(u.mem_read(0x1000000,100)),event=event));cases.append(c)
 data=dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Original41b201 entry effects,41aaac drain intercept,4199a6 timer; service34/24 and40f754 observed/stubbed. BallFFFF initialization nextengine tick externally.',cases=cases,expected=expected);fixture.write_text(json.dumps(data,separators=(',',':'))+'\n')
actual=json.loads(subprocess.check_output([str(a.native)],input=json.dumps(dict(cases=data['cases'])),text=True));assert actual==data['expected'],next((i,x,y) for i,(x,y) in enumerate(zip(actual,data['expected'])) if x!=y);print(json.dumps(dict(cases=len(actual),differences=0)))
