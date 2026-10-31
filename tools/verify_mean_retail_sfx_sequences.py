#!/usr/bin/env python3
"""Execute six bounded Mean Retail sound tables and retain service arguments.

The x86 table consumer and data are original; tick, table pointer, dispatcher
and queue are synthetic. It does not establish gameplay reachability or native
parity. No original sound bytes are emitted.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

import pefile
from unicorn import Uc, UC_ARCH_X86, UC_HOOK_BLOCK, UC_HOOK_CODE, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_EDX
from unicorn.x86_const import UC_X86_REG_EIP, UC_X86_REG_ESP

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE'
SHA = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
TABLES = (0x464128, 0x46415c, 0x464190, 0x4641c4, 0x4641f8, 0x46420c)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    exe = EXE.read_bytes()
    assert hashlib.sha256(exe).hexdigest() == SHA
    pe = pefile.PE(data=exe)
    image = pe.get_memory_mapped_image()
    results = []
    for table in TABLES:
        u = Uc(UC_ARCH_X86, UC_MODE_32)
        u.mem_map(0x400000, 0x100000)
        u.mem_write(0x400000, image)
        u.mem_map(0x3000000, 0x10000)
        blocks, events = set(), []

        def put(address, value):
            u.mem_write(address, struct.pack('<I', value & 0xffffffff))

        def get(address):
            return struct.unpack('<I', u.mem_read(address, 4))[0]

        def hook_block(_u, address, size, _d):
            if address < 0x500000:
                blocks.add((address, size))

        def service(uc, _address, _size, _data):
            desc = uc.reg_read(UC_X86_REG_EAX)
            events.append({'tick': get(0x46db3c), 'descriptor': hex(desc),
                           'volume': get(desc+8), 'period': get(desc+4),
                           'edx': uc.reg_read(UC_X86_REG_EDX),
                           'ebx': uc.reg_read(UC_X86_REG_EBX)})
            esp = uc.reg_read(UC_X86_REG_ESP)
            uc.reg_write(UC_X86_REG_EIP, get(esp))
            uc.reg_write(UC_X86_REG_ESP, esp+4)

        u.hook_add(UC_HOOK_BLOCK, hook_block)
        u.hook_add(UC_HOOK_CODE, service, begin=0x3002000, end=0x3002000)
        put(0x46dbe0, 0x3001000)
        put(0x300105c, 0x3002000)
        rows = []
        at = table
        while True:
            tick = struct.unpack_from('<I', image, at-0x400000)[0]
            if tick == 0xffff:
                break
            tick, descriptor, volume, period = struct.unpack_from('<4I', image, at-0x400000)
            assert 0x463ec4 <= descriptor <= 0x464104 and volume <= 64 and period > 0
            rows.append((tick, descriptor, volume, period))
            at += 16
            assert len(rows) <= 10
        for tick in range(max(row[0] for row in rows)+2):
            put(0x46db3c, tick)
            put(0x300f000, 0x300fff0)
            u.reg_write(UC_X86_REG_ESP, 0x300f000)
            u.reg_write(UC_X86_REG_EAX, table)
            u.emu_start(0x41c274, 0x300fff0, count=1000)
            assert u.reg_read(UC_X86_REG_EIP) == 0x300fff0
        assert [(e['tick'], int(e['descriptor'],16), e['volume'], e['period']) for e in events] == rows
        assert all(e['edx'] == 0xffffffff and e['ebx'] == 0x100 for e in events)
        for address, size in blocks:
            offset = pe.get_offset_from_rva(address-0x400000)
            assert image[address-0x400000:address-0x400000+size] == exe[offset:offset+size]
        results.append({'table':hex(table), 'events':events, 'executed_blocks':len(blocks)})
    # Interleave two tables to exercise the single shared cursor and reset.
    u = Uc(UC_ARCH_X86, UC_MODE_32)
    u.mem_map(0x400000, 0x100000)
    u.mem_write(0x400000, image)
    u.mem_map(0x3000000, 0x10000)
    interruptions = []
    def put_shared(address, value):
        u.mem_write(address, struct.pack('<I', value & 0xffffffff))
    def get_shared(address):
        return struct.unpack('<I', u.mem_read(address, 4))[0]
    def service_shared(uc, _address, _size, _data):
        desc = uc.reg_read(UC_X86_REG_EAX)
        interruptions.append({'tick':get_shared(0x46db3c), 'descriptor':hex(desc),
                              'period':get_shared(desc+4), 'volume':get_shared(desc+8)})
        esp = uc.reg_read(UC_X86_REG_ESP)
        uc.reg_write(UC_X86_REG_EIP, get_shared(esp))
        uc.reg_write(UC_X86_REG_ESP, esp+4)
    u.hook_add(UC_HOOK_CODE, service_shared, begin=0x3002000, end=0x3002000)
    put_shared(0x46dbe0, 0x3001000)
    put_shared(0x300105c, 0x3002000)
    for table, tick in ((0x464128,0),(0x464128,16),(0x46415c,0),
                        (0x464128,20),(0x46415c,24),(0x464128,0),
                        (0x464128,20),(0x464128,16)):
        put_shared(0x46db3c, tick)
        put_shared(0x300f000, 0x300fff0)
        u.reg_write(UC_X86_REG_ESP, 0x300f000)
        u.reg_write(UC_X86_REG_EAX, table)
        u.emu_start(0x41c274, 0x300fff0, count=1000)
        assert u.reg_read(UC_X86_REG_EIP) == 0x300fff0
    report = {'status':'VERIFIED_BOUNDED', 'scope':__doc__, 'exe_sha256':SHA,
              'consumer':'0x41c274', 'cases':results, 'interleaved_cursor_events':interruptions}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(f'PASS: {len(results)} original tables, {sum(len(c["events"]) for c in results)} dynamic sound events')


if __name__ == '__main__':
    main()
