#!/usr/bin/env python3
"""Compare bounded first-tick Retail tracker PCM with native table playback.

The original's tracker state, full music volume, mixer configuration and 882
frame window are explicitly adapted in verify_retail_tracker_pcm.py. Samples
are not asserted identical: this test checks mono, deterministic chunking and
an approximate level range while recording the remaining timing/PCM gap.
"""
import argparse
import hashlib
import json
import math
import struct
import subprocess
import sys
from pathlib import Path

from extract_mean_stim import extract
from verify_retail_tracker_pcm import GAME, TABLES

ROOT = Path(__file__).resolve().parents[1]
FRAMES = 882


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    results = []
    for name, (expected_dat, offset, order) in TABLES.items():
        subprocess.run([sys.executable, str(ROOT / 'tools/verify_retail_tracker_pcm.py'),
                        '--table', name, '--output', str(args.output)], check=True)
        dat = (GAME / 'DAT' / f'{name.upper()}.DAT').read_bytes()
        assert digest(dat) == expected_dat
        stim, _ = extract(dat, 0, (offset,))
        stim_file = args.output / f'{name}-bank0.stim'
        stim_file.write_bytes(stim)
        def native(chunk):
            return subprocess.check_output([str(args.native.resolve()), str(stim_file),
                                            str(FRAMES), str(chunk), 'restart', str(order), 'retail'])
        pcm = native(FRAMES)
        assert pcm == native(137), f'{name}: chunk or restart changed PCM'
        original_pcm = (args.output / f'{name}-first-tick.s16le').read_bytes()
        a = struct.unpack(f'<{2 * FRAMES}h', original_pcm)
        b = struct.unpack(f'<{2 * FRAMES}h', pcm)
        assert a[::2] == a[1::2] and b[::2] == b[1::2]
        a, b = a[::2], b[::2]
        aa, bb = sum(x * x for x in a), sum(x * x for x in b)
        assert aa and bb
        ratio = math.sqrt(bb / aa)
        correlation = sum(x * y for x, y in zip(a, b)) / math.sqrt(aa * bb)
        aligned = []
        for lag in range(-8, 9):
            x, y = ((a[lag:], b[:-lag]) if lag > 0 else
                    (a[:lag], b[-lag:]) if lag < 0 else (a, b))
            energy = sum(v * v for v in x) * sum(v * v for v in y)
            aligned.append((sum(v * w for v, w in zip(x, y)) / math.sqrt(energy), lag))
        best_correlation, best_lag = max(aligned)
        assert 0.9 < ratio < 1.1, f'{name}: first-tick level outside bounded tolerance: {ratio}'
        # Mean has a significant phase/PCM gap; do not silently equate samples.
        assert any(x != y for x, y in zip(a, b)), 'unexpected sample identity; reassess test'
        original_report = json.loads((args.output / f'{name}-report.json').read_text())
        results.append({'table': name, 'bank': 0, 'order': order,
                        'original_sha256': digest(original_pcm), 'native_sha256': digest(pcm),
                        'native_rms_over_original': round(ratio, 6),
                        'uncentered_correlation': round(correlation, 6),
                        'best_correlation_within_8_frames': round(best_correlation, 6),
                        'original_relative_frame_offset': best_lag,
                        'original_range': [min(a), max(a)], 'native_range': [min(b), max(b)],
                        'exact_frames': sum(x == y for x, y in zip(a, b)),
                        'executed_original_blocks': original_report['executed_original_blocks']})
    report = {'status': 'VERIFIED_BOUNDED_WITH_PCM_GAP', 'scope': __doc__,
              'native_probe_sha256': digest(args.native.read_bytes()),
              'output': '44100 Hz signed 16-bit duplicated mono', 'frames_per_table': FRAMES,
              'native_tracker_mix': {'separation': 0, 'interpolation': 'nearest', 'volume_percent': 66},
              'cases': results}
    (args.output / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: four original/native first-tick comparisons; remaining PCM differences recorded')


if __name__ == '__main__':
    main()
