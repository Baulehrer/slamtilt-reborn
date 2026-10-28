#!/usr/bin/env python3
"""Bounded41c57a/41af2c phase0 switch effects; presentation calls excluded."""
import json,struct,subprocess,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
r=Path(__file__).resolve().parents[1];u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,(r/'build/mean-prepared/pe-data.bin').read_bytes());u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
events={}
def hook(uc,a,n,c):
 if a in [0x41c8af,0x41b615]:uc.emu_stop();return
 if a in [0x1000400,0x1000500,0x1000600,0x1000700,0x40f754,0x419f6c,0x416fe0]:
  sp=uc.reg_read(UC_X86_REG_ESP)
  if a==0x1000500:events['score']=uc.reg_read(UC_X86_REG_EAX)
  if a==0x1000600:events['audio84']=True
  if a==0x1000700:events['audio80']=True
  if a==0x1000400:events['callback']=get(sp+12);uc.reg_write(UC_X86_REG_EAX,0)
  if a==0x419f6c:events['rebuild']=True
  if a==0x416fe0:events['reset']=True
  uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if a==0x1000400 else 8 if a==0x40f754 else 0))
u.hook_add(UC_HOOK_CODE,hook)
for o,a in [(0x34,0x1000400),(0x58,0x1000500),(0x84,0x1000600),(0x80,0x1000700)]:put(0x1003000+o,a)
cases=[];expected=[]
for layer in [1,3]:
 for mode in [2,4]:
  for phase in [0,1,2]:
   for count in [-32768,-1,0,1,5,32767]:
    for bank in [-1,0,6000]:
     f=bytearray((i*7+count)%256 for i in range(0x3c0))
     for o,v in [(0x3a6,phase),(0x1f4,count),(0x37a,bank),(0x392,0)]:struct.pack_into('<h',f,o,v)
     struct.pack_into('<III',f,0x030,0,0,0);struct.pack_into('<I',f,0x068,0x1002000);struct.pack_into('<I',f,0x0d0,0x1003000)
     c=dict(fields=list(f),mode=mode,layer=layer,mask=1,x=150<<16,y=(390 if layer==1 else 63)<<16);cases.append(c)
     u.mem_write(0x43f000,bytes(f));put(0x1002030,mode);put(0x100f020 if layer==3 else 0x100f01c,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f008)
     events=dict(score=0,callback=0,audio84=False,audio80=False,rebuild=False,reset=False)
     u.emu_start(0x41c57a if layer==1 else 0x41af2c,0x100fff0,count=2000)
     expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),mode=get(0x1002030),**events))
exe=sys.argv[1] if len(sys.argv)>1 else str(r/'build/native/mean_mode4_switch_probe')
a=json.loads(subprocess.check_output([exe],input=json.dumps(cases).encode()))
for i,(x,y) in enumerate(zip(a,expected)):
 if x!=y:print('FAIL',i,[(hex(k),aa,bb) for k,(aa,bb) in enumerate(zip(x['fields'],y['fields'])) if aa!=bb],{k:(x[k],y[k]) for k in x if k!='fields' and x[k]!=y[k]});raise SystemExit(1)
(r/'analysis/traces/mean-mode4-switch-original.json').write_text(json.dumps(dict(scope='41c57a and41af2c reached after verified layer/mask/pose guards; services34/58/80/84 and40f754,419f6c,416fe0 excluded and recorded; mode2/4,phase0/1/2,signedcounts,banks',cases=len(cases),differences=0,records=[dict(input=c,output=e) for c,e in zip(cases,expected)]),separators=(',',':'))+'\n');print('PASS',len(cases))
