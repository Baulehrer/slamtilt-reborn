#!/usr/bin/env python3
"""Bounded 41b8d0 oracle; explicit external-service boundaries."""
import hashlib,json,struct,subprocess,sys,itertools
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_32)
u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
services=[0x419da4,0x419f6c,0x4194e4,0x4169e4]
def hook(uc,a,n,d):
 if a not in services+[0x1000400,0x1000500,0x40f754]:return
 sp=uc.reg_read(UC_X86_REG_ESP);extra=0
 if a==0x1000400:
  events['callback_regs']=[uc.reg_read(x) for x in [UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ECX]];events['callback']=get(sp+12);events['args']=[struct.unpack('<i',uc.mem_read(sp+4,4))[0],struct.unpack('<i',uc.mem_read(sp+8,4))[0]];uc.reg_write(UC_X86_REG_EAX,returned);extra=12
 elif a==0x1000500:events['scores'].append(uc.reg_read(UC_X86_REG_EAX))
 elif a==0x40f754:events['control']=True;events['control_arg1']=get(sp+8);extra=8
 else:events['services'][services.index(a)]=True
 uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+extra)
u.hook_add(UC_HOOK_CODE,hook)
cases=[];expected=[]
# Valid original lamp indices plus signed timer/counter boundaries.
configs=[]
for selected,id,count,active in itertools.product([0,1,2,3,4],range(6),[0,4,5,6,32767,65535],[0,1]):configs.append((5,selected,id,count,active,0))
for id,bits,timer in itertools.product(range(6),range(8),[-1,0,1,32767]):configs.append((6,0,id,bits,1,timer))
configs.extend((mode,1,id,0,1,0) for mode in [1,2,3,4] for id in range(6))
for i,(mode,selected,id,count,active,timer) in enumerate(configs):
 f=bytearray(0x3c0);returned=0x10203040+i
 def w(o,v):struct.pack_into('<H',f,o,v&65535)
 w(0x1e6,selected);w(0x372,count);w(0x386,count);w(0x388,(i//2)%6);w(0x38c,(i//3)%6);w(0x39c,[-200,0,199,200,2000,32767][i%6]);w(0x35e,timer)
 for j,o in enumerate([0x38e,0x368,0x36c]):w(o,0 if count&(1<<j) else -1)
 for j in range(6):w(0x044+j*2,active)
 struct.pack_into('<I',f,0x058,0xfffffff0);struct.pack_into('<I',f,0x068,0x1002000);struct.pack_into('<I',f,0x0d0,0x1003000)
 u.mem_write(0x43f000,bytes(f));put(0x1002030,mode);put(0x1003034,0x1000400);put(0x1003058,0x1000500)
 events=dict(scores=[],callback=0,callback_regs=[7,6,2],args=[-1,-1],control=False,control_arg1=0,services=[False]*4)
 sp=0x100f000;put(sp,0x100fff0);u.reg_write(UC_X86_REG_ESP,sp);u.reg_write(UC_X86_REG_EAX,id);u.emu_start(0x41b8d0,0x100fff0,count=3000);assert u.reg_read(UC_X86_REG_EIP)==0x100fff0
 cases.append(dict(fields=list(f),mode=mode,id=id,returned=returned));expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),mode=get(0x1002030),**events))
actual=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases),text=True))
assert len(actual)==len(expected)
for i,(a,b) in enumerate(zip(actual,expected)):
 assert a==b,(i,{k:(a[k],b[k]) for k in a if a[k]!=b[k] and k!='fields'},[(hex(o),x,y) for o,(x,y) in enumerate(zip(a['fields'],b['fields'])) if x!=y])
(r/'analysis/traces/mean-shared-reward-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='41b8d0;419da4/419f6c/4194e4/4169e4/40f754 external explicit adapters;service34 returns controlled',cases=cases,expected=expected),separators=(',',':'))+'\n')
print(len(cases),'shared reward original states exact')
