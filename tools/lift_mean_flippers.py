#!/usr/bin/env python3
"""Generate bounded native C++ for original demo flipper routines (temporary lift)."""
import argparse,hashlib
from pathlib import Path
import pefile,capstone
from capstone.x86 import *
R={'eax':(0,4,0),'ecx':(1,4,0),'edx':(2,4,0),'ebx':(3,4,0),'esp':(4,4,0),'ebp':(5,4,0),'esi':(6,4,0),'edi':(7,4,0)}
for name,idx in [('a',0),('c',1),('d',2),('b',3)]:
 R[name+'x']=(idx,2,0);R[name+'l']=(idx,1,0);R[name+'h']=(idx,1,8)
for name,idx in [('sp',4),('bp',5),('si',6),('di',7)]:R[name]=(idx,2,0)
RANGES=[(0x4084bc,0x4085e0),(0x4085e0,0x4086b8),(0x409050,0x4095f0),(0x4095f0,0x40964c),(0x40964c,0x40968c),(0x40968c,0x4096e8),(0x4096e8,0x409bb4),(0x409bb4,0x409bec),(0x409e18,0x409ecc)]
CALL_HANDLER = None
INSTRUCTION_LISTS = None
INSTRUCTION_HANDLER = None
def generate(exe, expected_sha='31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00'):
 raw=exe.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=expected_sha:raise ValueError('Unsupported original build')
 pe=pefile.PE(data=raw);image=bytearray(pe.get_memory_mapped_image())
 for section in pe.sections:
  if section.Name.rstrip(b'\0')==b'.bss':
   a=section.VirtualAddress;n=max(section.Misc_VirtualSize,section.SizeOfRawData);image[a:a+n]=bytes(n)
 image=bytes(image);c=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);c.detail=True
 out=['#include "physics/flipper_lift.h"','namespace slam {']+[f'void flipper_{a:x}(FlipperLift &m);' for a,b in RANGES]
 for start,end in RANGES:
  out.append(f'void flipper_{start:x}(FlipperLift &m) {{')
  if INSTRUCTION_LISTS is not None:out.append(f'goto L{start:x};')
  instructions=INSTRUCTION_LISTS[start] if INSTRUCTION_LISTS is not None else c.disasm(image[start-0x400000:end-0x400000],start)
  for i in instructions:
   def reg(x):
    idx,n,shift=R[i.reg_name(x)];return f'((m.r[{idx}]>>{shift})&{hex((1<<(n*8))-1)}u)'
   def addr(op):
    v=op.mem;parts=[f'{v.disp & 0xffffffff}u']
    if v.base:parts.append(reg(v.base))
    if v.index:parts.append(f'{reg(v.index)}*{v.scale}u')
    return '('+'+'.join(parts)+')'
   def read(op):
    if op.type==X86_OP_REG:return reg(op.reg)
    if op.type==X86_OP_IMM:return f'{op.imm&0xffffffff}u'
    if op.type==X86_OP_MEM:return f'm.rd({addr(op)},{op.size})'
    raise ValueError(i.op_str)
   def write(op,value):
    if op.type==X86_OP_MEM:return f'm.wr({addr(op)},{value},{op.size});'
    idx,n,shift=R[i.reg_name(op.reg)];mask=((1<<(n*8))-1)<<shift
    return f'm.r[{idx}]=(m.r[{idx}]&{hex((~mask)&0xffffffff)}u)|(({value}&{hex((1<<(n*8))-1)}u)<<{shift});'
   ops=i.operands;mn=i.mnemonic;line=''
   if INSTRUCTION_HANDLER is not None:
    custom=INSTRUCTION_HANDLER(i,read,write,start,end)
    if custom is not None:
     out.append(f'L{i.address:x}: {custom}')
     continue
   if mn in ['mov','movzx']:line=write(ops[0],read(ops[1]))
   elif mn=='movsx':line=write(ops[0],f'std::uint32_t(FlipperLift::sign({read(ops[1])},{ops[1].size}))')
   elif mn=='lea':line=write(ops[0],addr(ops[1]))
   elif mn in ['add','sub','and','or','xor']:
    a,b=read(ops[0]),read(ops[1]);n=ops[0].size
    v=f'm.{mn}({a},{b},{n})' if mn in ['add','sub'] else f'm.logic({a}{dict(and_="&",or_="|",xor="^").get(mn+"_", "^")}{b},{n})'
    line=write(ops[0],v)
   elif mn=='sbb':line=write(ops[0],f'm.sbb({read(ops[0])},{read(ops[1])},{ops[0].size})')
   elif mn in ['inc','dec','neg','not']:
    a=read(ops[0]);n=ops[0].size
    v=f'm.add({a},1,{n})' if mn=='inc' else f'm.sub({a},1,{n})' if mn=='dec' else f'm.sub(0,{a},{n})' if mn=='neg' else f'~{a}'
    line=write(ops[0],v)
   elif mn in ['cmp','test']:
    line=f'(void)m.sub({read(ops[0])},{read(ops[1])},{ops[0].size});' if mn=='cmp' else f'(void)m.logic({read(ops[0])}&{read(ops[1])},{ops[0].size});'
   elif mn in ['sar','shr','shl']:line=write(ops[0],f'm.shift({read(ops[0])},{read(ops[1])},{ops[0].size},{dict(shl=0,shr=1,sar=2)[mn]})')
   elif mn=='imul':
    if len(ops)==1:
     line='{ auto v=FlipperLift::sign(m.r[0],4)*FlipperLift::sign('+read(ops[0])+',4);m.r[0]=std::uint32_t(v);m.r[2]=std::uint32_t(std::uint64_t(v)>>32);m.o=m.c=(v!=FlipperLift::sign(m.r[0],4));}'
    else:
     a,b=(read(ops[0]),read(ops[1])) if len(ops)==2 else (read(ops[1]),read(ops[2]))
     line=write(ops[0],f'{a}*{b}')
   elif mn=='rol':
    n=ops[0].size;v=read(ops[0]);cnt=read(ops[1]);line='{ auto v='+v+';auto c=('+cnt+')%'+str(n*8)+';if(c){auto q=((v<<c)|(v>>('+str(n*8)+'-c)))&'+hex((1<<(n*8))-1)+'u;'+write(ops[0],'q')+'m.c=(q&1)!=0;m.o=(((q>>'+str(n*8-1)+')&1)!=m.c);}}'
   elif mn=='bswap':
    v=read(ops[0]);line='{auto v='+v+';'+write(ops[0],'((v&255)<<24)|((v&65280)<<8)|((v>>8)&65280)|(v>>24)')+'}'
   elif mn=='cdq':line='m.r[2]=(m.r[0]&0x80000000u)?0xffffffffu:0;'
   elif mn in ['div','idiv']:
    line='{ std::uint64_t bits=(std::uint64_t(m.r[2])<<32)|m.r[0]; '
    if mn=='idiv':line+='std::int64_t a; std::memcpy(&a,&bits,8); auto b=FlipperLift::sign('+read(ops[0])+',4); if(!b)throw std::runtime_error("Lift divide zero");m.r[0]=std::uint32_t(a/b);m.r[2]=std::uint32_t(a%b);}'
    else:line+='auto b='+read(ops[0])+';if(!b)throw std::runtime_error("Lift divide zero");m.r[0]=std::uint32_t(bits/b);m.r[2]=std::uint32_t(bits%b);}'
   elif mn=='push':line=f'm.push({read(ops[0])});'
   elif mn=='pop':line=write(ops[0],'m.pop()')
   elif mn=='ret':line='(void)m.pop();'+(f'm.r[4]+={ops[0].imm}u;' if ops else '')+'return;'
   elif mn=='call' and CALL_HANDLER is not None:
    line=CALL_HANDLER(i,read)
   elif mn=='call':
    target=ops[0].imm
    if target not in [a for a,b in RANGES]:raise ValueError(f'Call outside bounded island {target:x}')
    line=f'm.push({i.address+i.size}u);flipper_{target:x}(m);'
   elif mn=='jmp':line=f'goto L{ops[0].imm:x};' if start<=ops[0].imm<end else f'flipper_{ops[0].imm:x}(m);return;'
   elif mn.startswith('j'):
    cond={'je':'m.z','jne':'!m.z','jl':'m.s!=m.o','jge':'m.s==m.o','jle':'m.z||(m.s!=m.o)','jg':'!m.z&&(m.s==m.o)','jb':'m.c','ja':'!m.c&&!m.z','jae':'!m.c','jbe':'m.c||m.z'}[mn]
    line=f'if({cond})goto L{ops[0].imm:x};' if start<=ops[0].imm<end else f'if({cond}) {{flipper_{ops[0].imm:x}(m);return;}}'
   elif mn=='movsd':line='m.wr(m.r[7],m.rd(m.r[6],4),4);m.r[7]+=4;m.r[6]+=4;'
   elif mn=='nop':line=';'
   else:raise ValueError(f'{i.address:x} {mn} {i.op_str}')
   out.append(f'L{i.address:x}: {line}')
  out.append('}')
 out.append('}')
 return '#include <cstring>\n'+ '\n'.join(out)+'\n',image
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('exe',type=Path);p.add_argument('output',type=Path);p.add_argument('--image',type=Path);a=p.parse_args();code,image=generate(a.exe);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(code)
 if a.image:a.image.write_bytes(image)
 print(f'Generated {len(code)} bytes of bounded static C++')
