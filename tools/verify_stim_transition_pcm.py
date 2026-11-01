#!/usr/bin/env python3
"""Measure selected table order transitions against SHA-pinned Retail routines.

The original and native each run one previous tracker/mixer tick before
selecting the target order. These adapted setups do not reproduce the full
game scheduler or establish which order transitions occur during play.
Private PCM stays in the work directory; only hashes and metrics are reported.
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
from verify_retail_tracker_pcm import ROOT, GAME, TABLES, EXE_SHA

CASES = ((0, 16), (0, 24), (0, 25), (0, 26), (0, 27), (0, 28), (0, 74), (1, 46))
BANKS = {'mean': (0x5c2d2, 0x61590), 'pirate': (0x51876, 0x568e8),
         'space': (0x53642, 0x5b8e0, 0x5fef8), 'demon': (0x6ffb4, 0x6b2bc, 0x6e2ce)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--table', choices=tuple(BANKS), default='mean')
    p.add_argument('--library', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--ticks', type=int, default=32)
    p.add_argument('--service', type=lambda value: int(value, 0), choices=(0x90, 0x84, 0x88), help='Exercise a same-bank sequencer service')
    p.add_argument('--same-order', action='store_true', help='Restart the current order instead of testing the eight target positions')
    p.add_argument('--require-exact', action='store_true')
    p.add_argument('--allow-original-unresolved', action='store_true', help='Report original faults without counting them as an exact match')
    a = p.parse_args()
    assert 1 <= a.ticks <= 2048
    a.work.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, LD_LIBRARY_PATH=str(a.library.absolute().parent))
    assert str(a.library.absolute()) in subprocess.check_output(['ldd', str(a.native.resolve())], env=env, text=True)
    dat = (GAME / 'DAT' / f'{a.table.upper()}.DAT').read_bytes()
    assert hashlib.sha256(dat).hexdigest() == TABLES[a.table][0]
    offsets = BANKS[a.table]
    banks, lengths = [], []
    for bank, offset in enumerate(offsets):
        path = a.work / f'bank-{bank}.stim'
        module, meta = extract(dat, 0, (offset,))
        path.write_bytes(module)
        banks.append(path)
        lengths.append(meta['orders'])
    results = []
    warm_orders = (5, 7) if a.table == 'mean' else (0, TABLES[a.table][2])
    for warm in warm_orders:
        cases = (tuple((b, warm) for b, length in enumerate(lengths) if warm < length)
                 if a.same_order else CASES if a.table == 'mean' else
                 tuple((b, order) for b, length in enumerate(lengths) for order in sorted({0, length//2, length-1})))
        for bank, order in cases:
            if warm >= lengths[bank]:
                continue
            work = a.work / f'warm-{warm}-bank-{bank}-order-{order}'
            cmd = [sys.executable, str(ROOT / 'tools/verify_retail_tracker_pcm.py'),
                   '--table', a.table, '--bank-offset', hex(offsets[bank]), '--order', str(order),
                   '--warm-order', str(warm), '--ticks', str(a.ticks), '--dynamic-voices',
                   '--allow-silent', '--output', str(work)]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode:
                results.append({'warm_order': warm, 'bank': bank, 'order': order,
                                'status': 'ORIGINAL_UNRESOLVED', 'error_tail': proc.stderr[-400:]})
                continue
            original = (work / f'{a.table}-first-tick.s16le').read_bytes()
            native_cmd = [str(a.native.resolve()), str(banks[bank].resolve()),
                          str(warm), str(order), str(a.ticks)]
            if a.service is not None:
                native_cmd.append(str(a.service))
            native = subprocess.check_output(native_cmd, env=env)
            assert len(original) == len(native) == a.ticks * 882 * 4
            original_channels = struct.unpack(f'<{len(original)//2}h', original)
            native_channels = struct.unpack(f'<{len(native)//2}h', native)
            assert original_channels[::2] == original_channels[1::2]
            assert native_channels[::2] == native_channels[1::2]
            x, y = original_channels[::2], native_channels[::2]
            same = sum(i == j for i, j in zip(x, y))
            xx, yy = sum(i*i for i in x), sum(i*i for i in y)
            results.append({'warm_order': warm, 'bank': bank, 'order': order,
                            'status': 'EXACT' if same == len(x) else 'DIFFERENT',
                            'frames': len(x), 'exact_frames': same,
                            'first_mismatch_tick': next((i//882 for i, (u, v) in enumerate(zip(x, y)) if u != v), None),
                            'correlation': round(sum(u*v for u, v in zip(x, y))/math.sqrt(xx*yy), 6) if xx and yy else None,
                            'original_sha256': hashlib.sha256(original).hexdigest(),
                            'native_sha256': hashlib.sha256(native).hexdigest()})
    report = {'status': 'MEASURED_BOUNDED', 'scope': __doc__, 'exe_sha256': EXE_SHA,
              'table': a.table, 'dat_sha256': TABLES[a.table][0], 'bank_offsets': [hex(x) for x in offsets],
              'service': hex(a.service) if a.service is not None else None, 'warm_ticks': 1,
              'tracker_ticks': a.ticks, 'library_sha256': hashlib.sha256(a.library.read_bytes()).hexdigest(),
              'native_sha256': hashlib.sha256(a.native.read_bytes()).hexdigest(), 'cases': results}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({status: sum(c['status'] == status for c in results)
                      for status in ('EXACT', 'DIFFERENT', 'ORIGINAL_UNRESOLVED')}))
    allowed = ('EXACT', 'ORIGINAL_UNRESOLVED') if a.allow_original_unresolved else ('EXACT',)
    if a.require_exact and (not any(c['status'] == 'EXACT' for c in results) or
                            any(c['status'] not in allowed for c in results) or
                            any((c['warm_order'], c['bank'], c['order']) not in ((7, 1, 46), (7, 1, 7))
                                for c in results if c['status'] == 'ORIGINAL_UNRESOLVED')):
        raise SystemExit('Some transitions differ or could not be evaluated; see report')


if __name__ == '__main__':
    main()
