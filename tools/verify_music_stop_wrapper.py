#!/usr/bin/env python3
"""Execute three retained Retail music-stop wrappers on bounded test states.

Their real gameplay reachability is unproven. The stop-service body is hooked at
its entry; argument, branch and memory-write observations use original x86.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_EIP,UC_X86_REG_ESP

ROOT=Path(__file__).resolve().parents[1]
EXE=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE'
BUILD='185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
TABLES={'pirate':('pirate-full-tick',0x435134,0x43515a,0x46e2b0,0x46e2b4),
        'space':('space-full-game',0x44650c,0x446532,0x46ed20,0x46ed24),
        'demon':('demon-full-game',0x41761c,0x417642,0x46d60c,0x46d64c)}
def sha(data): return hashlib.sha256(data).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'build/music-stop-audit/stop-wrapper-original.json');a=p.parse_args()
    raw=EXE.read_bytes();assert sha(raw)==BUILD
    pe=pefile.PE(data=raw).get_memory_mapped_image()
    startup=json.loads((ROOT/'docs/verification/retail-music-start-2026-10-30.json').read_text())
    assert startup['original_build_sha256']==BUILD
    rows=[]
    for table,(prep,entry,end,engine_slot,api_slot) in TABLES.items():
        directory=ROOT/'build/oracle'/prep; evidence=next(x for x in startup['tables'] if x['table']==table)
        image=(directory/'human-image.bin').read_bytes();runtime=(directory/'human-runtime.bin').read_bytes()
        assert sha(image)==evidence['image_sha256'] and sha(runtime)==evidence['runtime_sha256']
        assert image[entry-0x400000:end-0x400000]==pe[entry-0x400000:end-0x400000]
        for state in (0,1):
            u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image)
            u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,runtime)
            u.mem_map(0x2000000,0x10000);u.mem_map(0x2100000,0x1000)
            def get(addr):return int.from_bytes(u.mem_read(addr,4),'little')
            def put(addr,value):u.mem_write(addr,struct.pack('<I',value&0xffffffff))
            engine=get(engine_slot);api=get(api_slot);service=get(api+0x80)
            assert engine==0x46c67c and service==0x406268
            put(engine+0x30,state);put(engine+0x44,0xdecafbad)
            calls=[]
            def on_service(uc,_pc,_size,_data):
                calls.append({'eax':uc.reg_read(UC_X86_REG_EAX),'edx':uc.reg_read(UC_X86_REG_EDX)})
                sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
            u.hook_add(UC_HOOK_CODE,on_service,begin=service,end=service)
            put(0x200f000,0x2100000);u.reg_write(UC_X86_REG_ESP,0x200f000)
            u.reg_write(UC_X86_REG_EAX,0x12345678);u.reg_write(UC_X86_REG_EDX,0x87654321)
            u.emu_start(entry,0x2100000,count=100)
            assert u.reg_read(UC_X86_REG_EIP)==0x2100000 and u.reg_read(UC_X86_REG_ESP)==0x200f004
            assert get(engine+0x44)==0 and len(calls)==(1 if state==0 else 0)
            assert u.reg_read(UC_X86_REG_EDX)==0x87654321
            rows.append({'table':table,'entry':hex(entry),'engine':hex(engine),'field_30':state,
                         'field_44_after':get(engine+0x44),'service_calls':len(calls),
                         'code_sha256':sha(image[entry-0x400000:end-0x400000])})
    report={'status':'VERIFIED_BOUNDED','original_build_sha256':BUILD,'cases':rows,
            'scope':'Original x86 instructions on initialized table snapshots with explicit test values in engine+0x30/+0x44. Service 0x80 hooked at entry; does not establish gameplay reachability, native implementation, or final audio.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print('3 Retail stop wrappers x 2 states: zero flag conditionally requests 0x80, both branches clear +0x44')
if __name__=='__main__':main()
