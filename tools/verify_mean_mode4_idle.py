#!/usr/bin/env python3
import argparse,json,struct,hashlib,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
p=argparse.ArgumentParser();p.add_argument('--native',required=True);a=p.parse_args();r=Path(__file__).resolve().parents[1];dat=next((r/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'));mean=dat.read_bytes();image=(r/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x100000);u.mem_map(0x1100000,0x200000);u.mem_write(0x1100000,mean)
def put(ad,v):u.mem_write(ad,struct.pack('<I',v&0xffffffff))
def get(ad):return struct.unpack('<I',u.mem_read(ad,4))[0]
def call(ad):put(0x10ff000,0x10ffff0);u.reg_write(UC_X86_REG_ESP,0x10ff000);u.emu_start(ad,0x10ffff0,count=10000)
call(0x40af14);put(0x43e3e8,0x1000000);put(0x43efd8,0x1100000);put(0x100303c,0x406680);put(0x1003034,0x1004000)
events={};handle=0
def hook(uc,ad,n,data):
 if ad==0x406680:events['displayed']=True
 if ad==0x1004000:
  sp=uc.reg_read(UC_X86_REG_ESP);events['callback']=get(sp+12);uc.reg_write(UC_X86_REG_EAX,handle);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+16)
u.hook_add(UC_HOOK_CODE,hook)
cases=[];expected=[]
specs=[(state,counter,index) for state in [0,3,7] for counter,index in [(0,5),(3,8),(7,12),(11,16),(15,19)]]+[(3,counter,index) for counter,index in [(19,5),(23,9),(27,13),(31,17),(0x7fffffff,19)]]
for n,(state,counter,index) in enumerate(specs):
 handle=0 if n%2 else 123;lookup=0x18000+index*0x47af
 f=bytearray((i*7)%256 for i in range(0x3c0));f[0x0d0:0x0d4]=struct.pack('<I',0x1003000);f[0x39e:0x3a0]=struct.pack('<H',state);f[0x3a8:0x3aa]=b'\0\0'
 cases.append(dict(fields=list(f),counter=counter,lookup=lookup,handle=handle));u.mem_write(0x43f000,bytes(f));put(0x438af8,counter);put(0x438bdc,lookup);u.mem_write(0x1000000,bytes(i%4 for i in range(1920)));events={};call(0x4143b8)
 expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),counter=struct.unpack('<i',u.mem_read(0x438af8,4))[0],pixels=list(u.mem_read(0x1000000,1920)),callback=events.get('callback',0),clear_slots=bool(events.get('callback') and handle),displayed=events.get('displayed',False)))
actual=json.loads(subprocess.run([a.native,str(dat)],input=json.dumps(cases),capture_output=True,text=True,check=True).stdout)
for i,(x,y) in enumerate(zip(expected,actual)):
 if x!=y:raise AssertionError((i,[k for k in x if x[k]!=y[k]],[(j,v,y['pixels'][j]) for j,v in enumerate(x['pixels']) if v!=y['pixels'][j]][:20]))
assert len(actual)==len(expected)
(r/'analysis/traces/mean-mode4-idle-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),mean_dat_sha256=hashlib.sha256(mean).hexdigest(),scope='4143b8;actual406680/40f754;service34explicitreturn;sharedDMDschedulerexcluded',cases=cases,expected=expected),separators=(',',':'))+'\n');print(len(cases),'original/native mode4 idle pixel/state cases exact')
