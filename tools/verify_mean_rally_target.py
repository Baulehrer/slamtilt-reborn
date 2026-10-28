#!/usr/bin/env python3
"""4169e4 full native/original lamp and target comparison."""
import hashlib,json,struct,subprocess,sys,itertools
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EIP
r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_32)
u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def table(address,n):return list(struct.unpack('<'+'I'*n,image[address-0x400000:address-0x400000+n*4]))
directory=table(0x438ddc,6);targets=table(0x438df4,19);cases=[];expected=[]
for previous,count,rng in itertools.product(range(6),[0,1,4,5,6,65535],[0,1,15,16,32,48,255,0xffffffff]):
 f=bytearray((i*17+3)&255 for i in range(0x3c0));struct.pack_into('<H',f,0x38c,previous);struct.pack_into('<H',f,0x386,count);struct.pack_into('<I',f,0x068,0x1002000)
 u.mem_write(0x43f000,bytes(f));u.mem_write(0x1002038,struct.pack('<I',rng));u.mem_write(0x100f000,struct.pack('<I',0x100fff0));u.reg_write(UC_X86_REG_ESP,0x100f000);u.emu_start(0x4169e4,0x100fff0,count=300);assert u.reg_read(UC_X86_REG_EIP)==0x100fff0
 cases.append(dict(fields=list(f),mode=5,target_only=True,engine38=rng,directory=directory,targets=targets));expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),valid=True))
actual=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases),text=True))
assert len(actual)==len(expected)
for i,(a,b) in enumerate(zip(actual,expected)):assert a==b,(i,[(hex(o),x,y) for o,(x,y) in enumerate(zip(a['fields'],b['fields'])) if x!=y])
(r/'analysis/traces/mean-rally-target-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='4169e4;table438ddc6DWORD/table438df419DWORD;engine+38 explicit',cases=cases,expected=expected),separators=(',',':'))+'\n')
print(len(cases),'Rally target original states exact')
