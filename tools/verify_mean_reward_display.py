#!/usr/bin/env python3
"""Execute actual original scheduler4071e8 with actual reward callback410a34."""
import json, struct, subprocess, sys
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP, UC_X86_REG_EIP, UC_X86_REG_EAX, UC_X86_REG_EDX, UC_X86_REG_ECX, UC_X86_REG_EBX
ROOT=Path(__file__).resolve().parents[1]
reward2='--reward2' in sys.argv
callback=0x410910 if reward2 else 0x410a34
last_frame=159 if reward2 else 168
u=Uc(UC_ARCH_X86, UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000)]:u.mem_map(a,n)
u.mem_write(0x400000,(ROOT/'build/mean-prepared/pe-data.bin').read_bytes())
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<i',u.mem_read(a,4))[0]
def stub(uc,a,n,ctx):
 sp=uc.reg_read(UC_X86_REG_ESP);target=struct.unpack('<I',uc.mem_read(sp,4))[0]
 uc.reg_write(UC_X86_REG_ESP,sp+4);uc.reg_write(UC_X86_REG_EIP,target)
put(0x43f068,0x43e770);put(0x43f0d0,0x1002000)
put(0x100201c,0);put(0x100203c,0x200ff00)
u.hook_add(UC_HOOK_CODE,stub,begin=0x200ff00,end=0x200ff00)
u.hook_add(UC_HOOK_CODE,stub,begin=0x40f91c,end=0x40f91c)
put(0x43e81c,0);put(0x43e7b4,0);put(0x43e7a0,2)
put(0x43e740,0x1003000);put(0x1003004,0x1004000);put(0x1004008,0x1005000);put(0x1005034,0x413b04)
put(0x43e780,0);put(0x43e7b0,0)
for i,value in enumerate([0x200fff0,0x22 if reward2 else 0x21,1,callback]):put(0x200f000+i*4,value)
u.reg_write(UC_X86_REG_ESP,0x200f000)
for reg,value in [(UC_X86_REG_EAX,8),(UC_X86_REG_EDX,7),(UC_X86_REG_ECX,2),(UC_X86_REG_EBX,0)]:u.reg_write(reg,value)
u.emu_start(0x405f98,0x200fff0,count=2000)
initial=dict(state=get(0x43e780),active=get(0x43e784),frame=get(0x43e78c),callback=get(0x43e790))
assert initial==dict(state=4,active=2,frame=0,callback=callback)
u.mem_write(0x43f364,struct.pack('<h',-1))
rows=[]
for tick in range(last_frame+3):
 put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000)
 u.emu_start(0x4071e8,0x200fff0,count=2000)
 rows.append(dict(tick=tick+1,state=get(0x43e780),active=get(0x43e784),frame=get(0x43e78c),gate=struct.unpack('<h',u.mem_read(0x43f364,2))[0]))
exe=ROOT/'build/mean-reward-display-probe'
subprocess.run(['c++','-std=c++17','-I'+str(ROOT/'src/physics'),str(ROOT/'tests/mean_reward_display_probe.cpp'),str(ROOT/'src/physics/mean_reward_display.cpp'),'-o',str(exe)],check=True)
actual=[list(map(int,x.split())) for x in subprocess.check_output([str(exe),str(last_frame)],text=True).splitlines()]
errors=[r['tick'] for r,a in zip(rows,actual) if [r[k] for k in ['state','active','frame','gate']]!=a]
report=dict(initial=initial,scope=f'actual405f98 start+4071e8 scheduler+{callback:x} callback+413b04 idle; only graphics services stubbed; isolated reward/no queued interruption',registration='40f09e/40f0fb:43f338 descriptor+34',display_order='404b15 tabledisplay419890 then404b18 scheduler4071e8 at50Hz',differences=errors,states=rows)
(ROOT/('analysis/traces/mean-reward2-display-original.json' if reward2 else 'analysis/traces/mean-reward-display-original.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(steps=len(rows),differences=errors,transitions=[r for i,r in enumerate(rows) if i==0 or r['state']!=rows[i-1]['state'] or r['active']!=rows[i-1]['active'] or r['gate']!=rows[i-1]['gate']])))
assert not errors
