#!/usr/bin/env python3
"""Native profile layer writes vs original Demo40f8a0 with Retail directory records."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESP,UC_X86_REG_EIP
R=Path(__file__).resolve().parents[1]
profiles=json.loads((R/'analysis/table-profiles.json').read_text())['tables']
image=(R/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_map(0x1000000,0x10000);u.mem_write(0x400000,image)
cases=[];expected=[]
for name,p in profiles.items():
 for l in p['layers']:
  for seed in [0,1,17,255]:
   b=bytes((i*seed+seed)&255 for i in range(100));base=0x1100000
   u.mem_write(0x1000000,b)
   # Original initializer-derived directory; helper reads only selected entry.
   address=0x43f06c+l['layer']*20
   u.mem_write(address,struct.pack('<5I',l['planes'],l['stride'],base+l['normal_offset'],base+l['hit_offset'],base+l['render_offset']))
   u.mem_write(0x100f000,struct.pack('<I',0x100fff0));u.reg_write(UC_X86_REG_ESP,0x100f000)
   u.reg_write(UC_X86_REG_EAX,0x1000000);u.reg_write(UC_X86_REG_EDX,l['layer']+1)
   u.emu_start(0x40f8a0,0x100fff0,count=100);assert u.reg_read(UC_X86_REG_EIP)==0x100fff0
   cases.append(dict(table=name,layer=l['layer'],base=base,bytes=list(b)))
   expected.append(list(u.mem_read(0x1000000,100)))
a=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases),text=True));assert a==expected
(R/'analysis/traces/table-profile-layer-original.json').write_text(json.dumps(dict(scope='Original Demo40f8a0 helper with validated Retail initializer directory entries; all100ballbytes;not whole-table engine',image_sha256=hashlib.sha256(image).hexdigest(),cases=cases,expected=expected),separators=(',',':'))+'\n')
print('PASS',len(cases),'original layer writes across all four tables')
