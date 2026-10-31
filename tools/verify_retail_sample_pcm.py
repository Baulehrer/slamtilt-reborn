#!/usr/bin/env python3
"""Compare bounded Pirate/Space/Demon SFX directly against the Windows Retail x86 mixer.

Runs the Retail gain-LUT initializer 44b640 and mono one-shot resampler 44cc00
inside Unicorn. These samples use the explicit six-voice/full-volume convention;
this does not test tracker music, overlapping voices, the final stereo device mix,
original event timing or undocumented live mixer settings. Original media stays
outside the output: only build/context hashes and PCM hashes are retained.
"""
import argparse
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_BLOCK
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_EDI
from unicorn.x86_const import UC_X86_REG_EIP, UC_X86_REG_ESI, UC_X86_REG_ESP

ROOT = Path(__file__).resolve().parents[1]
BUILD_SHA = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
EXE = ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def original_cases(table, exe_path):
    context = ROOT / ('build/oracle/pirate-full-tick' if table == 'pirate' else f'build/oracle/{table}-full-game')
    summary = json.loads((context / 'summary.json').read_text())
    info_path = {'pirate': 'analysis/pirate-audio-static.json',
                 'space': 'analysis/space-audio-reuse.json',
                 'demon': 'analysis/demon-audio-profile.json'}[table]
    info = json.loads((ROOT / info_path).read_text())
    executable = exe_path.read_bytes()
    assert digest(executable) == BUILD_SHA
    image = (context / 'human-image.bin').read_bytes()
    dat = (context / 'human-dat.bin').read_bytes()
    assert summary['build_sha256'] == BUILD_SHA
    expected_image = (info['artifact']['image_sha256'] if table == 'pirate' else
                      info['image']['sha256'] if table == 'space' else info['canonical_context_sha256'])
    assert digest(image) == summary['context_hashes']['human-image.bin'] == expected_image
    expected_dat = info['artifact']['dat_sha256'] if table == 'pirate' else info['dat']['sha256']
    assert digest(dat) == summary['dat_sha256'] == expected_dat
    profiles = ([{'descriptor': p['address'], 'offset': p['pcm_offset'], 'length': p['length'],
                  'period': p['period'], 'pcm_sha256': p['pcm_sha256']}
                 for p in info['sfx_descriptors']] if table == 'pirate' else info['sample_profiles'])
    assert len({p['descriptor'] for p in profiles}) == len(profiles)
    u = Uc(UC_ARCH_X86, UC_MODE_32)
    u.mem_map(0x400000, 0x100000)
    u.mem_write(0x400000, image)
    u.mem_map(0x3000000, 0x60000)
    executed_blocks = set()
    def remember_block(_uc, address, size, _user):
        executed_blocks.add((address, size))
    u.hook_add(UC_HOOK_BLOCK, remember_block)

    def put(address, value):
        u.mem_write(address, struct.pack('<I', value & 0xffffffff))

    def run(address, eax=0, ebx=0, esi=0, edi=0):
        put(0x300f000, 0x305fff0)
        u.reg_write(UC_X86_REG_ESP, 0x300f000)
        for reg, value in [(UC_X86_REG_EAX, eax), (UC_X86_REG_EBX, ebx),
                           (UC_X86_REG_ESI, esi), (UC_X86_REG_EDI, edi)]:
            u.reg_write(reg, value)
        u.emu_start(address, 0x305fff0, count=2000000)
        assert u.reg_read(UC_X86_REG_EIP) == 0x305fff0, hex(address)

    put(0x46eeb8, 0x3010000)
    run(0x44b640, 0x20000 // 6)
    put(0x3002000, 0x3020000)
    put(0x3003000, 0x3010000)
    put(0x3003004, 44100)
    put(0x3003008, 65536)
    cases = []
    lazy_pointers = []
    for profile in profiles:
        descriptor, offset = int(profile['descriptor'], 0), int(profile['offset'], 0)
        length, period = profile['length'], profile['period']
        address = descriptor - 0x400000
        assert 0 <= address and address + 36 <= len(image)
        words = struct.unpack_from('<9I', image, address)
        assert (words[1], words[2], words[3]) == (period, 64, length), hex(descriptor)
        if words[5] == 0:
            # Some bank/shared-ID data pointers are resolved only on use.
            # Their eventual mapping is grounded in the existing profile evidence.
            lazy_pointers.append(hex(descriptor))
        else:
            assert words[5] == 0x1100000 + offset, hex(descriptor)
        assert period > 0 and 0 <= offset and offset + length <= len(dat)
        sample = dat[offset:offset + length]
        assert digest(sample) == profile['pcm_sha256'], hex(descriptor)
        u.mem_write(0x3020000, sample)
        for frames in (1, 221, 2048, 30000):
            put(0x3002004, length)
            frequency = 0x361f0f // period
            for off, value in [(0, 0x3002000), (4, 0), (8, 0), (12, 65536),
                               (16, frequency), (20, 0)]:
                put(0x3001000 + off, value)
            u.mem_write(0x3030000, bytes(frames * 2))
            run(0x44cc00, frames, 0x3030000, 0x3001000, 0x3003000)
            original = bytes(u.mem_read(0x3030000, frames * 2))
            cases.append({'descriptor': descriptor, 'offset': offset, 'length': length,
                          'period': period, 'frames': frames, 'mono_sha256': digest(original)})
    # PE BEGTEXT maps original VA 0x401000 to file offset 0x400. Verify every
    # actually executed basic block against the SHA-pinned Retail executable.
    for address, size in executed_blocks:
        assert 0x401000 <= address and address + size <= 0x454000, hex(address)
        in_image = image[address - 0x400000:address - 0x400000 + size]
        in_exe = executable[address - 0x401000 + 0x400:address - 0x401000 + 0x400 + size]
        assert len(in_exe) == size and in_image == in_exe, hex(address)
        assert bytes(u.mem_read(address, size)) == in_exe, hex(address)
    return {'table': table, 'build_sha256': BUILD_SHA, 'dat_sha256': digest(dat),
            'image_sha256': digest(image), 'executed_original_blocks': len(executed_blocks),
            'profile_count': len(profiles),
            'lazy_descriptor_pointers': lazy_pointers, 'cases': cases}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, default=ROOT/'build/native/retail_sample_pcm_probe')
    p.add_argument('--exe', type=Path, default=EXE, help='SHA-pinned Windows Retail EXE (test only)')
    p.add_argument('--output', type=Path, default=ROOT/'build/retail-sample-pcm')
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rows = []
    for table in ('pirate', 'space', 'demon'):
        fixture = original_cases(table, args.exe)
        output = args.output / f'{table}.json'
        output.write_text(json.dumps(fixture, indent=2) + '\n')
        dat = ROOT / ('build/oracle/pirate-full-tick/human-dat.bin' if table == 'pirate'
                      else f'build/oracle/{table}-full-game/human-dat.bin')
        subprocess.run([str(args.native.resolve()), table, str(dat), str(output)], check=True)
        rows.append({'table': table, 'cases': len(fixture['cases']),
                     'descriptors': fixture['profile_count'], 'fixture_sha256': digest(output.read_bytes()),
                     'image_sha256': fixture['image_sha256'], 'dat_sha256': fixture['dat_sha256'],
                     'executed_original_blocks': fixture['executed_original_blocks'],
                     'lazy_descriptor_pointers': fixture['lazy_descriptor_pointers']})
    (args.output / 'report.json').write_text(json.dumps({'status': 'PASS', 'build_sha256': BUILD_SHA,
        'scope': __doc__, 'native_sha256': digest(args.native.read_bytes()), 'tables': rows}, indent=2) + '\n')


if __name__ == '__main__':
    main()
