#!/usr/bin/env python3
"""Single-player bookkeeping vs original x86, then native drain/relaunch regression."""
import json, random, struct, subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EDX
ROOT=Path(__file__).resolve().parents[1]
image=(ROOT/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x1000)
u.hook_add(UC_HOOK_CODE,lambda uc,a,n,c: uc.emu_stop() if a in (0x4077e4,0x407808) else None)
rng=random.Random(1996);cases=[];expected=[]
for i in range(256):
 # Original also sets player+12=1; presentation field is preinitialized.
 b=bytearray(100);struct.pack_into('<H',b,0x12,1)
 struct.pack_into('<HH',b,0xe,rng.randrange(65536),rng.choice([0,1,2,32767,32768,65535]))
 cases.append(dict(operation='advance_ball',bytes=list(b)))
 u.mem_write(0x1000000,bytes(b));u.reg_write(UC_X86_REG_EDX,0x1000000)
 # Stop at the original next-player selection; single-player counters complete.
 u.emu_start(0x4077bb,0,count=30)
 expected.append(list(u.mem_read(0x1000000,100)))
p=ROOT/'build/oracle/ball-cycle-cases.json';p.write_text(json.dumps(cases))
actual=json.loads(subprocess.check_output([str(ROOT/'build/native/mean_probe'),str(p),str(ROOT/'build/mean-prepared/lookup.bin')],text=True))
assert actual==expected,'Single-player bookkeeping differs from original'
command=[str(ROOT/'build/native/mean_sim_probe'),str(ROOT/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT'),str(ROOT/'build/mean-prepared'),str(ROOT/'analysis/traces/mean-flight-100.json'),'2500','cycle']
a=json.loads(subprocess.check_output(command,text=True));b=json.loads(subprocess.check_output(command,text=True))
assert a==b and a['drains']>=1 and a['launches']>=2 and a['ball_number']==a['drains']+1
assert len(a['samples'])==2501 and a['active']
report=dict(original_counter_cases=len(cases),differences=0,native_steps=2500,drains=a['drains'],launches=a['launches'],ball_number=a['ball_number'],deterministic=a==b,scope='Single-player counter component verified; bonus/DMD skipped, no game-over limit implemented')
(ROOT/'analysis/traces/mean-ball-cycle-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
