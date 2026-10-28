#!/usr/bin/env python3
"""Bounded actual40671c and404b48 nudge driver oracle; no tilt/gameplay claim."""
import argparse,hashlib,json,random,struct,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EDX
p=argparse.ArgumentParser();p.add_argument('--native',required=True);a=p.parse_args()
r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
u.hook_add(UC_HOOK_CODE,lambda uc,ad,n,data: uc.emu_stop() if ad==0x404a8a else None)
fields=[0x429858,0x42985c,0x42980c,0x429808,0x429810,0x43e564,0x43e410,0x43e724,0x43e71c,0x43e70c]
ht=image[0x29814:0x29814+68];vt=image[0x29860:0x29860+68]
rng=random.Random(671);cases=[];expected=[]
for operation in (0,1):
 for phase_h in (-2147483648,-2,-1,0,1,7,15,16,17,2147483647):
  for phase_v in (-2147483648,-2,-1,0,1,7,15,16,17,2147483647):
   for sign in (-1,0,1):
    vals=[rng.getrandbits(32) for _ in fields];vals[0]=0 if phase_h%2 else vals[0];vals[2]=0 if phase_v%2 else vals[2];vals[1]=phase_v&0xffffffff;vals[3]=sign&0xffffffff;vals[4]=phase_h&0xffffffff
    for ad,val in zip(fields,vals):u.mem_write(ad,struct.pack('<I',val))
    # Waveform aliases share contiguous memory with globals; restore the original LUT bytes.
    u.mem_write(0x429814,ht);u.mem_write(0x429860,vt)
    u.mem_write(0x100f000,struct.pack('<I',0x100fff0));u.reg_write(UC_X86_REG_ESP,0x100f000);u.reg_write(UC_X86_REG_EDX,0)
    if operation==0:u.emu_start(0x40671c,0x100fff0,count=300)
    else:u.emu_start(0x404b48,0x404b82,count=100)
    cases.append(struct.pack('<I',operation)+struct.pack('<10I',*vals)+ht+vt)
    expected.append(b''.join(bytes(u.mem_read(ad,4)) for ad in fields)+ht+vt)
# Complete bursts: repeat pending requests while the original wave is active,
# with actual four-physics-step / one-outer-loop cadence.
for sign in (-1,0,1):
 for upward in (False,True):
  vals=[0,0xffffffff,0,0,0xffffffff,0,0,0,0,0]
  for ad,val in zip(fields,vals):u.mem_write(ad,struct.pack('<I',val))
  u.mem_write(0x429814,ht);u.mem_write(0x429860,vt)
  for step in range(40):
   if step in (0,8):
    u.mem_write(0x42980c,struct.pack('<i',sign));u.mem_write(0x429858,struct.pack('<i',-1 if upward else 0))
   for operation in ([0,1] if step%4==3 else [0]):
    vals=[struct.unpack('<I',u.mem_read(ad,4))[0] for ad in fields]
    cases.append(struct.pack('<I',operation)+struct.pack('<10I',*vals)+ht+vt)
    u.mem_write(0x100f000,struct.pack('<I',0x100fff0));u.reg_write(UC_X86_REG_ESP,0x100f000);u.reg_write(UC_X86_REG_EDX,0)
    if operation==0:u.emu_start(0x40671c,0x100fff0,count=300)
    else:u.emu_start(0x404b48,0x404b82,count=100)
    expected.append(b''.join(bytes(u.mem_read(ad,4)) for ad in fields)+ht+vt)
result=subprocess.run([a.native],input=b''.join(cases),capture_output=True,check=True).stdout
assert len(result)==len(expected)*176,(len(result),len(expected))
for i,e in enumerate(expected):
 actual=result[i*176:(i+1)*176]
 assert actual==e,(i,struct.unpack('<10I',actual[:40]),struct.unpack('<10I',e[:40]))
out={'scope':__doc__,'image_sha256':hashlib.sha256(image).hexdigest(),'cases':len(cases),'fields':[hex(x) for x in fields],'driver':'0x40671c..0x406804','accept_pending':'0x404b48..0x404b82, EDX=0','lut_sha256':hashlib.sha256(ht+vt).hexdigest()}
(r/'analysis/traces/mean-nudge-original.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(cases),'original/native nudge cases')
