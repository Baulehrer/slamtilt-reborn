#!/usr/bin/env python3
"""Bounded original x86 4186e5..41874e against native rotation input."""
import json, random, struct, subprocess
from pathlib import Path
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
ROOT=Path(__file__).resolve().parents[1]
exe=ROOT/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/SLAMTILT.EXE'
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000)
u.mem_write(0x400000,pefile.PE(str(exe)).get_memory_mapped_image())
u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
put(0x43f068,0x1001000)
r=random.Random(0x4186e5);cases=[]
for i in range(1024):
 angle=r.getrandbits(32);rate=r.getrandbits(32);a=r.getrandbits(32) if i>511 else i%2;b=r.getrandbits(32) if i>511 else (i//2)%2
 put(0x43efe8,angle);put(0x43eff8,rate);put(0x1001054,a);put(0x1001058,b)
 u.emu_start(0x4186e5,0x41874e,count=100)
 cases.append({'input':[angle,rate,a,b],'expected':[get(0x43efe8),get(0x43eff8)]})
probe=ROOT/'build/mean-minigame-input-probe'
subprocess.run(['c++','-std=c++17','-Isrc','tests/mean_minigame_input_probe.cpp','src/physics/mean_minigame_input.cpp','-o',str(probe)],cwd=ROOT,check=True)
p=subprocess.run([str(probe)],input=''.join(' '.join(map(str,c['input']))+'\n' for c in cases),text=True,capture_output=True,check=True)
actual=[list(map(int,line.split())) for line in p.stdout.splitlines()]
diff=[i for i,c in enumerate(cases) if actual[i]!=c['expected']]
result={'scope':'original 4186e5..41874e rotation input only; shared54/58 mapping not established','cases':cases,'differences':diff}
(ROOT/'analysis/traces/mean-minigame-input-fixture.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
print(json.dumps({'cases':len(cases),'differences':diff}));raise SystemExit(bool(diff))
