#!/usr/bin/env python3
"""Compare the two simultaneous Demon trace SFX with Retail tracker output.

The two SFX requests occurred at the same gameplay step in a retained diagnostic
trace. This test reconstructs them as simultaneous idle voices over a fresh
Retail startup track, not the original preceding voice state, actual game/audio
cadence, live mixed device output, or a proof of every reachable overlap.
Original assets and PCM are confined to --work, not the metrics-only report.
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
from extract_mean_stim import extract
from verify_retail_final_mix import original_mix
from verify_retail_tracker_pcm import EXE_SHA, GAME, ROOT, TABLES
from verify_table_combined_pcm import original_effects

FIXTURE = ROOT / 'analysis/traces/demon-clock-award-0-rewards.json'
PROFILE = ROOT / 'analysis/demon-audio-profile.json'
SAMPLES = [(0x46329c, 0x79c0d, 4490, '7ac1a594d0c4ce6366bc0ea5543cfa5c770479468c161a41e90b1563b67ccb11'),
           (0x4632c0, 0x7ad97, 4012, '59a22840ff1120b42be1a7634ba6f4d590b6336cd668f51eaf549e64b8c6a5ad')]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--library', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.work.mkdir(parents=True, exist_ok=True)
    native, library = a.native.resolve(), a.library.absolute()
    env = dict(os.environ, LD_LIBRARY_PATH=str(library.parent))
    if str(library) not in subprocess.check_output(['ldd', str(native)], env=env, text=True):
        raise RuntimeError(f'{native} does not link to {library}')
    native_hash, library_hash = sha(native.read_bytes()), sha(library.read_bytes())
    exe, dat_path = (GAME / 'SLAMTILT.EXE').read_bytes(), GAME / 'DAT/DEMON.DAT'
    dat = dat_path.read_bytes()
    dat_hash, bank, order = TABLES['demon']
    if sha(exe) != EXE_SHA or sha(dat) != dat_hash:
        raise RuntimeError('Unsupported Windows Retail executable or Demon DAT SHA')
    fixture_data, profile_data = FIXTURE.read_bytes(), PROFILE.read_bytes()
    fixture, profiles = json.loads(fixture_data), json.loads(profile_data)['sample_profiles']
    if (fixture.get('build_sha256') != EXE_SHA or fixture.get('dat_sha256') != dat_hash or
            not fixture.get('original_reset_exact')):
        raise RuntimeError('Demon fixture is not pinned to the expected Retail build')
    events = [e for e in fixture['audio_events'] if e[0] == 2360 and e[1] == 0x5c]
    if len(events) != 2 or [e[4] for e in events] != [s[0] for s in SAMPLES]:
        raise RuntimeError('Expected simultaneous SFX pair not found in Demon fixture')
    pe = pefile.PE(data=exe)
    image = pe.get_memory_mapped_image()
    for descriptor, offset, length, sample_hash in SAMPLES:
        profile = next((x for x in profiles if int(x['descriptor'], 0) == descriptor), None)
        if (not profile or int(profile['offset'], 0) != offset or profile['length'] != length or
                profile['period'] != 226 or profile['pcm_sha256'] != sample_hash or
                sha(dat[offset:offset + length]) != sample_hash):
            raise RuntimeError(f'Sample profile or PCM SHA mismatch at {descriptor:#x}')
        if struct.unpack_from('<4I', image, descriptor - 0x400000)[1:] != (226, 64, length):
            raise RuntimeError(f'Original descriptor fields differ at {descriptor:#x}')
    work = a.work / 'demon'
    subprocess.run([sys.executable, str(ROOT/'tools/verify_retail_tracker_pcm.py'),
                    '--table', 'demon', '--ticks', '3', '--dynamic-voices', '--output', str(work)],
                   check=True, stdout=subprocess.DEVNULL)
    music = struct.unpack('<5292h', (work/'demon-first-tick.s16le').read_bytes())
    if music[::2] != music[1::2]:
        raise RuntimeError('Unexpected non-mono Retail tracker output')
    effects, sfx_blocks = original_effects(exe, dat, [(s[1], s[2]) for s in SAMPLES], 2646)
    rows = [(s, m, m) for s, m in zip(effects, music[::2])]
    if any(not -32768 <= s + m <= 32767 for s, m, _ in rows):
        raise RuntimeError('Unmodeled final mixer overflow in chosen trace-derived case')
    mixed, mix_blocks = original_mix(exe, rows)
    original = struct.pack('<5292h', *(v for pair in mixed for v in pair))
    stim, _ = extract(dat, 0, (bank,))
    stim_file = work/'source.stim'
    stim_file.write_bytes(stim)
    base = [str(native), str(stim_file), str(dat_path), str(order),
            *(str(value) for sample in SAMPLES for value in sample[1:3]), '2646']
    chunks = []
    for chunk in (137, 882, 2646):
        actual = subprocess.check_output(base + [str(chunk)], env=env)
        if len(actual) != len(original):
            raise RuntimeError('Native PCM length differs')
        mismatches = sum(actual[i:i+4] != original[i:i+4] for i in range(0, len(actual), 4))
        chunks.append({'size': chunk, 'mismatch_frames': mismatches, 'native_pcm_sha256': sha(actual)})
    if sha(native.read_bytes()) != native_hash or sha(library.read_bytes()) != library_hash:
        raise RuntimeError('Native binary or library changed during comparison')
    report = {'status': 'MEASURED_BOUNDED', 'scope': __doc__, 'exe_sha256': EXE_SHA,
              'dat_sha256': dat_hash, 'fixture': str(FIXTURE.relative_to(ROOT)),
              'fixture_sha256': sha(fixture_data), 'profile_sha256': sha(profile_data),
              'native_sha256': native_hash, 'library_sha256': library_hash,
              'events': events, 'sample_sha256': [s[3] for s in SAMPLES],
              'music_bank_offset': hex(bank), 'music_order': order, 'frames': 2646,
              'original_sfx_blocks': sfx_blocks, 'original_mix_blocks': mix_blocks,
              'original_pcm_sha256': sha(original), 'chunks': chunks}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    if any(c['mismatch_frames'] for c in chunks):
        raise SystemExit(f'Original/native PCM mismatch; see {a.output}')
    print('PASS: Demon recorded SFX pair plus synthetic-start tracker, three chunk sizes')


if __name__ == '__main__':
    main()
