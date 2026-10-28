#!/usr/bin/env python3
"""Native bounded Retail contact+response vs actual original for four table descriptors."""
import hashlib,json,random,struct,subprocess,sys
from pathlib import Path
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_MEM_INVALID
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESP,UC_X86_REG_EIP
R=Path(__file__).resolve().parents[1];des=json.loads((R/'analysis/corpus-table-descriptor-levers.json').read_text());raw=(R/des['build']).read_bytes();assert hashlib.sha256(raw).hexdigest()==des['build_sha256']
pe=pefile.PE(data=raw);image=bytearray(pe.get_memory_mapped_image());image.extend(bytes(0x100000-len(image)))
for s in pe.sections:
 if s.Name.rstrip(b'\0')==b'.bss':image[s.VirtualAddress:s.VirtualAddress+max(s.Misc_VirtualSize,s.SizeOfRawData)]=bytes(max(s.Misc_VirtualSize,s.SizeOfRawData))
demo=bytearray((R/'build/mean-prepared/pe-data.bin').read_bytes());demo.extend(bytes(0x100000-len(demo)));demo[0x3e700:0x3e7a0]=(R/'build/mean-prepared/engine-globals.bin').read_bytes()
atan=struct.unpack_from('<I',demo,0x3e728)[0];aux=struct.unpack_from('<I',demo,0x3e730)[0]
lookups=[(0x4e0000,(R/'build/mean-prepared/lookup.bin').read_bytes()),(0x4e3000,demo[atan-0x400000:atan-0x400000+2050]),(0x4e4000,demo[aux-0x400000:aux-0x400000+8192])]
work=R/'build/oracle/retail-flippers';work.mkdir(parents=True,exist_ok=True);records=[]
for table in des['tables']:
 u=Uc(UC_ARCH_X86,UC_MODE_32)
 for a,n in [(0x400000,0x100000),(0x1000000,0x1000),(0x2000000,0x10000),(0x2100000,0x1000)]:u.mem_map(a,n)
 u.mem_write(0x400000,bytes(image))
 def bad(uc,access,address,size,value,data):
  print(f"invalid memory {address:#x}, eip={uc.reg_read(UC_X86_REG_EIP):#x}",flush=True); return False
 u.hook_add(UC_HOOK_MEM_INVALID,bad)
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def run(a,stop=0x2100000):
  put(0x200f000,0x2100000);u.reg_write(UC_X86_REG_ESP,0x200f000);u.emu_start(a,stop,count=100000);assert u.reg_read(UC_X86_REG_EIP)==stop
 put(0x46c644,int(table['returned_descriptor'],16));run(0x405057,0x405153)
 for a,data in lookups:u.mem_write(a,bytes(data))
 for a,v in [(0x46c66c,0x4e0000),(0x46c648,0x4e0800),(0x46c638,0x4e3000),(0x46c640,0x4e4000)]:put(a,v)
 # Supply the same explicit original shared globals as the existing pose oracle.
 import capstone
 from capstone.x86 import X86_OP_MEM
 cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True
 aa=list(cs.disasm(demo[0x9050:0x9bb4],0x409050));bb=list(cs.disasm(image[0x9ce8:0xa84c],0x409ce8));assert len(aa)==len(bb)
 for a,b in zip(aa,bb):
  assert a.mnemonic==b.mnemonic
  for x,y in zip(a.operands,b.operands):
   if x.type==X86_OP_MEM and not x.mem.base and not x.mem.index and x.mem.disp>=0x400000 and x.mem.disp not in (0x43e744,0x43e764,0x43e728,0x43e730):
    put(y.mem.disp,struct.unpack_from('<I',demo,x.mem.disp-0x400000)[0])
 context=bytes(u.mem_read(0x400000,0x100000));path=work/(table['table']+'-image.bin');path.write_bytes(context)
 third=struct.unpack_from('<H',context,int(table['graphics_descriptor'],16)-0x400000+0x1c)[0]
 rng=random.Random(1996);cases=[];expected=[];hits=0
 for i in range(600):
  u.mem_write(0x400000,context);idx=i%(3 if third else 2);addr=0x46c77c-idx*26;px,py=struct.unpack('<hh',u.mem_read(addr,4))
  b=bytearray(100);struct.pack_into('<ii',b,0,(px+rng.randrange(-65,66))<<16,(py+rng.randrange(-20,21))<<16);struct.pack_into('<ii',b,0x14,rng.randrange(-393216,393216),rng.randrange(-393216,393216));struct.pack_into('<H',b,0x28,40)
  cases.append(dict(bytes=list(b),index=idx));u.mem_write(0x1000000,bytes(b));u.reg_write(UC_X86_REG_EAX,0x1000000);u.reg_write(UC_X86_REG_EDX,addr);run(0x409ce8);result=u.reg_read(UC_X86_REG_EAX)
  if result==0:hits+=1;u.reg_write(UC_X86_REG_EAX,0x1000000);u.reg_write(UC_X86_REG_EDX,addr);run(0x40a380)
  expected.append(dict(result=result,bytes=list(u.mem_read(0x1000000,100)),scratch=struct.unpack('<I',u.mem_read(0x46c660,4))[0]))
 cf=work/(table['table']+'-cases.json');cf.write_text(json.dumps(cases));a=json.loads(subprocess.check_output([sys.argv[1],str(path),str(cf)],text=True));assert len(a)==len(expected)
 for i,(x,y) in enumerate(zip(a,expected)):assert x==y,(table['table'],i,x,y)
 records.append(dict(table=table['table'],cases=600,hits=hits,context_sha256=hashlib.sha256(context).hexdigest(),inputs=cases,expected=expected));print('PASS',table['table'],600,'Retail contact/response cases;',hits,'hits')
(R/'analysis/traces/retail-flipper-contact-original.json').write_text(json.dumps(dict(build_sha256=des['build_sha256'],scope='Actual Retail startup parameter copy; cold BSS plus explicit original Demo-derived shared globals and trig/atan/aux tables; synthetic ball coordinates/velocities; contact and response compiled exact, not live whole-game proof or Demo/Retail equality',records=records),separators=(',',':'))+'\n')
