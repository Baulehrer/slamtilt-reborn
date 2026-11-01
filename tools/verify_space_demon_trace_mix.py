#!/usr/bin/env python3
"""Compare two trace-derived Space/Demon SFX+music combinations against Retail.

Both requests come from retained diagnostic gameplay traces. Playback is an
isolated reconstruction: the SFX begins 882 frames before a fresh tracker,
and earlier voices are absent. This assumes a cadence and does not establish
actual gameplay timing, full-mix equivalence, or physical audio output.
Original media and PCM are written only to --work, never to --output.
"""
import argparse
import hashlib
import json
import os
import struct
import subprocess
import sys
from pathlib import Path

import pefile
from unicorn import Uc, UC_ARCH_X86, UC_HOOK_BLOCK, UC_MODE_32
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_EDI,
                               UC_X86_REG_EIP, UC_X86_REG_ESI, UC_X86_REG_ESP)
from extract_mean_stim import extract
from verify_retail_final_mix import original_mix
from verify_retail_tracker_pcm import EXE_SHA, GAME, ROOT, TABLES

CASES = [
    ('space', 'space-mission-campaign-rewards.json', 4632, 0x465dbc, 0x658cd, 5808, 0x5b8e0, 0, 'analysis/space-audio-reuse.json', '7ca06b0a74520784ddc5f17509344cbcb9ef9718ee45d28454ab9ac1a820407d'),
    ('demon', 'demon-kickback-on-rewards.json', 2004, 0x4633bc, 0x8333c, 6330, 0x6e2ce, 13, 'analysis/demon-audio-profile.json', 'f6578a49bbfd29d8c61aacb5173aac010ca1bd1af33333f743687f9eb7763506'),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def original_sfx(executable, pe, image, data, offset, length):
    u = Uc(UC_ARCH_X86, UC_MODE_32)
    u.mem_map(0x400000, 0x100000)
    u.mem_write(0x400000, image)
    u.mem_map(0x3000000, 0x90000)
    blocks = set()
    u.hook_add(UC_HOOK_BLOCK, lambda _u, addr, size, _d: blocks.add((addr, size)))

    def put(addr, value):
        u.mem_write(addr, struct.pack('<I', value & 0xffffffff))

    def run(addr, eax=0, ebx=0, esi=0, edi=0):
        put(0x300f000, 0x308fff0)
        for reg, value in ((UC_X86_REG_ESP, 0x300f000), (UC_X86_REG_EAX, eax),
                           (UC_X86_REG_EBX, ebx), (UC_X86_REG_ESI, esi), (UC_X86_REG_EDI, edi)):
            u.reg_write(reg, value)
        u.emu_start(addr, 0x308fff0, count=2000000)
        if u.reg_read(UC_X86_REG_EIP) != 0x308fff0:
            raise RuntimeError(f'Original routine {addr:#x} did not return')

    put(0x46eeb8, 0x3010000)
    run(0x44b640, 0x20000 // 6)
    for delta, value in ((0, 0x3010000), (4, 44100), (8, 65536)):
        put(0x3003000 + delta, value)
    u.mem_write(0x3040000, data[offset:offset + length])
    put(0x3002000, 0x3040000)
    put(0x3002004, length)
    for delta, value in ((0, 0x3002000), (4, 0), (8, 0), (12, 64 << 10),
                         (16, 0x361f0f // 226), (20, 0)):
        put(0x3001000 + delta, value)
    frames = 882 + 2646
    u.mem_write(0x3030000, bytes(frames * 2))
    run(0x44cc00, frames, 0x3030000, 0x3001000, 0x3003000)
    pcm = struct.unpack(f'<{frames}h', u.mem_read(0x3030000, frames * 2))[882:]
    for addr, size in blocks:
        source = pe.get_offset_from_rva(addr - 0x400000)
        if bytes(u.mem_read(addr, size)) != executable[source:source + size]:
            raise RuntimeError(f'Original instruction mismatch at {addr:#x}')
    return pcm, len(blocks)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--library', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    native, library = args.native.resolve(), args.library.absolute()
    env = dict(os.environ, LD_LIBRARY_PATH=str(library.parent))
    if str(library) not in subprocess.check_output(['ldd', str(native)], env=env, text=True):
        raise RuntimeError(f'{native} did not link to expected {library}')
    native_sha, lib_sha = sha(native.read_bytes()), sha(library.read_bytes())
    exe = (GAME / 'SLAMTILT.EXE').read_bytes()
    if sha(exe) != EXE_SHA:
        raise RuntimeError('Unrecognized Windows Retail executable SHA')
    pe = pefile.PE(data=exe)
    image = pe.get_memory_mapped_image()
    rows = []
    for table, fixture, tick, desc, offset, length, bank, order, profile_path, sample_sha in CASES:
        fixture_path = ROOT / 'analysis/traces' / fixture
        trace_data = fixture_path.read_bytes()
        trace = json.loads(trace_data)
        if (trace.get('build_sha256') != EXE_SHA or
                trace.get('dat_sha256') != TABLES[table][0] or
                not trace.get('original_reset_exact')):
            raise RuntimeError(f'{table}: trace is not pinned to the expected original build and data')
        events = trace['audio_events']
        sfx = next((e for e in events if e[0] == tick and e[1] == 0x5c and e[4] == desc), None)
        music = next((e for e in events if e[0] == tick + 1 and e[1] in (0x84, 0x88) and e[3] == order), None)
        if sfx is None or music is None or music[2] != (1 if table == 'space' else 2):
            raise RuntimeError(f'{table}: expected event pair absent from {fixture_path}')
        dat_path = GAME / 'DAT' / f'{table.upper()}.DAT'
        dat = dat_path.read_bytes()
        if sha(dat) != TABLES[table][0]:
            raise RuntimeError(f'{table}: unsupported DAT SHA')
        profile_data = (ROOT / profile_path).read_bytes()
        profiles = json.loads(profile_data)['sample_profiles']
        profile = next((p for p in profiles if int(p['descriptor'], 0) == desc), None)
        if (profile is None or int(profile['offset'], 0) != offset or profile['length'] != length or
                profile['period'] != 226 or profile['pcm_sha256'] != sample_sha or
                sha(dat[offset:offset + length]) != sample_sha):
            raise RuntimeError(f'{table}: original sample profile or PCM SHA mismatch')
        descriptor = struct.unpack_from('<4I', image, desc - 0x400000)
        if descriptor[1:] != (226, 64, length) or offset + length > len(dat):
            raise RuntimeError(f'{table}: original SFX descriptor disagrees with selected sample')
        work = args.work / table
        work.mkdir(exist_ok=True, parents=True)
        subprocess.run([sys.executable, str(ROOT / 'tools/verify_retail_tracker_pcm.py'),
                        '--table', table, '--bank-offset', hex(bank), '--order', str(order),
                        '--ticks', '3', '--dynamic-voices', '--allow-silent', '--output', str(work)],
                       check=True, stdout=subprocess.DEVNULL)
        music_pcm = struct.unpack('<5292h', (work / f'{table}-first-tick.s16le').read_bytes())
        if music_pcm[::2] != music_pcm[1::2]:
            raise RuntimeError(f'{table}: original music is not expected mono stereo output')
        sfx_pcm, sfx_blocks = original_sfx(exe, pe, image, dat, offset, length)
        inputs = [(s, m, m) for s, m in zip(sfx_pcm, music_pcm[::2])]
        if any(not -32768 <= s + m <= 32767 for s, m, _ in inputs):
            raise RuntimeError(f'{table}: selected case hits unmodeled final mixer overflow')
        mixed, mix_blocks = original_mix(exe, inputs)
        original = struct.pack('<5292h', *(value for pair in mixed for value in pair))
        stim, _ = extract(dat, 0, (bank,))
        stim_path = work / 'source.stim'
        stim_path.write_bytes(stim)
        actual = subprocess.check_output([str(native), str(stim_path), str(dat_path),
                                         str(offset), str(length), str(order), '882'], env=env)
        if len(actual) != len(original):
            raise RuntimeError(f'{table}: native PCM length differs')
        mismatches = sum(original[i:i+4] != actual[i:i+4] for i in range(0, len(original), 4))
        rows.append({'table': table, 'fixture': str(fixture_path.relative_to(ROOT)),
                     'fixture_sha256': sha(trace_data), 'sfx_event': sfx, 'music_event': music,
                     'sfx_descriptor': hex(desc), 'sfx_data_offset': hex(offset), 'sfx_length': length,
                     'sfx_profile': profile_path, 'sfx_profile_sha256': sha(profile_data),
                     'sfx_sample_sha256': sample_sha,
                     'music_bank_offset': hex(bank), 'music_order': order, 'frames': 2646,
                     'pre_frames': 882, 'original_sfx_blocks': sfx_blocks, 'original_mix_blocks': mix_blocks,
                     'original_pcm_sha256': sha(original), 'native_pcm_sha256': sha(actual),
                     'mismatch_frames': mismatches, 'status': 'EXACT' if not mismatches else 'DIFFERENT'})
        print(table, rows[-1]['status'], flush=True)
    if sha(native.read_bytes()) != native_sha or sha(library.read_bytes()) != lib_sha:
        raise RuntimeError('Native binary or library changed during comparison')
    result = {'status': 'MEASURED_BOUNDED', 'scope': __doc__, 'exe_sha256': EXE_SHA,
              'dat_sha256': {name: TABLES[name][0] for name in ('space', 'demon')},
              'native_sha256': native_sha, 'library_sha256': lib_sha, 'cases': rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    if any(row['mismatch_frames'] for row in rows):
        raise SystemExit(f'Original/native PCM differs; see {args.output}')
    print('PASS: Space and Demon trace-derived music/SFX combinations')


if __name__ == '__main__':
    main()
