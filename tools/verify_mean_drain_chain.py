#!/usr/bin/env python3
"""Composed original table drain, engine bonus, save/reset and initializer.
Rendering/audio adapters excluded; controlled single-player service context.
"""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESP,UC_X86_REG_EIP
R=Path(__file__).resolve().parents[1];image=(R/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
def word(a,v):u.mem_write(a,struct.pack('<H',v&65535))
def w(a):return struct.unpack('<H',u.mem_read(a,2))[0]
score=0;finished=False;finish_call=False
adapters={0x4060a4:0,0x4060f8:0,0x406280:4,0x40617c:8,0x406680:0,0x416fe0:0,0x419f6c:0,0x1003000:0,0x1003010:0,0x1003020:12,0x40f754:8}
def hook(uc,a,n,c):
 global score,finished
 if a in [0x100fff0,0x4078a6] or (a==0x407794 and not finish_call):
  if a==0x407794:finished=True
  uc.emu_stop();return
 if a in adapters:
  if a==0x1003020:uc.reg_write(UC_X86_REG_EAX,0)
  if a==0x1003010:score=(score+uc.reg_read(UC_X86_REG_EAX))&0xffffffff
  sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+adapters[a])
u.hook_add(UC_HOOK_CODE,hook)
def call(a,eax=0):
 put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.reg_write(UC_X86_REG_EAX,eax);
 try:u.emu_start(a,0x100fff0,count=100000)
 except Exception:
  print(hex(a),hex(u.reg_read(UC_X86_REG_EIP)),hex(u.reg_read(UC_X86_REG_ESP)));raise
 assert u.reg_read(UC_X86_REG_EIP) in [0x100fff0,0x407794,0x4078a6], ('instruction budget exhausted',hex(a),hex(u.reg_read(UC_X86_REG_EIP)))
def snapshot():
 return dict(ball=list(u.mem_read(0x43e568,100)),fields=list(u.mem_read(0x43f000,0x3c0)),record=list(u.mem_read(0x43ee24,52)),mode=get(0x43e7a0),score=score,bonus=get(0x43d6e8),ball_number=w(0x43d6ee),extra=w(0x43d6f0),multiplier=w(0x43d6f2),held=w(0x43d6f4),display=[get(a) for a in [0x43e73c,0x43e7e4,0x43e738,0x43e734,0x43e714,0x43e718]])
source=json.loads((R/'analysis/traces/mean-capture-flight-original.json').read_text());cases=[];expected=[]
for i in range(72):
 u.mem_write(0x400000,image);u.mem_write(0x43f000,bytes(0x3c0));u.mem_write(0x43ee24,bytes(52));u.mem_write(0x43d6e0,bytes(24))
 ball=source['flights'][i%3][-1];u.mem_write(0x43e568,bytes(ball));bonus=[0,500000,123456789,0xffffffff][i%4];mult=[1,2,3][(i//4)%3];extra=(i//12)%2;held=(i//6)%2;suppressed=(i//3)%2;engine3c=1996+i;services=1 if i<24 or i>=48 else 0;timer=-1 if services else [0,50,400][i%3];count=1 if services else 1+i%2
 for a,v in [(0x43e740,0x1001000),(0x1001004,0x1001100),(0x100100c,0x1001400),(0x1001108,0x1001200),(0x1001200,0x41aaac),(0x1001210,0x41ab94),(0x1001214,0x419f6c),(0x1001218,0x419ad8),(0x100121c,0x419b00),(0x1001238,0x419554),(0x43f068,0x43e770),(0x43f0d0,0x1002000),(0x100201c,services),(0x1002034,0x1003020),(0x1002024,0x408084),(0x1002010,0x43d6e0),(0x100204c,0x4060a4),(0x100203c,0x406680),(0x1002088,0x1003000),(0x1002058,0x1003010),(0x1002090,0x1003000),(0x43d858,0x43d6e0),(0x43d8a0,0x1003010),(0x43e770,count),(0x43e774,1),(0x43e778,1),(0x43e7a0,2),(0x43e7ac,engine3c),(0x43d864,suppressed),(0x43d6e8,bonus)]:put(a,v)
 for j,v in enumerate([3,0x6040,0x1100000+0x959f6,0x1100000+0x9ba36,0x1100000+0xb3b36]):put(0x43f06c+j*4,v)
 word(0x438af4,0);word(0x438a40,0);put(0x438af8,0);put(0x438b44,0);put(0x438b4c,0);u.mem_write(0x43ee1c,bytes(8))
 word(0x43f3ae,timer);word(0x43d6ee,1);word(0x43d6f0,extra);word(0x43d6f2,mult);word(0x43d6f4,held)
 for a in [0x43e73c,0x43e7e4,0x43e734,0x43e714,0x43e718]:put(a,0)
 put(0x43e738,1);score=0;finished=False
 cases.append(dict(ball=ball,fields=list(u.mem_read(0x43f000,0x3c0)),bonus=bonus,multiplier=mult,extra=extra,held=held,suppressed=suppressed,engine3c=engine3c,services=services,timer=timer,count=count,fast=i>=48));rows=[]
 # Observe intercept before its engine service24, then execute engine with real save.
 adapters[0x408084]=0;call(0x41aaac,0x43e568);rows.append(snapshot());del adapters[0x408084]
 if services==0:
  call(0x41ab94,0x43e568);word(0x43e5c0,0);rows.append(snapshot());expected.append(rows);continue
 call(0x408084,0x43e568);rows.append(snapshot())
 if i>=48:put(0x43e734,3)
 for tick in range(500):
  call(0x4072cc);rows.append(snapshot())
  if finished:break
 assert finished
 finish_call=True;call(0x407794);finish_call=False;rows.append(snapshot())
 call(0x41ab94,0x43e568);word(0x43e5c0,0);rows.append(snapshot());expected.append(rows)
actual=json.loads(subprocess.run([sys.argv[1]],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout)
assert len(actual)==len(expected)
for ci,(aa,bb) in enumerate(zip(actual,expected)):
 assert len(aa)==len(bb),(ci,'length',len(aa),len(bb))
 for ti,(a,b) in enumerate(zip(aa,bb)):
  if a!=b:
   print('different field values',[(hex(j),a['fields'][j],b['fields'][j]) for j in range(0x3c0) if a['fields'][j]!=b['fields'][j]])
   raise AssertionError((ci,ti,{k:([j for j,(x,y) in enumerate(zip(a[k],b[k])) if x!=y] if isinstance(a[k],list) else [a[k],b[k]]) for k in a if a[k]!=b[k]}))
report=dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='48 controlled single-player expired-save drain chains (24 accelerated) and24 direct-save contexts; save service34/40f754 scheduling adapters excluded; actual41aaac/408084/419ad8/4072cc/419554/407794/419b00/41ab94; drawing/audio/lamp rebuild adapters excluded, no live tick or Full game-over threshold proof',cases=cases,expected=expected)
(R/'analysis/traces/mean-drain-chain-original.json').write_text(json.dumps(report,separators=(',',':'))+'\n');print('PASS',len(cases),'chains;',sum(map(len,expected)),'full state snapshots')
