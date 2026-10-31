#!/usr/bin/env python3
"""Execute the Retail sample resampler through repeated synthetic loop edges.

The test covers a single synthetic 8-bit voice, explicit fixed gain and sample
rate, and bounded forward loops. It does not prove tracker events, device
cadence, reverse loops, libxmp behavior or natural gameplay timing.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

import pefile
from unicorn import Uc, UC_ARCH_X86, UC_HOOK_BLOCK, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_EDI
from unicorn.x86_const import UC_X86_REG_EIP, UC_X86_REG_ESI, UC_X86_REG_ESP

from verify_retail_tracker_pcm import EXE_SHA, GAME


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--exe', type=Path, default=GAME / 'SLAMTILT.EXE')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    exe = a.exe.read_bytes()
    assert hashlib.sha256(exe).hexdigest() == EXE_SHA
    image = pefile.PE(data=exe).get_memory_mapped_image()
    cases = []
    for start, length, freq in ((0, 3, 8287), (7, 13, 16574),
                                (9, 31, 18668), (3, 5, 44000)):
        expected = None
        for chunk in (1, 137, 4096):
            u = Uc(UC_ARCH_X86, UC_MODE_32)
            u.mem_map(0x400000, 0x100000)
            u.mem_write(0x400000, image)
            u.mem_map(0x3000000, 0x60000)
            blocks = set()
            u.hook_add(UC_HOOK_BLOCK, lambda _u, address, size, _d: blocks.add((address, size)))

            def put(address, value):
                u.mem_write(address, struct.pack('<I', value & 0xffffffff))

            def run(address, eax, ebx=0, esi=0, edi=0):
                put(0x300f000, 0x305fff0)
                for reg, value in ((UC_X86_REG_ESP, 0x300f000), (UC_X86_REG_EAX, eax),
                                   (UC_X86_REG_EBX, ebx), (UC_X86_REG_ESI, esi),
                                   (UC_X86_REG_EDI, edi)):
                    u.reg_write(reg, value)
                u.emu_start(address, 0x305fff0, count=2000000)
                assert u.reg_read(UC_X86_REG_EIP) == 0x305fff0

            put(0x46eeb8, 0x3010000)
            run(0x44b640, 0x20000 // 6)
            pcm = bytes((i * 37 + 11) % 256 for i in range(64))
            u.mem_write(0x3020000, pcm)
            for off, value in ((0, 0x3020000), (4, 64), (8, start), (12, length)):
                put(0x3002000 + off, value)
            for off, value in ((0, 0x3002000), (4, 0), (8, 0), (12, 65536),
                               (16, freq), (20, 0xffffffff)):
                put(0x3001000 + off, value)
            for off, value in ((0, 0x3010000), (4, 44100), (8, 65536)):
                put(0x3003000 + off, value)
            frames = 4096
            u.mem_write(0x3030000, bytes(frames * 2))
            for i in range(0, frames, chunk):
                run(0x44cc00, min(chunk, frames - i), 0x3030000 + 2 * i,
                    0x3001000, 0x3003000)
            actual = struct.unpack(f'<{frames}h', u.mem_read(0x3030000, frames * 2))
            step = ((freq << 32) // 44100) & ~15
            model = []
            for i in range(frames):
                index = (i * step) >> 32
                if index >= start + length:
                    index = start + (index - start) % length
                value = pcm[index] if pcm[index] < 128 else pcm[index] - 256
                model.append(value * (0x20000 // 6) * 127 // 65536)
            assert list(actual) == model, (start, length, freq, chunk)
            if expected is not None:
                assert actual == expected
            expected = actual
            for address, size in blocks:
                assert 0x401000 <= address and address + size <= 0x454000
                off = address - 0x401000 + 0x400
                assert bytes(u.mem_read(address, size)) == exe[off:off + size]
        cases.append({'loop_start': start, 'loop_length': length, 'frequency': freq,
                      'frames': frames, 'chunks': [1, 137, 4096],
                      'pcm_sha256': hashlib.sha256(struct.pack(f'<{frames}h', *expected)).hexdigest()})
    report = {'status': 'VERIFIED_BOUNDED', 'scope': __doc__, 'exe_sha256': EXE_SHA,
              'entry': '0x44cc00', 'rate': 44100, 'cases': cases}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: four original forward-loop cases; 12 chunkings, 4096 frames each')


if __name__ == '__main__':
    main()
