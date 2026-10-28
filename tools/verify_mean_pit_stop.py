#!/usr/bin/env python3
"""Actual41b61c bounded PitStop chains, explicit presentation admission adapters."""
import hashlib,json,struct,subprocess,sys,itertools
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
def hook(uc,a,n,d):
 if a not in [0x1000400,0x1000500,0x40f754]:return
 sp=uc.reg_read(UC_X86_REG_ESP);extra=0
 if a==0x1000400:
  events['requests'].append([get(sp+12)]+[uc.reg_read(z) for z in [UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ECX]]);uc.reg_write(UC_X86_REG_EAX,return_values[len(events["requests"])-1] if return_values is not None else returned);extra=12
 elif a==0x1000500:events['scores'].append(uc.reg_read(UC_X86_REG_EAX))
 else:
  if get(0x43f038):put(0x43f024,0);events['clear']=True
  extra=8
 uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+extra)
u.hook_add(UC_HOOK_CODE,hook);cases=[];expected=[];chains=[];return_values=None
for mode,returned,order in itertools.product([2,4,5,6],[0,0x12345678],[[0,1,2,3],[3,1,0,2]]):
 f=bytearray(0x3c0);struct.pack_into('<H',f,0x398,65535);struct.pack_into('<H',f,0x1d8,4);struct.pack_into('<I',f,0x024,123);struct.pack_into('<I',f,0x068,0x1002000);struct.pack_into('<I',f,0x0d0,0x1003000);af8=77;start=len(cases)
 # Duplicate hits must not add another puncture/repair.
 for id in (order[:1]*2+order[1:])*2:
  u.mem_write(0x43f000,bytes(f));put(0x438af8,af8);put(0x1002030,mode);put(0x1003034,0x1000400);put(0x1003058,0x1000500);events=dict(scores=[],requests=[],clear=False)
  cases.append(dict(fields=list(f),mode=mode,af8=af8,id=id,returned=returned));put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.reg_write(UC_X86_REG_EAX,id);u.emu_start(0x41b61c,0x100fff0,count=3000);assert u.reg_read(UC_X86_REG_EIP)==0x100fff0
  f=bytearray(u.mem_read(0x43f000,0x3c0));af8=struct.unpack('<i',u.mem_read(0x438af8,4))[0];expected.append(dict(fields=list(f),mode=get(0x1002030),af8=af8,**events))
 chains.append(dict(mode=mode,admission=returned,order=order,first_case=start,count=len(cases)-start))
# Distinctadmissions for the two requests on terminalpuncture/repair.
for repairing,return_values in itertools.product([False,True],[[0,0],[0,123],[123,0],[123,456]]):
 f=bytearray(0x3c0);struct.pack_into('<H',f,0x398,10 if repairing else 65535);struct.pack_into('<H',f,0x1d8,1);struct.pack_into('<H',f,0x3ac,3);struct.pack_into('<I',f,0x024,77);struct.pack_into('<I',f,0x068,0x1002000);struct.pack_into('<I',f,0x0d0,0x1003000)
 for j in range(3):f[(0x060 if repairing else 0x1d4)+j]=1
 u.mem_write(0x43f000,bytes(f));put(0x438af8,77);put(0x1002030,5);put(0x1003034,0x1000400);put(0x1003058,0x1000500);events=dict(scores=[],requests=[],clear=False)
 cases.append(dict(fields=list(f),mode=5,af8=77,id=3,returns=return_values));put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.reg_write(UC_X86_REG_EAX,3);u.emu_start(0x41b61c,0x100fff0,count=3000)
 expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),mode=get(0x1002030),af8=struct.unpack('<i',u.mem_read(0x438af8,4))[0],**events))
return_values=None
# Executeactual419890 up to419903 while explicitpriorhelpers are returnadapters.
def tick_hook(uc,a,n,d):
 if a in [0x417d68,0x419704,0x418094]:
  sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
 if a in [0x419903,0x419a97]:uc.emu_stop()
u.hook_add(UC_HOOK_CODE,tick_hook)
for timer,gate in itertools.product([-32768,-1,0,1,1500,32767],[0,1,2]):
 f=bytearray((i*7)%256 for i in range(0x3c0));struct.pack_into('<H',f,0x398,timer&65535);struct.pack_into('<I',f,0x0d0,0x1003000)
 u.mem_write(0x43f000,bytes(f));put(0x438af8,77);put(0x100301c,gate)
 for i in range(5):put(0x438b98+i*4,0x1004000+i*4);put(0x1004000+i*4,-1)
 put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.emu_start(0x419890,0x100fff0,count=3000)
 cases.append(dict(fields=list(f),mode=6,af8=77,tick=True,service1c=gate));expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),mode=6,af8=77,scores=[],requests=[],clear=False))
actual=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases),text=True));assert len(actual)==len(expected)
for i,(a,b) in enumerate(zip(actual,expected)):
 assert a==b,(i,{k:(a[k],b[k]) for k in a if a[k]!=b[k] and k!='fields'},[(hex(j),x,y) for j,(x,y) in enumerate(zip(a['fields'],b['fields'])) if x!=y])
(r/'analysis/traces/mean-pit-stop-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Actual41b61c; sequentialpuncture4/repair4/jackpot contexts; modes2/4/5/6 unchanged; service34 controlled,40f754 adapter applies accepted field024 clearing, capture-delay memory external; actualscore service values recorded; tick actual419890 through419903 with priorhelpers adapted, service1c gates and expiry boundary',chains=chains,cases=cases,expected=expected),separators=(',',':'))+'\n');print(len(cases),'PitStop original states exact')
