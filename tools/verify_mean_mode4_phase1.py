#!/usr/bin/env python3
import argparse,json,struct,hashlib,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
p=argparse.ArgumentParser();p.add_argument('--native',required=True);p.add_argument('--numeric',action='store_true');a=p.parse_args();r=Path(__file__).resolve().parents[1];dat=next((r/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'));mean=dat.read_bytes();image=(r/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x100000);u.mem_map(0x1100000,0x200000);u.mem_write(0x1100000,mean)
def put(ad,v):u.mem_write(ad,struct.pack('<I',v&0xffffffff))
def get(ad):return struct.unpack('<I',u.mem_read(ad,4))[0]
def call(ad):put(0x10ff000,0x10ffff0);u.reg_write(UC_X86_REG_ESP,0x10ff000);u.emu_start(ad,0x10ffff0,count=100000);assert u.reg_read(UC_X86_REG_EIP)==0x10ffff0, "Original phase1 call exhausted instruction budget"
call(0x40af14);put(0x43e3e8,0x1000000);put(0x43efd8,0x1100000)
for offset,target in [(0x3c,0x406680),(0x40,0x1004000),(0x84,0x1005000),(0x8c,0x1006000)]:put(0x1003000+offset,target)
if a.numeric:
 main=dat.parent/'MAIN.DAT';u.mem_map(0x1300000,0x10000);u.mem_write(0x1300000,main.read_bytes());put(0x43e82c,0x1300000);put(0x1003040,0x406280)
events={}
def hook(uc,ad,n,data):
 if a.numeric and ad==0x406280:
  events.update(number=True,value=uc.reg_read(UC_X86_REG_EBX),eax=uc.reg_read(UC_X86_REG_EAX),edx=uc.reg_read(UC_X86_REG_EDX),ecx=uc.reg_read(UC_X86_REG_ECX));return
 if ad in [0x1004000,0x1005000,0x1006000]:
  sp=uc.reg_read(UC_X86_REG_ESP)
  if ad==0x1005000:
   assert (uc.reg_read(UC_X86_REG_EAX),uc.reg_read(UC_X86_REG_EDX))==(50,1);events['audio']=True
  if ad==0x1006000:events['service8c']=True
  if ad==0x1004000:events.update(number=True,value=uc.reg_read(UC_X86_REG_EBX),eax=uc.reg_read(UC_X86_REG_EAX),edx=uc.reg_read(UC_X86_REG_EDX),ecx=uc.reg_read(UC_X86_REG_ECX))
  uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+(4 if ad==0x1004000 else 0))
u.hook_add(UC_HOOK_CODE,hook)
cases=[];expected=[]
for phase in [-1,0,1,2,3]:
 for timer in ([0,1,18,19,20,99,100,499] if phase!=2 else [-1,0,-16,-159]):
  for scorecount in [-1,0,1,2,50]:
   f=bytearray((i*7)%256 for i in range(0x3c0));f[0x0d0:0x0d4]=struct.pack('<I',0x1003000)
   f[0x3aa:0x3ac]=struct.pack('<H',phase&65535);f[0x3a0:0x3a2]=struct.pack('<H',timer&65535);f[0x03c:0x040]=struct.pack('<I',scorecount&0xffffffff)
   cases.append(dict(fields=list(f)));u.mem_write(0x43f000,bytes(f));u.mem_write(0x1000000,b'\0'*1920);events=dict(audio=False,service8c=False,number=False,value=0,eax=0,edx=0,ecx=0);call(0x4141b8)
   expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),pixels=list(u.mem_read(0x1000000,1920)),**events))
actual=json.loads(subprocess.run([a.native,str(dat)]+(["--numeric"] if a.numeric else []),input=json.dumps(cases),capture_output=True,text=True,check=True).stdout)
for i,(x,y) in enumerate(zip(expected,actual)):
 if x!=y:raise AssertionError((i,[k for k in x if x[k]!=y[k]],[(hex(k),aa,bb) for k,(aa,bb) in enumerate(zip(x['fields'],y['fields'])) if aa!=bb],{k:v for k,v in x.items() if k not in ['fields','pixels']},{k:v for k,v in y.items() if k not in ['fields','pixels']}))
assert len(actual)==len(expected)
(r/('analysis/traces/mean-mode4-phase1-numeric-original.json' if a.numeric else 'analysis/traces/mean-mode4-phase1-original.json')).write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),mean_dat_sha256=hashlib.sha256(mean).hexdigest(),scope=('4141b8actual406680 plus actual406280 numeric font composition; audio services recorded; DMDschedulerexcluded' if a.numeric else '4141b8actual406680;numeric40/audioservicesrecorded;DMDschedulerexcluded;validframeindexdomain'),cases=cases,expected=expected),separators=(',',':'))+'\n');print(len(cases),'original/native phase1 pixel/state/service cases exact')
