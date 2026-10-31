#!/usr/bin/env python3
"""Compare three isolated Pirate first-row voices against original voice state.

The Retail state is reconstructed by verify_retail_tracker_pcm.py. Native
libxmp channels are muted independently. Correlations cover one synthetic
882-frame window, not gameplay timing, later notes, effects or loop handling.
"""
import argparse
import hashlib
import json
import math
import os
import struct
import subprocess
import sys
from pathlib import Path

from extract_mean_stim import extract
from verify_retail_tracker_pcm import GAME, TABLES

ROOT = Path(__file__).resolve().parents[1]
FRAMES = 882


def correlation(a, b, lag):
    x, y = ((a[lag:], b[:-lag]) if lag > 0 else
            (a[:lag], b[-lag:]) if lag < 0 else (a, b))
    energy = sum(v * v for v in x) * sum(v * v for v in y)
    assert energy
    return sum(v * w for v, w in zip(x, y)) / math.sqrt(energy)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--floor-library', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(ROOT / 'tools/verify_retail_tracker_pcm.py'),
                    '--table', 'pirate', '--output', str(args.work)], check=True)
    original = json.loads((args.work / 'pirate-report.json').read_text())
    dat = (GAME / 'DAT/PIRATE.DAT').read_bytes()
    sha, offset, order = TABLES['pirate']
    assert hashlib.sha256(dat).hexdigest() == sha
    stim, _ = extract(dat, 0, (offset,))
    stim_path = args.work / 'pirate-bank0.stim'
    stim_path.write_bytes(stim)
    baseline_env = dict(os.environ)
    baseline_env.pop('LD_LIBRARY_PATH', None)
    floor_env = dict(baseline_env, LD_LIBRARY_PATH=str(args.floor_library.resolve().parent))
    linkage = subprocess.check_output(['ldd', str(args.native.resolve())], env=floor_env, text=True)
    assert str(args.floor_library.resolve().parent / 'libxmp.so.4') in linkage
    cases = []
    for channel in (1, 2, 3):
        row = original['channels'][channel]
        _, address, length, _, _, period, volume, _ = row
        assert volume == 64 and length > 0
        sample = dat[address - 0x1100000:address - 0x1100000 + length]
        step = (((0x361f0f // period) << 32) // 44100) & ~15
        indices = [(i * step) >> 32 for i in range(FRAMES)]
        assert max(indices) < len(sample)
        model = []
        for index in indices:
            value = sample[index]
            value = value if value < 128 else value - 256
            model.append(value * (0x20000 // 6) * 127 // 65536)
        variants = {}
        for name, env in (('baseline', baseline_env), ('floor', floor_env)):
            result = subprocess.check_output([str(args.native.resolve()), str(stim_path),
                                              str(order), str(channel)], env=env)
            assert len(result) == 4 + FRAMES * 4
            native_period = struct.unpack_from('<I', result)[0]
            pcm = struct.unpack_from(f'<{FRAMES * 2}h', result, 4)
            assert pcm[::2] == pcm[1::2]
            pcm = pcm[::2]
            best, lag = max((correlation(model, pcm, x), x) for x in range(-8, 9))
            variants[name] = {'period_q12': native_period,
                              'zero_offset_correlation': round(correlation(model, pcm, 0), 6),
                              'best_correlation': round(best, 6), 'best_offset_frames': lag}
        cases.append({'channel': channel, 'original_period': period,
                      'sample_offset': hex(address - 0x1100000), 'variants': variants})
    assert cases[0]['variants']['floor']['period_q12'] != cases[0]['original_period'] * 4096
    assert all(c['variants']['floor']['period_q12'] == c['original_period'] * 4096
               for c in cases[1:])
    assert all(c['variants']['floor']['zero_offset_correlation'] > 0.999
               for c in cases[1:])
    report = {'status': 'VERIFIED_BOUNDED', 'scope': __doc__,
              'original_exe_sha256': original['exe_sha256'], 'dat_sha256': sha,
              'native_probe_sha256': hashlib.sha256(args.native.read_bytes()).hexdigest(),
              'floor_library_sha256': hashlib.sha256(args.floor_library.read_bytes()).hexdigest(),
              'frames': FRAMES, 'cases': cases}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: Pirate period divergence localized to channel 1; channels 2/3 agree with floor model')


if __name__ == '__main__':
    main()
