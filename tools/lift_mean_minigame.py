#!/usr/bin/env python3
"""Bounded static mini-game intermediate; original code stays local in build."""
from pathlib import Path
import sys
import lift_mean_flippers as g
from capstone.x86 import X86_OP_IMM
root=Path(__file__).resolve().parents[1]
g.RANGES=[(0x4180d0,0x4191f6),(0x4191f6,0x4192c6),(0x4192c6,0x4192d0),(0x4192d0,0x4194e4),(0x40e960,0x40ef9d),(0x419da4,0x419e68),(0x40f754,0x40f7d1)]
def call(i,read):
 target=i.operands[0]
 if target.type==X86_OP_IMM and target.imm in [a for a,b in g.RANGES]:
  return f'm.push({i.address+i.size}u);flipper_{target.imm:x}(m);'
 return f'm.service({read(target)});'
g.CALL_HANDLER=call
exe=next((root/'build/corpus/win95/demo-1997').rglob('SLAMTILT.EXE'))
code,_=g.generate(exe)
code=code.replace('physics/flipper_lift.h','physics/mean_minigame_lift.h').replace('FlipperLift','MeanMinigameLift').replace('flipper_','minigame_')
# Exact three Demo/Retail changes, verified across the entire normalized island.
replacements={
 'L418848: m.r[0]=(m.r[0]&0x0u)|(((0u+((m.r[1]>>0)&0xffffffffu)*2u)&0xffffffffu)<<0);':
 'L418848: m.r[0]=(m.r[0]&0x0u)|(((0u+((m.r[1]>>0)&0xffffffffu)*m.contact_decrement_scale())&0xffffffffu)<<0);',
 'L419220: m.r[0]=(m.r[0]&0x0u)|((((m.r[0]>>0)&0xffffffffu)*20000000u&0xffffffffu)<<0);':
 'L419220: m.r[0]=(m.r[0]&0x0u)|((((m.r[0]>>0)&0xffffffffu)*m.lap_award()&0xffffffffu)<<0);',
 'L4193c6: (void)m.sub(((m.r[7]>>0)&0xffffffffu),7u,4);':
 'L4193c6: (void)m.sub(((m.r[7]>>0)&0xffffffffu),m.completion_value(),4);'}
for before,after in replacements.items():
 assert code.count(before)==1,before
 code=code.replace(before,after)
out=root/'build/generated/mean_minigame.cpp' ;out.write_text(code)
print(f'Generated{len(code)}bytes of bounded mini-game C++')
