#!/usr/bin/env python3
"""Compare original dynamic Mean Retail sound sequence PCM with native mixer.

Events come from bounded original table-consumer execution. Six-voice gain,
master level and event timing are adapted; actual gameplay reachability,
voice arbitration and final music/device mix are outside this comparison.
"""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

import pefile
from unicorn import Uc, UC_ARCH_X86, UC_HOOK_BLOCK, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_EDI
from unicorn.x86_const import UC_X86_REG_EIP, UC_X86_REG_ESI, UC_X86_REG_ESP
from verify_retail_tracker_pcm import EXE_SHA, GAME, TABLES

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    seq = args.output/'sequences.json'
    subprocess.run([sys.executable, str(ROOT/'tools/verify_mean_retail_sfx_sequences.py'),
                    '--output', str(seq)], check=True)
    events = json.loads(seq.read_text())
    exe = (GAME/'SLAMTILT.EXE').read_bytes()
    dat_path = GAME/'DAT/MEAN.DAT'
    dat = dat_path.read_bytes()
    assert digest(exe) == EXE_SHA and digest(dat) == TABLES['mean'][0]
    pe = pefile.PE(data=exe)
    image = pe.get_memory_mapped_image()
    u = Uc(UC_ARCH_X86, UC_MODE_32)
    u.mem_map(0x400000, 0x100000)
    u.mem_write(0x400000, image)
    u.mem_map(0x3000000, 0x60000)
    blocks = set()
    u.hook_add(UC_HOOK_BLOCK, lambda _u, addr, size, _d: blocks.add((addr, size)))

    def put(address, value):
        u.mem_write(address, struct.pack('<I', value & 0xffffffff))

    def run(address, eax=0, ebx=0, esi=0, edi=0):
        put(0x300f000, 0x305fff0)
        for reg, value in ((UC_X86_REG_ESP, 0x300f000), (UC_X86_REG_EAX, eax),
                           (UC_X86_REG_EBX, ebx), (UC_X86_REG_ESI, esi),
                           (UC_X86_REG_EDI, edi)):
            u.reg_write(reg, value)
        u.emu_start(address, 0x305fff0, count=2000000)
        assert u.reg_read(UC_X86_REG_EIP) == 0x305fff0

    put(0x46eeb8, 0x3010000)
    run(0x44b640, 0x20000 // 6)
    put(0x3002000, 0x3020000)
    for offset, value in ((0, 0x3010000), (4, 44100), (8, 65536)):
        put(0x3003000 + offset, value)
    cases = []
    for table in events['cases']:
        for event in table['events']:
            desc = int(event['descriptor'], 0)
            sid, _, _, length, displacement, _ = struct.unpack_from('<6I', image, desc-0x400000)
            assert sid > 0
            offset = struct.unpack_from('>I', dat, 4*(sid-1))[0] + 8 + displacement
            assert 0 <= offset <= len(dat)-length
            u.mem_write(0x3020000, dat[offset:offset+length])
            put(0x3002004, length)
            period, volume = event['period'], event['volume']
            for frames in (221, 2048):
                for off, val in ((0, 0x3002000), (4, 0), (8, 0), (12, volume << 10),
                                 (16, 0x361f0f // period), (20, 0)):
                    put(0x3001000 + off, val)
                u.mem_write(0x3030000, bytes(frames*2))
                run(0x44cc00, frames, 0x3030000, 0x3001000, 0x3003000)
                original = bytes(u.mem_read(0x3030000, frames*2))
                native = subprocess.check_output([str(args.native.resolve()), str(dat_path),
                    str(offset), str(length), str(period), str(volume), str(frames)])
                assert native == original, (table['table'], event, frames)
                cases.append({'table':table['table'], 'tick':event['tick'],
                              'descriptor':event['descriptor'], 'offset':hex(offset),
                              'period':period, 'volume':volume, 'frames':frames,
                              'pcm_sha256':digest(original)})
    # Cover every supported amplitude, including values absent from the six
    # observed tables; the same real DAT slice is used with synthetic controls.
    event = events['cases'][0]['events'][0]
    desc = int(event['descriptor'], 0)
    sid, _, _, length, displacement, _ = struct.unpack_from('<6I', image, desc-0x400000)
    offset = struct.unpack_from('>I', dat, 4*(sid-1))[0] + 8 + displacement
    u.mem_write(0x3020000, dat[offset:offset+length])
    put(0x3002004, length)
    for volume in range(65):
        for off, val in ((0, 0x3002000), (4, 0), (8, 0), (12, volume << 10),
                         (16, 0x361f0f // 226), (20, 0)):
            put(0x3001000 + off, val)
        u.mem_write(0x3030000, bytes(442))
        run(0x44cc00, 221, 0x3030000, 0x3001000, 0x3003000)
        native = subprocess.check_output([str(args.native.resolve()), str(dat_path),
                    str(offset), str(length), '226', str(volume), '221'])
        assert native == bytes(u.mem_read(0x3030000, 442)), volume
    for address, size in blocks:
        off = pe.get_offset_from_rva(address-0x400000)
        assert bytes(u.mem_read(address,size)) == exe[off:off+size]
    report = {'status':'VERIFIED_BOUNDED', 'scope':__doc__, 'exe_sha256':EXE_SHA,
              'dat_sha256':digest(dat), 'native_sha256':digest(args.native.read_bytes()),
              'cases':cases, 'synthetic_volume_sweep':{'min':0, 'max':64,
                  'frames_per_volume':221}, 'executed_original_blocks':len(blocks)}
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: {len(cases)} original/native dynamic PCM cases, plus 65 volume levels')


if __name__ == '__main__':
    main()
