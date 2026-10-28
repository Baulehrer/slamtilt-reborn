#!/usr/bin/env python3
"""Material3/4/5 normal response, base score and effect trigger vs original x86."""
import json, random, struct, subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_ESP
ROOT=Path(__file__).resolve().parents[1]
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000),(0x2100000,0x2000)]:u.mem_map(a,n)
u.mem_write(0x400000,(ROOT/'build/mean-prepared/pe-data.bin').read_bytes())
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
put(0x4298c8,0x1000000);put(0x43e764,0x42a1f8);put(0x43e744,0x42a9f8)
put(0x43e740,0x1001000);put(0x1001004,0x1001100);put(0x1001104,0x1001200);put(0x1001200,0x41e00c)
put(0x43f068,0x1003000);put(0x1003030,4)
for a in [0x43ee1c,0x43ee1e,0x43ee20,0x43ee22]:u.mem_write(a,b'\1\0')
put(0x43f0d0,0x1002000);put(0x1002058,0x2101000);put(0x100205c,0x2101010)
points=[]
def skip(uc,a,n,c):
 if a==0x2101000:points.append(uc.reg_read(UC_X86_REG_EAX))
 sp=uc.reg_read(UC_X86_REG_ESP);ret=struct.unpack('<I',uc.mem_read(sp,4))[0]
 uc.reg_write(UC_X86_REG_ESP,sp+4);uc.reg_write(UC_X86_REG_EIP,ret)
for a in [0x2101000,0x2101010,0x419da4,0x409d78]:u.hook_add(UC_HOOK_CODE,skip,begin=a,end=a)
rng=random.Random(1996);cases=[];expected=[]
for i in range(1000):
 b=bytearray(100);struct.pack_into('<ii',b,0,rng.randrange(320*65536),rng.randrange(616*65536))
 struct.pack_into('<ii',b,0x14,rng.randrange(-8*65536,8*65536),rng.randrange(-8*65536,8*65536))
 struct.pack_into('<H',b,0x1e,rng.randrange(4096));struct.pack_into('<H',b,0x3c,3+i%3)
 cases.append(dict(operation='wall_event',bytes=list(b),offset_x=0,offset_y=0))
 u.mem_write(0x1000000,bytes(b));u.mem_write(0x43f38a,b'\0\0')
 for addr in [0x438b08,0x438b14,0x438b38]:u.mem_write(addr,bytes(12))
 points.clear();put(0x200f000,0x2100000);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0)
 u.emu_start(0x409bec,0x2100000,count=20000)
 assert u.reg_read(UC_X86_REG_ESP)==0x200f004
 effect=next((a for a in [0x438b08,0x438b14,0x438b38] if struct.unpack('<I',u.mem_read(a+8,4))[0]),0)
 expected.append(dict(bytes=list(u.mem_read(0x1000000,100)),points=sum(points),field_438b_state=effect))
p=ROOT/'build/oracle/contact-event-cases.json';p.write_text(json.dumps(cases))
actual=json.loads(subprocess.check_output([str(ROOT/'build/native/mean_probe'),str(p),str(ROOT/'build/mean-prepared/lookup.bin')],text=True))
diff=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
report=dict(cases=len(cases),differences=diff,active_events=sum(x['points']>0 for x in expected),scope='Human mode material3/4/5; all100ball bytes + base score requests + effect-state selection. Separation, notification and419da4 rule service excluded; mode bonus43f38a=0')
(ROOT/'analysis/traces/mean-contact-event-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert actual==expected

# Regression for the actual material5 stop found on the second ball.
command=[str(ROOT/'build/native/mean_sim_probe'),str(ROOT/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT'),str(ROOT/'build/mean-prepared'),str(ROOT/'analysis/traces/mean-flight-100.json'),'6000','cycle']
a=json.loads(subprocess.check_output(command,text=True));b=json.loads(subprocess.check_output(command,text=True))
assert a==b and a['active'] and len(a['samples'])==6001
assert a['drains']>=2 and a['launches']>=3 and a['score']>75000
report.update(native_steps=6000,native_drains=a['drains'],native_launches=a['launches'],native_score=a['score'],native_deterministic=a==b)
(ROOT/'analysis/traces/mean-contact-event-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
