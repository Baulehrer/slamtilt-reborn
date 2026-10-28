#!/usr/bin/env python3
import argparse,json,struct,hashlib,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
p=argparse.ArgumentParser();p.add_argument('--native',required=True);a=p.parse_args();r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(ad,v):u.mem_write(ad,struct.pack('<I',v&0xffffffff))
def get(ad):return struct.unpack('<I',u.mem_read(ad,4))[0]
events={};handle=0
def hook(uc,ad,n,data):
 if ad==0x1000400 or ad in [0x4194e4,0x419f6c,0x416fe0]:
  sp=uc.reg_read(UC_X86_REG_ESP)
  if ad==0x1000400:
   events['callback']=get(sp+12);uc.reg_write(UC_X86_REG_EAX,handle)
  uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if ad==0x1000400 else 0))
u.hook_add(UC_HOOK_CODE,hook);put(0x1003034,0x1000400)
cases=[];expected=[]
for right in [False,True]:
 for phase in [0,1,2]:
  for field39e in [0,2,3,7]:
   for field3aa in [-1,0,1,2,3]:
    for divisor in [-10,0,10,500]:
     for handle in [0,123]:
      f=bytearray((i*7)%256 for i in range(0x3c0))
      def word(o,v):f[o:o+2]=struct.pack('<H',v&65535)
      f[0x068:0x06c]=struct.pack('<I',0x1002000);f[0x0d0:0x0d4]=struct.pack('<I',0x1003000)
      f[0x030:0x034]=struct.pack('<I',divisor&0xffffffff);word(0x3a6,phase);word(0x39e,field39e);word(0x3aa,field3aa);word(0x3a8,129)
      lookup=0x210000;c=dict(fields=list(f),right=right,lookup=lookup,handle=handle);cases.append(c)
      u.mem_write(0x43f000,bytes(f));put(0x1002030,4);put(0x438be0,lookup);u.mem_write(0x438a40,struct.pack('<H',77));
      for ad in [0x438b64,0x438b70,0x438b7c,0x438b88,0x438b94]:put(ad,222)
      sp=0x100f000;u.mem_write(sp,b'\0'*(24 if right else 16)+struct.pack('<I',0x100fff0));u.reg_write(UC_X86_REG_ESP,sp);events={}
      u.emu_start(0x417849 if right else 0x41751c,0x100fff0,count=1000)
      mode=get(0x1002030);expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),field438a40=struct.unpack('<h',u.mem_read(0x438a40,2))[0],mode=mode,callback=events.get('callback',0),clear_slots=bool(events.get('callback') and handle),exit=mode==2))
actual=json.loads(subprocess.run([a.native],input=json.dumps(cases),capture_output=True,text=True,check=True).stdout)
for i,(x,y) in enumerate(zip(expected,actual)):
 if x!=y:raise AssertionError((i,[(hex(k),aa,bb) for k,(aa,bb) in enumerate(zip(x['fields'],y['fields'])) if aa!=bb],{k:v for k,v in x.items() if k!='fields'},{k:v for k,v in y.items() if k!='fields'}))
(r/'analysis/traces/mean-mode4-input-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Mode4 branches41751c/417849;actual40f754;service34 explicitreturn;exit4194e4/419f6c/416fe0 excluded',cases=cases,expected=expected),separators=(',',':'))+'\n');print(len(cases),'original/native mode4 input cases exact')
