#!/usr/bin/env python3
"""Execute the Retail six-voice game mixer on synthetic tracker/SFX voices.

This verifies the shared mixer call with 16-bit stereo output and six-voice,
full-volume settings, not a particular sound device or a natural gameplay trace.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

import pefile
from unicorn import Uc, UC_ARCH_X86, UC_HOOK_BLOCK, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EDX, UC_X86_REG_EIP, UC_X86_REG_ESP

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE'
SHA = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
FRAMES = 221


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, default=EXE)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    binary = args.exe.read_bytes()
    assert hashlib.sha256(binary).hexdigest() == SHA, 'unsupported original'
    image = pefile.PE(data=binary).get_memory_mapped_image()
    results = []
    for voices in (1, 4, 6):
        u = Uc(UC_ARCH_X86, UC_MODE_32)
        u.mem_map(0x400000, 0x100000)
        u.mem_write(0x400000, image)
        u.mem_map(0x3000000, 0x60000)
        blocks = set()
        u.hook_add(UC_HOOK_BLOCK, lambda _u, a, n, _d: blocks.add((a, n)))

        def put(address, value):
            u.mem_write(address, struct.pack('<I', value & 0xffffffff))

        def run(address, eax, edx=0):
            put(0x3050000, 0x305fff0)
            for reg, value in ((UC_X86_REG_ESP, 0x3050000),
                               (UC_X86_REG_EAX, eax), (UC_X86_REG_EDX, edx)):
                u.reg_write(reg, value)
            u.emu_start(address, 0x305fff0, count=1000000)
            assert u.reg_read(UC_X86_REG_EIP) == 0x305fff0

        put(0x46eeb8, 0x3010000)
        run(0x44b640, 0x20000 // 6)
        for address, value in ((0x46eeac, 0), (0x46eec4, 0), (0x46ee90, 0),
                               (0x46eea4, 6), (0x46ee98, FRAMES),
                               (0x46ee88, 44100 * 256 // FRAMES),
                               (0x46eeb0, 0x3030000), (0x46eeb4, 0x3031000),
                               (0x46eec8, 0x3032000), (0x46eea8, 16),
                               (0x46eecc, 1), (0x46ee9c, 1), (0x46eebc, 44100)):
            put(address, value)
        container, output = 0x3000000, 0x3003000
        put(container, 0x3004000)
        put(container + 0x2808, 65536)
        put(container + 0x2804, 250)
        put(output, 0x3033000)
        put(output + 8, FRAMES)
        samples = []
        for i in range(voices):
            voice, header, pcm = 0x3004000 + i * 0x40, 0x3005000 + i * 0x80, 0x3009000 + i * 0x1000
            frequency = 8363 + i * 500
            values = (header, 0, 0, 65536, frequency, 0, 0, 0,
                      voice + 0x40 if i + 1 < voices else 0)
            for offset, value in enumerate(values):
                put(voice + 4 * offset, value)
            put(header, pcm)
            put(header + 4, 512)
            sample = bytes((j * 3 + i * 17) % 256 for j in range(512))
            samples.append((sample, frequency))
            u.mem_write(pcm, sample)
        run(0x44b560, output, container)
        result = struct.unpack(f'<{FRAMES * 2}h', u.mem_read(0x3033000, FRAMES * 4))
        expected = []
        for frame in range(FRAMES):
            value = 0
            for sample, frequency in samples:
                step = ((frequency << 32) // 44100) & ~15
                index = (step * frame) >> 32
                raw = sample[index]
                signed = raw if raw < 128 else raw - 256
                value += signed * (0x20000 // 6) * 127 // 65536
            expected.append(((value + 32768) & 0xffff) - 32768)
        assert list(result[::2]) == expected
        assert list(result[1::2]) == expected
        assert any(expected) and len(set(expected)) > 10
        for address, size in blocks:
            assert 0x401000 <= address and address + size <= 0x454000
            off = address - 0x401000 + 0x400
            assert bytes(u.mem_read(address, size)) == binary[off:off + size]
        results.append({'voices': voices, 'frames': FRAMES, 'left_equals_right': True,
                        'nearest_sample_matches': True, 'executed_original_blocks': len(blocks),
                        'mono_sha256': hashlib.sha256(struct.pack(f'<{FRAMES}h', *expected)).hexdigest()})
    report = {'status': 'VERIFIED_BOUNDED', 'scope': __doc__, 'executable_sha256': SHA,
              'entry': '0x44b560', 'voice_mix': '0x44c918', 'sample_loop': '0x44cd4d',
              'final_mix': '0x44b8bc', 'factory_gain_factor': 0x20000 // 6,
              'sample_rate': 44100, 'cases': results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: original game mixer outputs identical channels and nearest samples in 1/4/6-voice cases')


if __name__ == '__main__':
    main()
