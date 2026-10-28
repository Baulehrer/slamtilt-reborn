#!/usr/bin/env python3
import argparse,json,struct,hashlib,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
p=argparse.ArgumentParser();p.add_argument('--native',required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];directory=next((root/'build/corpus/win95/demo-1997').rglob('MEAN.DAT')).parent;mean=(directory/'MEAN.DAT').read_bytes();main=(directory/'MAIN.DAT').read_bytes();image=(root/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x100000);u.mem_map(0x1100000,0x200000);u.mem_write(0x1100000,mean);u.mem_write(0x1010000,main)
def put(ad,v):u.mem_write(ad,struct.pack('<I',v&0xffffffff))
def get(ad):return struct.unpack('<I',u.mem_read(ad,4))[0]
def call(ad):u.reg_write(UC_X86_REG_ESP,0x10ff000);put(0x10ff000,0x10ffff0);u.emu_start(ad,0x10ffff0,count=100000)
call(0x40af14);put(0x43e3e8,0x1000000);put(0x43e82c,0x1010000);put(0x43efd8,0x1100000);put(0x43f068,0x1002000);put(0x43f0d0,0x1003000)
for offset,target in [(0x3c,0x406680),(0x4c,0x4060a4),(0x50,0x40607c),(0x40,0x406280),(0x38,0x406574),(0x70,0x1004000),(0x68,0x1004000)]:put(0x1003000+offset,target)
def hook(uc,address,n,data):
 if address==0x1004000:
  sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,hook)
def fnv(data):
 h=14695981039346656037
 for v in data:h=((h^v)*1099511628211)&0xffffffffffffffff
 return str(h)
specs=[dict(callback=callback,score=0,flags=[0]*4,steps=steps,restore=restore) for callback,steps in [(0x412574,167),(0x41265c,300)] for restore in [0,1]]
specs += [dict(callback=0x41249c,score=score,flags=[0]*4,steps=116,restore=restore) for score in [0,30000000,45000000,75000000,4294967294] for restore in [0,1]]
specs += [dict(callback=0x4126ec,score=0,flags=[0]*4,steps=92,restore=restore) for restore in [0,1]]
expected=[]
for c in specs:
 put(0x1002014,c['callback']);put(0x100201c,0);put(0x43f050,c['score']);u.mem_write(0x43f1dc,bytes(c['flags']));u.mem_write(0x1000000,bytes(i%4 for i in range(1920)));frames=[]
 for offset,key in [(0x358,'field358'),(0x362,'field362'),(0x1fe,'field1fe'),(0x1f2,'field1f2')]:u.mem_write(0x43f000+offset,struct.pack('<H',c.get(key,0)))
 put(0x43efd0,0x1005000)
 source=bytes((i%4 if c.get('restore',0) else 0) for i in range(1920))
 packed=bytearray(480)
 for i,v in enumerate(source):
  packed[i//8] |= (v&1)<<(7-i%8)
  packed[240+i//8] |= ((v>>1)&1)<<(7-i%8)
 u.mem_write(0x1005000,bytes(packed))
 for n in range(c['steps']):
  call(c['callback']);frames.append(dict(active=get(0x1002014)!=0,counter=get(0x100201c),fnv=fnv(bytes(u.mem_read(0x1000000,1920)))))
 expected.append(frames)
actual=json.loads(subprocess.run([a.native,str(directory/'MEAN.DAT'),str(directory/'MAIN.DAT')],input=json.dumps(specs),capture_output=True,text=True,check=True).stdout)
for series,(original,native) in enumerate(zip(expected,actual)):
 assert len(original)==len(native)
 for frame,(x,y) in enumerate(zip(original,native)):assert x==y,(series,frame,x,y)
assert len(actual)==len(expected)
report=dict(image_sha256=hashlib.sha256(image).hexdigest(),mean_dat_sha256=hashlib.sha256(mean).hexdigest(),scope='Actual412574/41265c/41249c/4126ec and bitmap/font/mask pixel services; timeout20-tick lamp70/68 adapters skipped, shared scheduler excluded',series=specs,expected=expected)
(root/'analysis/traces/mean-mode4-dmd-original.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
print(f'{sum(c["steps"] for c in specs)} original/native callback pixel/state cases exact')
