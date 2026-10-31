#!/usr/bin/env python3
"""Compare Original/native Demon callback 0x413048 on controlled states.

Only the callback boundary is executed. Counter, phase, position, prior index,
dispatcher and service stubs are adapted; no natural gameplay reachability,
real graphics, original queue cadence or physical playback is inferred.
"""
import argparse
import hashlib
import json
import struct
import subprocess
from pathlib import Path

import pefile
from unicorn import Uc, UC_ARCH_X86, UC_HOOK_BLOCK, UC_HOOK_CODE, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX
from unicorn.x86_const import UC_X86_REG_EDX, UC_X86_REG_ESI, UC_X86_REG_EDI
from unicorn.x86_const import UC_X86_REG_EBP, UC_X86_REG_EIP, UC_X86_REG_ESP, UC_X86_REG_EFLAGS

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
CONTEXT = ROOT/'build/oracle/demon-full-game'
EXE_SHA = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
DAT_SHA = '0d78f5dbc069c5082cecce06f9620385288f615c03c83696483a43f272069c4d'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    exe = (GAME/'SLAMTILT.EXE').read_bytes()
    summary = json.loads((CONTEXT/'summary.json').read_text())
    image, runtime, dat = [(CONTEXT/name).read_bytes() for name in
                           ('human-image.bin','human-runtime.bin','human-dat.bin')]
    assert digest(exe) == summary['build_sha256'] == EXE_SHA
    assert digest(dat) == summary['dat_sha256'] == DAT_SHA
    for name, value in (('human-image.bin',image),('human-runtime.bin',runtime),('human-dat.bin',dat)):
        assert digest(value) == summary['context_hashes'][name]
    pe = pefile.PE(data=exe)
    original_pe = pe.get_memory_mapped_image()
    assert image[0x13048:0x13118] == original_pe[0x13048:0x13118]
    cases = [{'counter':13, 'phase':phase, 'position':position << 8, 'previous':previous}
             for phase in (0,200,311,312,316) for position in (0,1,11,12,13)
             for previous in (0,1,11,0xffffffff)]
    u = Uc(UC_ARCH_X86, UC_MODE_32)
    for address, size in ((0x400000,0x100000),(0x1000000,0x400000),
                          (0x2000000,0x10000),(0x2100000,0x1000)):
        u.mem_map(address,size)
    blocks, events = set(), []
    u.hook_add(UC_HOOK_BLOCK, lambda _u, addr, size, _d: blocks.add((addr,size)) if addr < 0x500000 else None)

    def put(address, value):
        u.mem_write(address, struct.pack('<I', value & 0xffffffff))

    def get(address):
        return struct.unpack('<I',u.mem_read(address,4))[0]

    def service(uc, address, _size, _data):
        if address == 0x2100100:
            events.append([uc.reg_read(UC_X86_REG_EAX), uc.reg_read(UC_X86_REG_EDX),
                           uc.reg_read(UC_X86_REG_EBX)])
        else:
            assert address == 0x2100104
        sp = uc.reg_read(UC_X86_REG_ESP)
        uc.reg_write(UC_X86_REG_EIP,get(sp))
        uc.reg_write(UC_X86_REG_ESP,sp+4)
    u.hook_add(UC_HOOK_CODE,service,begin=0x2100100,end=0x2100104)
    expected = []
    for case in cases:
        u.mem_write(0x400000,image)
        u.mem_write(0x1000000,runtime)
        u.mem_write(0x1100000,dat)
        for address,value in ((0x46d60c,0x1000100),(0x100011c,case['counter']),
                              (0x46d5e0,case['phase']),(0x46d600,case['position']),
                              (0x463b64,case['previous']),(0x46d64c,0x1005000),
                              (0x100505c,0x2100100),(0x100503c,0x2100104),
                              (0x200f000,0x2100000)):
            put(address,value)
        for reg in (UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,UC_X86_REG_EDX,
                    UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP):
            u.reg_write(reg,0)
        u.reg_write(UC_X86_REG_EFLAGS,2)
        u.reg_write(UC_X86_REG_ESP,0x200f000)
        events.clear()
        u.emu_start(0x413048,0x2100000,count=10000)
        assert u.reg_read(UC_X86_REG_EIP) == 0x2100000
        remainder = (case['position'] >> 8) % 12
        emits = case['phase'] >= 312 and remainder != case['previous']
        assert events == ([[0x463308,7,6]] if emits else [])
        expected.append({'events':list(events),'counter':get(0x100011c),'previous':get(0x463b64)})
    for addr,size in blocks:
        assert 0x413048 <= addr and addr+size <= 0x413118
        off = pe.get_offset_from_rva(addr-0x400000)
        assert image[addr-0x400000:addr-0x400000+size] == exe[off:off+size]
    args.output.mkdir(parents=True,exist_ok=True)
    inputs = args.output/'cases.json'
    inputs.write_text(json.dumps(cases)+'\n')
    actual = json.loads(subprocess.check_output([str(args.native.resolve()),str(CONTEXT),str(inputs)]))
    assert actual == expected
    report = {'status':'VERIFIED_BOUNDED','scope':__doc__,'exe_sha256':EXE_SHA,
              'dat_sha256':DAT_SHA,'image_sha256':digest(image),'native_sha256':digest(args.native.read_bytes()),
              'callback':'0x413048','sample_descriptor':'0x463308','cases':len(cases),
              'emitting_cases':sum(bool(x['events']) for x in expected),
              'executed_original_blocks':len(blocks),
              'rule':'phase >= 312 and ((position >> 8) % 12) differs from previous',
              'service_arguments':{'edx':7,'ebx':6}}
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: {len(cases)} Demon callback states; {report["emitting_cases"]} Original/native sound requests')


if __name__ == '__main__':
    main()
