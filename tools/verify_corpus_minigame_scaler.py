#!/usr/bin/env python3
"""Original three-build scaler microtrace and Demo dispatcher branch proof."""
import hashlib,itertools,json,struct
from pathlib import Path
import pefile
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ECX,UC_X86_REG_EIP
R=Path(__file__).resolve().parents[1]
meta=json.loads((R/'analysis/windows-symbol-map.json').read_text())['builds']
byhash={b['sha256']:b for b in meta}
configs=[('demo','31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00',0x418842,2),('retail','185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6',0x425282,4),('fix','5054441d4966efc4cdf14edef6061bad9c8af70ea56ec7f772d69cdc16612667',0x425652,4)]
records=[];images={};md=Cs(CS_ARCH_X86,CS_MODE_32)
for name,sha,start,factor in configs:
 path=R/byhash[sha]['path'];raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==sha
 image=pefile.PE(data=raw).get_memory_mapped_image();images[name]=image
 ins=list(md.disasm(image[start-0x400000:start-0x400000+21],start))
 assert [i.mnemonic for i in ins]==['mov','lea','sub','mov']
 address=struct.unpack('<I',ins[0].bytes[2:6])[0];assert ins[1].bytes[-4:]==bytes(4)
 u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image)
 cases=[]
 for remaining,magnitude in itertools.product([0,1,2,3,4,100,0x100000,0x7fffffff],[1,2,16,65536,0x100000]):
  u.mem_write(address,struct.pack('<I',remaining));u.reg_write(UC_X86_REG_ECX,magnitude)
  u.emu_start(start,start+21,count=20);assert u.reg_read(UC_X86_REG_EIP)==start+21
  result=struct.unpack('<I',u.mem_read(address,4))[0];assert result==(remaining-factor*magnitude)&0xffffffff
  cases.append(dict(initial=remaining,magnitude=magnitude,final=result,negative=bool(result&0x80000000)))
 records.append(dict(build=name,path=str(path.relative_to(R)),sha256=sha,start=hex(start),counter_address=hex(address),factor=factor,cases=cases))
# The changed block is under 3a4==1; Drag Race's known variant2 selects418a81.
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_map(0x2000000,0x10000);u.mem_write(0x400000,images['demo'])
u.mem_write(0x43f0d0,struct.pack('<I',0x2001000));branches=[]
def stop(uc,a,n,c):
 if a in [0x418113,0x418a81]:uc.emu_stop()
u.hook_add(UC_HOOK_CODE,stop)
from unicorn.x86_const import UC_X86_REG_ESP
for variant,target in [(1,0x418113),(2,0x418a81)]:
 u.mem_write(0x43f3a4,struct.pack('<H',variant));u.reg_write(UC_X86_REG_ESP,0x200f000)
 u.emu_start(0x4180d0,0x4192c6,count=40);assert u.reg_read(UC_X86_REG_EIP)==target
 branches.append(dict(field_3a4=variant,branch=hex(target)))
report=dict(schema=1,status='VERIFIED bounded arithmetic and dispatcher branch',builds=records,dispatch=branches,claim='Demo variant1 counter loses2*magnitude; Retail/Fix lose4*magnitude. Known Drag Race variant2 branches past this block.',limits=['Synthetic magnitude at arithmetic boundary; no full minigame trajectory or upstream projection equivalence.','Counter43effc semantics not renamed; draw loop4183bc reads its highWORD into up-to20 marker loop, suggesting resource/energy display.','Formula1 identification from selected3 native entry plus rulebook is STRONG, distinct from proved variant selector.'])
(R/'analysis/corpus-minigame-scaler.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS 120 original scaler cases, 2 dispatcher branches; changed block is variant1, not Drag Race variant2')
if __name__=='__main__': pass
