#!/usr/bin/env python3
"""Bounded original mode entry with distinct preserved-field sentinels."""
import json, struct, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
prefix=(ROOT/'tools/trace_mean_upper_second.py').read_text().split('b=bytearray(100)')[0]
expected=[]
for all_lit,value,selection in __import__("itertools").product(range(2),[0,16,32],range(3)):
 exec(compile(prefix,'upper-harness','exec'))
 for a,v in [(0x43f1e6,selection),(0x43f372,12),(0x43f38c,13),(0x43f386,14),(0x43f3b4,15),(0x43f39c,16),(0x43f384,19),(0x43f394,-1),(0x43f36a,-1)]:u.mem_write(a,struct.pack('<h',v))
 for i in range(6):u.mem_write(0x43f044+i*2,struct.pack('<h',11))
 put(0x43f05c,17);put(0x43f058,18);put(0x1001038,value)
 if all_lit:u.mem_write(0x43f1e0,bytes([1]*5))
 b=bytearray(100);struct.pack_into('<HH',b,0x58,3,1);u.mem_write(0x1000000,bytes(b))
 put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000)
 u.emu_start(0x415330,0x200fff0,count=4000)
 expected.append({'044':[word(0x43f044+i*2) for i in range(6)],**{key:word(int('43f'+key,16)) for key in ['372','38c','386','3b4','39c','384']},'05c':get(0x43f05c),'058':get(0x43f058),'1e0':list(u.mem_read(0x43f1e0,5))})
probe=ROOT/'build/oracle/mean_mode5_begin_probe'
subprocess.run(['c++','-std=c++17','-Isrc','-Ibuild/native/_deps/json-src/include','tests/mean_mode5_begin_probe.cpp','src/physics/mean_mode5_left.cpp','src/physics/mean_mode_reset.cpp','src/physics/mean_upper_release.cpp','src/physics/mean_step.cpp','src/physics/mean_material_bundle.cpp','-o',str(probe)],cwd=ROOT,check=True)
actual=json.loads(subprocess.check_output([str(probe)],text=True))
report={'states':len(expected),'differences':[i for i,(x,y) in enumerate(zip(actual,expected)) if x!=y],'expected':expected,'scope':'Original415330 upper timer=-1->-2, selections0..2; distinct preserved-field sentinels; presentation services bounded.'}
(ROOT/'analysis/traces/mean-mode5-begin-fixture.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!="expected"}))
assert actual==expected,(actual,expected)
