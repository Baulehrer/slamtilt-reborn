#!/usr/bin/env python3
"""Bounded selected4 entry and single-ball clock against original execution."""
import json,struct,subprocess
from pathlib import Path
exec((Path(__file__).parent/'trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
from unicorn.x86_const import UC_X86_REG_EBP,UC_X86_REG_ECX
u.mem_write(0x43f1e6,struct.pack('<h',4));u.mem_write(0x43f394,struct.pack('<h',-1));u.mem_write(0x43f36a,struct.pack('<h',-1))
b=bytearray(100);struct.pack_into('<HH',b,0x58,3,1);u.mem_write(0x1000000,bytes(b))
def run(start,clock=False):
 put(0x200f000,0x200fff0)
 if clock:
  u.mem_write(0x200efe8,bytes(24));u.reg_write(UC_X86_REG_ESP,0x200efe8);u.reg_write(UC_X86_REG_EBP,5);u.reg_write(UC_X86_REG_ECX,0x1001000)
 else:u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000)
 u.emu_start(start,0x200fff0,count=20000)
def snapshot():
 return dict(timer=word(0x43f376),field36e=word(0x43f36e),field37e=word(0x43f37e),field388=word(0x43f388),data=list(u.mem_read(0x43f23c,24)),mode=get(0x1001030),selected=word(0x43f1e6),flags=list(u.mem_read(0x43f1e0,5)),field366=word(0x43f366),engine40=get(0x1001040),sum=get(0x43f058)&0xffffffff)
run(0x415330);states=[snapshot()]
for i in range(801):run(0x414e79,True);states.append(snapshot())
fixture={'scope':'Actual415330 selected4 entry and414e79 single-ball stage1 clock; actual mode selection/reset; DMD/audio services bounded; no multiball spawn','states':states}
(ROOT/'analysis/traces/mean-mode4-fixture.json').write_text(json.dumps(fixture,separators=(',',':'))+'\n')
print(json.dumps({'entry':states[0],'final':states[-1],'states':len(states)}))

subprocess.run(['c++','-std=c++17','-Isrc','-Ibuild/native/_deps/json-src/include','tests/mean_mode4_probe.cpp','src/physics/mean_mode5_clock.cpp','src/physics/mean_mode5_left.cpp','src/physics/mean_mode_reset.cpp','src/physics/mean_upper_release.cpp','src/physics/mean_step.cpp','src/physics/mean_material_bundle.cpp','-o','build/oracle/mean_mode4_probe'],check=True)
actual=json.loads(subprocess.check_output(['build/oracle/mean_mode4_probe']))
assert actual==states,[(i,a,b) for i,(a,b) in enumerate(zip(actual,states)) if a!=b][:1]
print(json.dumps({'verified_states':len(states),'differences':0}))
