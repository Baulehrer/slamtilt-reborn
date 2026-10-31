#!/usr/bin/env python3
"""Compare every native Mean sample to the Demo's actual resampler.

Original descriptors, period and length are checked against the pinned Demo
image; PCM offsets are the existing adapter's bindings, supplied explicitly.
This does not prove all Retail-only descriptors or event reachability.
"""
import argparse
import hashlib
import json
import struct
import subprocess
from pathlib import Path

import pefile
from unicorn import Uc, UC_ARCH_X86, UC_HOOK_BLOCK, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_EDI
from unicorn.x86_const import UC_X86_REG_EIP, UC_X86_REG_ESI, UC_X86_REG_ESP

ROOT = Path(__file__).resolve().parents[1]
DEMO_SHA = '31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00'
DAT_SHA = '1169210c52fb4cb8785a0ef87e42bcabbc9d7b17bf9b9062f4642fb2cb69755f'
IMAGE_SHA = '8ec7d39b5b56cee1d929536d71446743604fb0ae8fcf260f9be6a3fde81e96d1'
PROFILES = [(0x437cf0,0x63a1d,6465,160),(0x437d14,0x6535e,4078,226),
            (0x437da4,0x6aaa4,3026,226),(0x437d38,0x6634c,4490,226),
            (0x437d5c,0x674d6,4012,226),(0x437dec,0x6d40e,5808,226),
            (0x437dc8,0x6b676,7576,226),(0x437fe4,0x27b66,2747,428),
            (0x438008,0x286ea,2882,428),(0x43802c,0x292f5,3395,428),
            (0x438050,0x2a100,4536,428),
            (0x437e10,0x38ef0,8948,226),(0x437e34,0x337f0,4006,226),
            (0x437e58,0x4e072,23600,226),(0x437e7c,0x47aea,12388,226),
            (0x437ea0,0x84,200,226),(0x437ec4,0x45c0c,7894,226),
            (0x437ee8,0x43c40,16034,226),(0x437f0c,0x1a5a8,21680,226),
            (0x437f30,0x3e484,14000,226),(0x437f54,0x1f958,2400,226),
            (0x437f78,0x8b52,7200,226),(0x437f9c,0x107d8,4264,226),
            (0x437fc0,0x4bfdc,8334,226)]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    builds = json.loads((ROOT/'analysis/windows-symbol-map.json').read_text())['builds']
    exe = (ROOT / next(x['path'] for x in builds if x['sha256'] == DEMO_SHA)).read_bytes()
    dat = (ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/MEAN.DAT').read_bytes()
    image = (ROOT/'build/mean-prepared/pe-data.bin').read_bytes()
    assert (sha(exe), sha(dat), sha(image)) == (DEMO_SHA, DAT_SHA, IMAGE_SHA)
    pe = pefile.PE(data=exe)
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

    put(0x43f418, 0x3010000)
    run(0x41eb60, 0x20000 // 6)
    put(0x3002000, 0x3020000)
    for offset, value in ((0, 0x3010000), (4, 44100), (8, 65536)):
        put(0x3003000 + offset, value)
    cases = []
    for descriptor, offset, length, period in PROFILES:
        words = struct.unpack_from('<9I', image, descriptor - 0x400000)
        assert (words[1], words[2], words[3]) == (period, 64, length)
        if words[0]:
            resolved = struct.unpack_from('>I', dat, (words[0]-1)*4)[0] + 8 + words[4]
            assert resolved == offset, hex(descriptor)
        assert 0 <= offset and offset + length <= len(dat)
        u.mem_write(0x3020000, dat[offset:offset + length])
        for frames in (1, 221, 2048, 30000):
            put(0x3002004, length)
            for off, value in ((0, 0x3002000), (4, 0), (8, 0), (12, 65536),
                               (16, 0x361f0f // period), (20, 0)):
                put(0x3001000 + off, value)
            u.mem_write(0x3030000, bytes(frames * 2))
            run(0x420120, frames, 0x3030000, 0x3001000, 0x3003000)
            pcm = bytes(u.mem_read(0x3030000, frames * 2))
            cases.append({'descriptor': descriptor, 'offset': offset, 'length': length,
                          'period': period, 'frames': frames, 'mono_sha256': sha(pcm)})
    for address, size in blocks:
        offset = pe.get_offset_from_rva(address - 0x400000)
        assert bytes(u.mem_read(address, size)) == exe[offset:offset + size]
    report = {'table': 'mean', 'dat_sha256': DAT_SHA, 'build_sha256': DEMO_SHA,
              'image_sha256': IMAGE_SHA, 'profile_count': len(PROFILES), 'cases': cases,
              'scope': __doc__, 'executed_original_blocks': len(blocks)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    dat_path = ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/MEAN.DAT'
    subprocess.run([str(args.native.resolve()), 'mean', str(dat_path), str(args.output)], check=True)
    print(f'PASS: {len(PROFILES)} Mean descriptors, {len(cases)} original/native PCM cases')


if __name__ == '__main__':
    main()
