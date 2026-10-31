#!/usr/bin/env python3
"""Compare a bounded final-mixer mode against the actual native gain helper.

Inputs are synthetic signed samples, not captured music or sound effects. The
test proves arithmetic for the selected Retail device format and highlights an
overflow difference; it does not establish original/native tracker gain parity,
real-world clipping frequency, device timing, or audible game equivalence.
"""
import argparse
import hashlib
import json
import random
import struct
import subprocess
from pathlib import Path

import pefile
from unicorn import Uc, UC_ARCH_X86, UC_HOOK_BLOCK, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_EDX
from unicorn.x86_const import UC_X86_REG_EIP, UC_X86_REG_ESP

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE'
SHA = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
SEED = 0x5A4D


def digest(data):
    return hashlib.sha256(data).hexdigest()


def original_mix(executable, rows):
    assert digest(executable) == SHA, 'unsupported Retail executable'
    image = pefile.PE(data=executable).get_memory_mapped_image()
    u = Uc(UC_ARCH_X86, UC_MODE_32)
    u.mem_map(0x400000, 0x100000)
    u.mem_write(0x400000, image)
    u.mem_map(0x3000000, 0x30000)
    blocks = set()
    u.hook_add(UC_HOOK_BLOCK, lambda _u, addr, size, _d: blocks.add((addr, size)))

    def put(address, value):
        u.mem_write(address, struct.pack('<I', value))

    mono, left, right, output = 0x3001000, 0x3004000, 0x3007000, 0x300a000
    for address, values in ((mono, [x[0] for x in rows]),
                            (left, [x[1] for x in rows]),
                            (right, [x[2] for x in rows])):
        u.mem_write(address, struct.pack(f'<{len(values)}h', *values))
    # Original signed 16-bit stereo selector, with all three input buffers.
    for address, value in ((0x46eea8, 16), (0x46eecc, 1), (0x46ee9c, 1),
                           (0x46eeb0, mono), (0x46eeb4, left), (0x46eec8, right),
                           (0x46eec4, 0), (0x46eeac, 0), (0x46ee90, 0)):
        put(address, value)
    stop = 0x302fff0
    put(0x3020000, stop)
    for register, value in ((UC_X86_REG_ESP, 0x3020000), (UC_X86_REG_EAX, output),
                            (UC_X86_REG_EDX, len(rows)), (UC_X86_REG_EBX, 0)):
        u.reg_write(register, value)
    u.emu_start(0x44b8bc, stop, count=1000000)
    assert u.reg_read(UC_X86_REG_EIP) == stop, 'original did not return'
    # Check each executed block against the authenticated PE text on disk.
    for address, size in blocks:
        assert 0x401000 <= address and address + size <= 0x454000
        offset = address - 0x401000 + 0x400
        assert bytes(u.mem_read(address, size)) == executable[offset:offset + size]
    raw = u.mem_read(output, len(rows) * 4)
    values = struct.unpack(f'<{len(rows) * 2}h', raw)
    return list(zip(values[::2], values[1::2])), len(blocks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, default=EXE)
    parser.add_argument('--native', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cases = [(0, 0, 0), (1000, 2000, -2000),
             (10000, 30000, 1000), (-10000, -30000, -1000),
             (32767, 0, 1), (-32768, 0, -1),
             (32767, 32767, -32768), (-32768, -32768, 32767)]
    rng = random.Random(SEED)
    rows = cases + [tuple(rng.randint(-32768, 32767) for _ in range(3))
                    for _ in range(1024)]
    original, blocks = original_mix(args.exe.read_bytes(), rows)
    stdin = ''.join(f'{m} {l} {r}\n' for m, l, r in rows)
    result = subprocess.run([str(args.native.resolve())], input=stdin, text=True,
                            capture_output=True, check=True)
    native = [tuple(map(int, line.split())) for line in result.stdout.splitlines()]
    assert len(native) == len(rows) and all(len(row) == 2 for row in native)
    wrap = lambda x: ((x + 32768) & 0xffff) - 32768
    clamp = lambda x: min(32767, max(-32768, x))
    overflow = 0
    for (mono, left, right), orig, actual in zip(rows, original, native):
        sums = (mono + left, mono + right)
        assert orig == tuple(map(wrap, sums))
        assert actual == tuple(map(clamp, sums))
        for value, old, new in zip(sums, orig, actual):
            out_of_range = value < -32768 or value > 32767
            assert (old != new) == out_of_range
            overflow += out_of_range
    assert 0 < overflow < len(rows) * 2
    factor = 0x20000 // 6
    one_min = (-128 * factor * 127) // 65536
    one_max = (127 * factor * 127) // 65536
    # Exercise the production default SFX path with every signed 8-bit value,
    # both ordinary and edge music inputs. The original gets the corresponding
    # mono values; this is still synthetic, not tracker PCM or a gameplay trace.
    voice_rows = [(sample, music, -music if music != -32768 else 32767)
                  for sample in range(-128, 128) for music in (0, 30000, -32768)]
    voice_sums = [(sample * factor * 127 // 65536, left, right)
                  for sample, left, right in voice_rows]
    voice_original, voice_blocks = original_mix(args.exe.read_bytes(), voice_sums)
    voice_input = ''.join(f'{sample} {left} {right}\n' for sample, left, right in voice_rows)
    voice_run = subprocess.run([str(args.native.resolve()), '--voice'], input=voice_input,
                               text=True, capture_output=True, check=True)
    voice_native = [tuple(map(int, line.split())) for line in voice_run.stdout.splitlines()]
    assert len(voice_native) == len(voice_sums)
    voice_overflow = 0
    for (mono, left, right), orig, actual in zip(voice_sums, voice_original, voice_native):
        sums = (mono + left, mono + right)
        assert orig == tuple(map(wrap, sums)) and actual == tuple(map(clamp, sums))
        voice_overflow += sum(not -32768 <= value <= 32767 for value in sums)
    assert voice_overflow > 0
    report = {'status': 'VERIFIED_BOUNDED_WITH_SYNTHETIC_OVERFLOW_GAP',
              'scope': __doc__, 'executable_sha256': SHA,
              'native_probe_sha256': digest(args.native.read_bytes()),
              'original_entry': '0x44b8bc', 'original_selected_branch': '0x44bca9',
              'format': 'signed 16-bit stereo; mono, left and right buffers enabled',
              'seed': SEED, 'frames': len(rows), 'executed_original_blocks': blocks,
              'matching_channels': len(rows) * 2 - overflow,
              'synthetic_overflow_channels': overflow,
              'production_sfx_path': {'frames': len(voice_rows),
                  'all_signed_8_bit_values_tested': True,
                  'synthetic_overflow_channels': voice_overflow,
                  'executed_original_blocks': voice_blocks,
                  'scope': 'one synthetic PCM voice plus synthetic stereo music; '
                           'no original tracker scaling or gameplay capture'},
              'factory_six_voice_math': {'gain_factor': factor,
                  'single_sample_min': one_min, 'single_sample_max': one_max,
                  'six_voice_sum_min': 6 * one_min, 'six_voice_sum_max': 6 * one_max,
                  'scope': 'signed 8-bit full volume sample terms; excludes tracker input'},
              'examples': [{'mono': row[0], 'left': row[1], 'right': row[2],
                            'original': list(old), 'native': list(new)}
                           for row, old, new in zip(rows[:len(cases)], original, native)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: {len(rows)} gain-helper frames and {len(voice_rows)} production SFX '
          f'frames; synthetic overflows differ as expected')


if __name__ == '__main__':
    main()
