#!/usr/bin/env python3
"""Compare two-plane decoder against actual40af14+406680, syntheticinputs."""
import json,struct,subprocess,random,hashlib
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX
root=Path(__file__).resolve().parents[1];u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000)]:u.mem_map(a,n)
u.mem_write(0x400000,(root/'build/mean-prepared/pe-data.bin').read_bytes())
def call(a):
 u.mem_write(0x200f000,struct.pack('<I',0x200fff0));u.reg_write(UC_X86_REG_ESP,0x200f000);u.emu_start(a,0x200fff0,count=20000)
call(0x40af14);u.mem_write(0x43e3e8,struct.pack('<I',0x1001000))
subprocess.run(['c++','-std=c++17','-Isrc','tests/windows_dmd_probe.cpp','-o','build/windows_dmd_probe'],check=True)
r=random.Random(0x406680);cases=[]
for case in range(32):
 data=bytes((i*17+case*11)&255 for i in range(480)) if case<16 else r.randbytes(480)
 u.mem_write(0x1000000,data);u.reg_write(UC_X86_REG_EAX,0x1000000);call(0x406680)
 expected=bytes(u.mem_read(0x1001000,1920));actual=subprocess.check_output(['build/windows_dmd_probe'],input=data)
 assert actual==expected,case
 cases.append(dict(input=data.hex(),expected_sha256=hashlib.sha256(expected).hexdigest()))
(root/'analysis/traces/windows-dmd-fixture.json').write_text(json.dumps(dict(scope='Original40af14 LUTsetup and406680 unpacker; two240byteplanes->96x20 level0..3',cases=cases),separators=(',',':'))+'\n')
print(json.dumps(dict(cases=32,pixels=61440,differences=0)))
