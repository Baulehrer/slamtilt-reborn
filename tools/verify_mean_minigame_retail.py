#!/usr/bin/env python3
"""Actual Retail/Fix code, translated cached entry context, compared to native profile."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
import pefile
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from capstone.x86 import X86_OP_IMM,X86_OP_MEM
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
R=Path(__file__).resolve().parents[1];meta=json.loads((R/'analysis/windows-symbol-map.json').read_text())['builds']
config=[('retail','185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6',0xca40,0x2eb10,0x9a0,0xf00),('fix','5054441d4966efc4cdf14edef6061bad9c8af70ea56ec7f772d69cdc16612667',0xce10,0x2fb10,0xc00,0x12d0)]
source=R/'build/mean-minigame-prepared';demo=(source/'image.bin').read_bytes();runtime=(source/'runtime.bin').read_bytes()
keys=json.loads((R/'analysis/traces/mean-minigame1-winning-input.json').read_text())['keys']
dat_path=next((R/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'));dat=dat_path.read_bytes()
md=Cs(CS_ARCH_X86,CS_MODE_32);md.detail=True
services=[0x405f98,0x406574,0x406680,0x406280,0x40617c,0x4060f8,0x4060a4,0x405c60,0x40560c,0x4058c8,0x4058a0,0x40587c,0x405814]
reports=[]
for name,sha,cd,gd,sd,nd in config:
 path=R/next(x['path'] for x in meta if x['sha256']==sha);raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==sha
 if name=='retail':assert next(path.parent.rglob('MEAN.DAT')).read_bytes()==dat, 'Retail/Demo MEAN.DAT mismatch'
 image=pefile.PE(data=raw).get_memory_mapped_image();mapping={a:a+sd for a in services};diffs=[];instruction_count=0
 for begin,end,delta in [(0x4180d0,0x4194e4,cd),(0x40e960,0x40ef9d,nd),(0x40f754,0x40f7d1,cd),(0x419da4,0x419e68,cd),(0x40f994,0x40fb78,cd),(0x40fb78,0x40fdcd,cd),(0x415bce,0x415d00,cd)]:
  aa=list(md.disasm(demo[begin-0x400000:end-0x400000],begin));bb=list(md.disasm(image[begin+delta-0x400000:end+delta-0x400000],begin+delta));assert len(aa)==len(bb)
  for a,b in zip(aa,bb):
   assert a.address+delta==b.address and a.mnemonic==b.mnemonic and len(a.operands)==len(b.operands),(a.address,b.address)
   instruction_count+=1
   for x,y in zip(a.operands,b.operands):
    assert x.type==y.type
    if x.type==X86_OP_IMM:
     if 0x400000<=x.imm<0x500000 and 0x400000<=y.imm<0x500000:
      assert mapping.setdefault(x.imm,y.imm)==y.imm
     elif x.imm!=y.imm:diffs.append((hex(a.address),x.imm,y.imm))
    elif x.type==X86_OP_MEM:
     if x.mem.scale!=y.mem.scale:diffs.append((hex(a.address),x.mem.scale,y.mem.scale))
     assert x.mem.base==y.mem.base and x.mem.index==y.mem.index
     if 0x400000<=x.mem.disp<0x500000:
      assert mapping.setdefault(x.mem.disp,y.mem.disp)==y.mem.disp
     else:assert x.mem.disp==y.mem.disp
    else:assert x.reg==y.reg
 assert diffs==[('0x418848',2,4),('0x419220',20000000,40000000),('0x4193c6',7,4),('0x40fb4f',20000000,40000000),('0x40fd77',20000000,40000000)],diffs
 u=Uc(UC_ARCH_X86,UC_MODE_32)
 for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000),(0x1100000,0x200000)]:u.mem_map(a,n)
 u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime);u.mem_write(0x1100000,dat)
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 # Original code stays untouched. Seed only the cached original capture context.
 u.mem_write(0x43ec3c+gd,demo[0x3ec3c:0x3f3c0])
 for old,new in mapping.items():
  if not (0x43ec3c<=old<0x43f3c0) and old>=0x429000:u.mem_write(new,demo[old-0x400000:old-0x400000+4])
 for off in range(0,len(runtime)-3,4):
  v=struct.unpack_from('<I',runtime,off)[0]
  if v in mapping:put(0x1000000+off,mapping[v])
 inverse={v:k for k,v in mapping.items()};points=[0];callback=[0]
 def adapter(uc,a,n,c):
  original=inverse[a];sp=uc.reg_read(UC_X86_REG_ESP);ret=get(sp)
  if original==0x40560c:points[0]=(points[0]+uc.reg_read(UC_X86_REG_EAX))&0xffffffff
  if original==0x405f98:callback[0]=inverse[get(sp+12)];uc.reg_write(UC_X86_REG_EAX,1)
  uc.reg_write(UC_X86_REG_EIP,ret);uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if original==0x405f98 else 4 if original==0x406280 else 8 if original==0x40617c else 0))
 for old in services+[0x40f91c,0x419f6c,0x416fe0]:
  u.hook_add(UC_HOOK_CODE,adapter,begin=mapping[old],end=mapping[old])
 initial_image=bytes(u.mem_read(0x400000,0x100000));initial_runtime=bytes(u.mem_read(0x1000000,0x10000))
 temporary=R/'build/mean-minigame-retail-input';temporary.mkdir(exist_ok=True)
 partial=keys[:1082]+[0]*8918;partial_path=temporary/'one-lap-abort.json';partial_path.write_text(json.dumps(dict(keys=partial)))
 for scenario,scenario_keys,scenario_path in [('win',keys,R/'analysis/traces/mean-minigame1-winning-input.json'),('one-lap-abort',partial,partial_path)]:
  u.mem_write(0x400000,initial_image);u.mem_write(0x1000000,initial_runtime);points[0]=0;callback[0]=0
  rows=[]
  for tick,key in enumerate(scenario_keys):
   put(0x1001054,-1 if key==1 else 0);put(0x1001058,-1 if key==2 else 0);put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000)
   u.emu_start(0x4180d0+cd,0x200fff0,count=100000)
   h=14695981039346656037
   for byte in u.mem_read(0x43ec3c+gd,480):h=((h^byte)*1099511628211)&0xffffffffffffffff
   rows.append(dict(fields=list(struct.unpack('<24I',u.mem_read(0x43efd8+gd,96))),active=get(0x1001044),mode=get(0x1001030),field_1fa=struct.unpack('<H',u.mem_read(0x43f1fa+gd,2))[0],points=points[0],callback=callback[0],packed_frame_fnv=str(h)))
   if not get(0x1001044):break
  native=json.loads(subprocess.check_output([sys.argv[1],str(source/'image.bin'),str(source/'runtime.bin'),str(dat_path),str(scenario_path),'retail']))
  assert len(native)==len(rows),(name,scenario,len(native),len(rows))
  for tick,(aa,bb) in enumerate(zip(native,rows)):assert aa==bb,(name,scenario,tick,{k:(aa[k],bb[k]) for k in aa if aa[k]!=bb[k]})
  assert (points[0],callback[0],rows[-1]['fields'][1])==((120000000,0x40fb78,4) if scenario=='win' else (40000000,0x40f994,2))
  reports.append(dict(build=name,scenario=scenario,build_sha256=sha,instructions=instruction_count,diffs=diffs,mapping={hex(aa):hex(bb) for aa,bb in mapping.items()},ticks=len(rows),points=points[0],callback=hex(callback[0]),initial_field_1fa=struct.unpack('<H',initial_image[0x3f1fa+gd:0x3f1fc+gd])[0],final_field_1fa=rows[-1]['field_1fa'],final_fields=rows[-1]['fields'],trace_sha256=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()))

(R/'analysis/traces/mean-minigame-retail-original.json').write_text(json.dumps(dict(scope='Actual unmodified Retail/Fix code with translated cached Demo selected3-capture context and compatible Demo DAT/LUT; external presentation/audio/scoring/lamp services adapted. Not Retail startup or whole-table equivalence.',dat_sha256=hashlib.sha256(dat).hexdigest(),builds=reports),indent=2)+'\n')
print('Retail/Fix entire normalized island and actual tick traces match native Retail profile',[(x['build'],x['ticks'],x['points']) for x in reports])
