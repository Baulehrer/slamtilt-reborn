#!/usr/bin/env python3
"""Bounded rule-island instruction and relocated-address reuse proof."""
import hashlib,json,struct
from pathlib import Path
import pefile
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from capstone.x86 import X86_OP_IMM,X86_OP_MEM
R=Path(__file__).resolve().parents[1];meta=json.loads((R/'analysis/windows-symbol-map.json').read_text())['builds']
configs=[('demo','31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00',0),('retail','185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6',0xca40),('fix','5054441d4966efc4cdf14edef6061bad9c8af70ea56ec7f772d69cdc16612667',0xce10)]
images={};relocations={}
for name,sha,_ in configs:
 raw=(R/next(x['path'] for x in meta if x['sha256']==sha)).read_bytes();assert hashlib.sha256(raw).hexdigest()==sha;pe=pefile.PE(data=raw);images[name]=pe.get_memory_mapped_image();relocations[name]={pe.OPTIONAL_HEADER.ImageBase+e.rva for block in pe.DIRECTORY_ENTRY_BASERELOC for e in block.entries if e.type==3}
md=Cs(CS_ARCH_X86,CS_MODE_32);md.detail=True
ranges=[(0x4102c0,0x410504,'kickstart_result_family'),(0x4130cc,0x4131cc,'kickstart_intro'),(0x4141b8,0x4143b8,'kickstart_idle'),(0x41b010,0x41b10d,'kickstart_entry'),(0x41b2c9,0x41b491,'left_ramp_progress'),(0x41249c,0x412908,'cliff_dmd'),(0x4143b8,0x414553,'cliff_idle'),(0x414d30,0x414e79,'mode4_clock'),(0x41af2c,0x41affc,'cliff_success'),(0x415330,0x4180d0,'capture_input_modes'),(0x419da4,0x419e68,'bumper_mode_selection'),(0x419e68,0x419f6c,'player_init'),(0x419f6c,0x41aaac,'lamp_modes'),(0x41aaac,0x41ab94,'table_callback'),(0x41ab94,0x41ac30,'turn_gate'),(0x41b61c,0x41b8d0,'pit_stop'),(0x41b8d0,0x41bdd0,'shared_reward'),(0x41bdd0,0x41c0a3,'capture'),(0x41c0df,0x41c39e,'mode4'),(0x41c611,0x41c6d9,'right_cancel'),(0x41cb28,0x41cd50,'right_progress'),(0x41ce03,0x41d0fa,'award_bank'),(0x41d220,0x41d294,'award_update'),(0x41d3e4,0x41d8af,'switch_reward'),(0x41e00c,0x41e245,'stock_car_bumpers'),(0x41e269,0x41e7fe,'material5')]
reports=[]
for name,sha,delta in configs[1:]:
 mapping={};groups=[];total=0
 for begin,end,label in ranges:
  aa=list(md.disasm(images['demo'][begin-0x400000:end-0x400000],begin));bb=list(md.disasm(images[name][begin+delta-0x400000:end+delta-0x400000],begin+delta))
  assert len(aa)==len(bb),(name,label,len(aa),len(bb));normalized=[]
  for a,b in zip(aa,bb):
   assert a.address+delta==b.address and a.size==b.size and a.mnemonic==b.mnemonic and len(a.operands)==len(b.operands),(name,label,hex(a.address))
   xraw=bytearray(a.bytes);yraw=bytearray(b.bytes)
   for x,y in zip(a.operands,b.operands):
    assert x.type==y.type and x.size==y.size
    if x.type==X86_OP_IMM:
     if a.address+a.imm_offset in relocations['demo'] or a.mnemonic.startswith('j') or a.mnemonic=='call':
      assert mapping.setdefault(x.imm,y.imm)==y.imm
      if (a.mnemonic.startswith('j') or a.mnemonic=='call') and any(lo<=x.imm<hi for lo,hi,_ in ranges):assert y.imm-x.imm==delta,(label,hex(a.address),'branch target')
      xraw[a.imm_offset:a.imm_offset+a.imm_size]=bytes(a.imm_size);yraw[b.imm_offset:b.imm_offset+b.imm_size]=bytes(b.imm_size)
     else:assert x.imm==y.imm,(name,label,hex(a.address),x.imm,y.imm)
    elif x.type==X86_OP_MEM:
     assert x.mem.base==y.mem.base and x.mem.index==y.mem.index and x.mem.scale==y.mem.scale
     if a.address+a.disp_offset in relocations['demo']:
      assert mapping.setdefault(x.mem.disp,y.mem.disp)==y.mem.disp
      xraw[a.disp_offset:a.disp_offset+a.disp_size]=bytes(a.disp_size);yraw[b.disp_offset:b.disp_offset+b.disp_size]=bytes(b.disp_size)
     else:assert x.mem.disp==y.mem.disp
    else:assert x.reg==y.reg
   assert xraw==yraw,(name,label,hex(a.address),'opcode difference')
   normalized.extend(xraw)
  decoded_end=aa[-1].address+aa[-1].size if aa else begin
  assert decoded_end==end,(label,'partial decode',hex(decoded_end),hex(end))
  total+=len(aa);groups.append(dict(name=label,demo_range=[hex(begin),hex(end)],target_range=[hex(begin+delta),hex(end+delta)],instructions=len(aa),normalized_sha256=hashlib.sha256(bytes(normalized)).hexdigest()))
 tables=[]
 for address,count,label in [(0x438bdc,128,'mode4_lookup'),(0x438ddc,6,'rally_first'),(0x438df4,19,'rally_second')]:
  target=mapping[address];size=count*4;old=images['demo'][address-0x400000:address-0x400000+size];new=images[name][target-0x400000:target-0x400000+size]
  assert old==new,(name,label,'table differs')
  tables.append(dict(name=label,demo_address=hex(address),target_address=hex(target),dwords=count,sha256=hashlib.sha256(old).hexdigest()))
 reports.append(dict(tables=tables,build=name,build_sha256=sha,instructions=total,groups=groups,address_map={hex(a):hex(b) for a,b in mapping.items()}))
(R/'analysis/mean-rule-reuse.json').write_text(json.dumps(dict(scope='Bounded instruction/operand/opcode equivalence and consistent address map; not proof of indirect pointer initialization or complete runtime/table equivalence.',builds=reports),indent=2)+'\n')
print('PASS Mean rule reuse',[(x['build'],x['instructions']) for x in reports])
