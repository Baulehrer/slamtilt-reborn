#!/usr/bin/env python3
"""Bounded original4060a4/4060f8 pixels, fixture storeshashesonly."""
import argparse,hashlib,json,subprocess,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--dat',type=Path,required=True);p.add_argument('--mean-dat',type=Path,required=True);p.add_argument('--oracle',action='store_true');a=p.parse_args()
f=R/'analysis/traces/mean-bonus-pixels-original.json'
if a.oracle:
 from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
 from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_EDX,UC_X86_REG_ESP
 image=(R/'build/mean-prepared/pe-data.bin').read_bytes();dat=a.dat.read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_32)
 u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x100000)
 def put(ad,v):u.mem_write(ad,struct.pack('<I',v))
 u.mem_write(0x1010000,dat);put(0x43e82c,0x1010000);put(0x43e3e8,0x1000000)
 def call(ad):
  u.reg_write(UC_X86_REG_ESP,0x10ff000);put(0x10ff000,0x10ffff0);u.emu_start(ad,0x10ffff0,count=100000)
 cases=[]
 for level in range(7):
  for text,x in [('BONUS',7),('NO BONUS',4),('TOTAL SCORE',1),('BONUS HELD',2),('X BONUS',6),('0123456789',0)]:
   u.reg_write(UC_X86_REG_EAX,level);call(0x4060a4)
   u.mem_write(0x1001000,text.encode()+b'\0');u.reg_write(UC_X86_REG_EAX,x);u.reg_write(UC_X86_REG_EDX,1);u.reg_write(UC_X86_REG_EBX,0x1001000);call(0x4060f8)
   cases.append(dict(level=level,text=text,x=x,sha256=hashlib.sha256(bytes(u.mem_read(0x1000000,1920))).hexdigest()))
 # Execute the complete table stage1 callback withoriginalservices.
 call(0x40af14)
 mean=a.mean_dat.read_bytes();u.mem_map(0x1100000,0x200000);u.mem_write(0x1100000,mean)
 put(0x43efd8,0x1100000);put(0x43f0d0,0x1002000)
 put(0x1002000+0x4c,0x4060a4);put(0x1002000+0x3c,0x406680);put(0x43f028,0)
 intro=[]
 for counter in range(1,65):
  u.reg_write(UC_X86_REG_EAX,1);call(0x419554)
  assert u.reg_read(UC_X86_REG_EAX)==0
  intro.append(dict(counter=counter,sha256=hashlib.sha256(bytes(u.mem_read(0x1000000,1920))).hexdigest()))
 # Record exact tablecallback fields andreturn, services88/58 capturedexternally.
 from unicorn import UC_HOOK_CODE
 from unicorn.x86_const import UC_X86_REG_EIP
 awarded=[]
 def service(uc,address,size,ctx):
  if address not in (0x1003000,0x1003010):return
  if address==0x1003010:awarded.append(uc.reg_read(UC_X86_REG_EAX))
  sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,struct.unpack('<I',uc.mem_read(sp,4))[0]);uc.reg_write(UC_X86_REG_ESP,sp+4)
 u.hook_add(UC_HOOK_CODE,service);put(0x1002000+0x88,0x1003000);put(0x1002000+0x58,0x1003010);put(0x1002000+0x10,0x1004000);put(0x1004000+0xa,2<<16);put(0x43f02c,0)
 clock=[]
 for n in range(66):
  awarded.clear();u.reg_write(UC_X86_REG_EAX,1 if n else 0);call(0x419554)
  clock.append([struct.unpack('<I',u.mem_read(ad,4))[0] for ad in (0x43f028,0x43f02c)]+[u.reg_read(UC_X86_REG_EAX),awarded[0] if awarded else 0])
 data=dict(clock=clock,intro=intro,mean_dat_sha256=hashlib.sha256(mean).hexdigest(),image_sha256=hashlib.sha256(image).hexdigest(),dat_sha256=hashlib.sha256(dat).hexdigest(),addresses=['0x4060a4','0x4060f8','0x407410','0x407509','0x407607','0x4076a3'],cases=cases)
 f.write_text(json.dumps(data,separators=(',',':'))+'\n')
else:data=json.loads(f.read_text())
assert hashlib.sha256(a.dat.read_bytes()).hexdigest()==data['dat_sha256']
for c in data['cases']:
 actual=subprocess.check_output([str(a.native),str(a.dat),str(c['level']),c['text'],str(c['x'])]);assert hashlib.sha256(actual).hexdigest()==c['sha256'],c
assert hashlib.sha256(a.mean_dat.read_bytes()).hexdigest()==data['mean_dat_sha256']
for c in data['intro']:
 actual=subprocess.check_output([str(a.native),str(a.mean_dat),str(c['counter']),'intro']);assert hashlib.sha256(actual).hexdigest()==c['sha256'],c
actual=[list(map(int,line.split())) for line in subprocess.check_output([str(a.native),'clock','2'],text=True).splitlines()]
assert actual==data['clock']
print(json.dumps(dict(cases=len(data['cases'])+len(data['intro'])+len(data['clock']),differences=0)))
