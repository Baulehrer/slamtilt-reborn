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
 if ad==0x1000400 or ad in [0x419f6c,0x416fe0,0x1000500,0x1000600]:
  sp=uc.reg_read(UC_X86_REG_ESP)
  if ad in [0x1000500,0x1000600]:events['audio']=62 if ad==0x1000500 else -1
  if ad==0x1000400:
   events['callback']=get(sp+12);uc.reg_write(UC_X86_REG_EAX,handle)
  uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if ad==0x1000400 else 0))
u.hook_add(UC_HOOK_CODE,hook);put(0x1003034,0x1000400);put(0x1003084,0x1000500);put(0x1003080,0x1000600)
cases=[];expected=[]
for phase in [0,1,2]:
 for field39e in [0,3,7,15]:
  for field3aa in [-1,0,1,2,3]:
   for timer in [-32768,-1,0,1,18,19,349,350,32767]:
    for bank in [-1,0]:
     for handle in [0,123]:
      f=bytearray((i*7)%256 for i in range(0x3c0))
      def word(o,v):f[o:o+2]=struct.pack('<H',v&65535)
      f[0x068:0x06c]=struct.pack('<I',0x1002000);f[0x0d0:0x0d4]=struct.pack('<I',0x1003000)
      word(0x3a6,phase);word(0x39e,field39e);word(0x3aa,field3aa);word(0x396,timer);word(0x3a0,timer);word(0x3a8,timer);word(0x37a,bank)
      cases.append(dict(fields=list(f),handle=handle))
      u.mem_write(0x43f000,bytes(f));put(0x1002030,4);put(0x1002040,13);u.mem_write(0x438a40,struct.pack('<H',77));
      for ad in [0x438b64,0x438b70,0x438b7c,0x438b88,0x438b94]:put(ad,222)
      sp=0x100f000;u.mem_write(sp,b'\0'*24+struct.pack('<I',0x100fff0));u.reg_write(UC_X86_REG_ESP,sp);u.reg_write(UC_X86_REG_EAX,0x1003000);u.reg_write(UC_X86_REG_ECX,0x1002000);events={}
      u.emu_start(0x414d30,0x100fff0,count=1000)
      mode=get(0x1002030);expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),field438a40=struct.unpack('<h',u.mem_read(0x438a40,2))[0],mode=mode,engine40=get(0x1002040),callback=events.get('callback',0),clear_slots=bool(events.get('callback') and handle),exit=mode==2,audio=events.get('audio',0)))
actual=json.loads(subprocess.run([a.native],input=json.dumps(cases),capture_output=True,text=True,check=True).stdout)
for i,(x,y) in enumerate(zip(expected,actual)):
 if x!=y:raise AssertionError((i,[(hex(k),aa,bb) for k,(aa,bb) in enumerate(zip(x['fields'],y['fields'])) if aa!=bb],{k:v for k,v in x.items() if k!='fields'},{k:v for k,v in y.items() if k!='fields'}))
(r/'analysis/traces/mean-mode4-clock-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Mode4clock414d30..414e78;actual40f754;service34 explicitreturn;exit419f6c/416fe0 excluded',cases=cases,expected=expected),separators=(',',':'))+'\n');print(len(cases),'original/native mode4 clock cases exact')
