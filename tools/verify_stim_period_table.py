#!/usr/bin/env python3
"""Compare libxmp's 16 ProTracker tuning tables against authenticated Retail bytes.

The comparison covers table entries only; it does not establish effect timing
or complete music equivalence. Original game bytes are not copied to the report.
"""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

import pefile
from verify_retail_tracker_pcm import EXE_SHA, GAME


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--exe', type=Path, default=GAME / 'SLAMTILT.EXE')
    p.add_argument('--libxmp-source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    data = a.exe.read_bytes()
    assert hashlib.sha256(data).hexdigest() == EXE_SHA, 'unrecognized Retail EXE'
    image = pefile.PE(data=data).get_memory_mapped_image()
    text = (a.libxmp_source / 'src/period.c').read_text()
    body = text.split('pt_period_table[16][36] = {', 1)[1].split('\n};', 1)[0]
    groups = re.findall(r'\{([^{}]+)\}', body)
    assert len(groups) == 16
    count = 0
    for tuning, group in enumerate(groups):
        native = list(map(int, re.findall(r'\d+', group)))
        original = struct.unpack_from('<37h', image, 0x466fec - 0x400000 + tuning * 74)
        assert len(native) == 36 and original[0] == original[1]
        assert native == list(original[1:]), f'tuning {tuning} differs'
        count += len(native)
    player = (a.libxmp_source / 'src/player.c').read_text()
    ratios = re.search(r'ratios\[16\]\s*=\s*\{([^}]+)\}', player)
    assert ratios, 'STIM arpeggio ratios not found'
    native_ratios = tuple(map(int, re.findall(r'\d+', ratios.group(1))))
    assert native_ratios == struct.unpack_from('<16I', image, 0x46750c - 0x400000)
    report = {'status': 'VERIFIED_BOUNDED', 'exe_sha256': EXE_SHA,
              'original_table': '0x466fec', 'tunings': 16,
              'notes_per_tuning': 36, 'matching_entries': count,
              'arpeggio_table': '0x46750c', 'matching_arpeggio_ratios': 16,
              'scope': __doc__}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: {count} period entries match Retail')


if __name__ == '__main__':
    main()
