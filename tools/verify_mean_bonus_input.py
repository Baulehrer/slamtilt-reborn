#!/usr/bin/env python3
"""Original flipper edges driving existing bonus fast-forward state."""
import json,struct,subprocess,sys,hashlib
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EIP,UC_X86_REG_ESP
R=Path(__file__).resolve().parents[1];image=(R/'build/mean-prepared/pe-data.bin').read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v))
put(0x43e740,0x1001000);put(0x1001004,0x1001100);put(0x1001108,0x1001200)
cases=[];expected=[]
for flags in list(range(256))+[0x12345600,0xffffffff]:
 for right in [False,True]:
  for pressed in [False,True]:
   put(0x43e734,flags);u.reg_write(UC_X86_REG_ESP,0x100f000)
   start,end={(False,True):(0x40423e,0x404255),(False,False):(0x4042b1,0x4042d0),(True,True):(0x404347,0x40436c),(True,False):(0x4043bb,0x4043c2)}[right,pressed]
   u.emu_start(start,end,count=30);assert u.reg_read(UC_X86_REG_EIP)==end
   cases.append(dict(flags=flags,right=right,pressed=pressed));expected.append(struct.unpack('<I',u.mem_read(0x43e734,4))[0])
a=json.loads(subprocess.run([sys.argv[1]],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout);assert a==expected
(R/'analysis/traces/mean-bonus-input-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Original flipper input bit-write slices only; key mapping/guard/table callbacks excluded; bonus field734==3 acceleration already independently proven',cases=cases,expected=expected),separators=(',',':'))+'\n');print('PASS',len(cases),'original flipper/bonus bit writes')
