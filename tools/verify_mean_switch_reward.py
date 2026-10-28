#!/usr/bin/env python3
import argparse,json,struct,hashlib,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
p=argparse.ArgumentParser();p.add_argument('--native',required=True);a=p.parse_args();r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(ad,v):u.mem_write(ad,struct.pack('<I',v&0xffffffff))
def get(ad):return struct.unpack('<I',u.mem_read(ad,4))[0]
events={}
def hook(uc,ad,n,data):
 if ad in [0x1000400,0x1000500,0x1000600,0x40f754]:
  sp=uc.reg_read(UC_X86_REG_ESP)
  if ad==0x1000500:events['score']=uc.reg_read(UC_X86_REG_EAX)
  if ad==0x1000600:events['audio']=True
  if ad==0x1000400:uc.reg_write(UC_X86_REG_EAX,0)
  uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if ad==0x1000400 else 8 if ad==0x40f754 else 0))
u.hook_add(UC_HOOK_CODE,hook)
put(0x43f0d0,0x1003000)
for offset,target in [(0x34,0x1000400),(0x58,0x1000500),(0x84,0x1000600)]:put(0x1003000+offset,target)
cases=[];expected=[]
for selector in range(9):
 for cash in [0,1]:
  for seed in range(12):
   f=bytearray((i*7+seed)%256 for i in range(0x3c0))
   def word(o,v):f[o:o+2]=struct.pack('<H',v&65535)
   word(0x358,cash);word(0x362,selector);word(0x206,[-1,0,1,6,7,8][seed%6]);word(0x1fe,seed%3);word(0x1f2,seed%6);word(0x1fa,65535 if seed%2 else 0)
   f[0x038:0x03c]=b'\0'*4;f[0x0d0:0x0d4]=struct.pack('<I',0x1003000)
   cases.append(dict(fields=list(f)));u.mem_write(0x43f000,bytes(f));put(0x438af8,123);put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);events={'score':0,'audio':False}
   u.emu_start(0x41d3e4,0x100fff0,count=1000)
   expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),af8=get(0x438af8),**events))
actual=json.loads(subprocess.run([a.native],input=json.dumps(cases),capture_output=True,text=True,check=True).stdout)
assert len(actual)==len(expected)
for i,(x,y) in enumerate(zip(expected,actual)):
 if x!=y:
  diffs=[(hex(k),aa,bb) for k,(aa,bb) in enumerate(zip(x['fields'],y['fields'])) if aa!=bb]
  raise AssertionError((i,diffs,{k:v for k,v in x.items() if k!='fields'},{k:v for k,v in y.items() if k!='fields'}))
(r/'analysis/traces/mean-switch-reward-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Actual41d3e4..41d8af sevenbranches+cash;40f8ecactual,service34/58/84 recorded,40f754excluded',cases=cases,expected=expected),separators=(',',':'))+'\n')
print(len(cases),'original/native dispatcher cases exact')
