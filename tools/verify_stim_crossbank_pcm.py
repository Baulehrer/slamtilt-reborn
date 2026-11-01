#!/usr/bin/env python3
"""Compare bounded, manually primed Retail cross-bank tracker transitions.

A configurable number of tracker/mixer ticks precedes a bank/order switch.
A fresh source and target context are used per case. Events, reachability,
device timing, multiball and other game services are not modeled. No original
media or PCM is in the report.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from extract_mean_stim import extract
from verify_retail_tracker_pcm import ROOT, GAME, TABLES, EXE_SHA

BANKS = {'mean': (0x5c2d2, 0x61590), 'pirate': (0x51876, 0x568e8),
         'space': (0x53642, 0x5b8e0, 0x5fef8), 'demon': (0x6ffb4, 0x6b2bc, 0x6e2ce)}
REPRESENTATIVE = {('mean', 0, 1, 5, 31), ('mean', 0, 1, 5, 46), ('mean', 1, 0, 5, 16),
                  ('pirate', 0, 1, 34, 27), ('pirate', 1, 0, 34, 34),
                  ('space', 0, 2, 32, 28), ('space', 2, 0, 32, 33),
                  ('demon', 0, 2, 25, 18), ('demon', 2, 1, 25, 15)}


EFFECT8 = {('mean', 1, 0, warm, order) for warm in (5, 7) for order in (1, 16, 23, 24, 25, 26)} | {('mean', 0, 1, warm, 46) for warm in (5, 7)}


def sha(data): return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True); p.add_argument('--library', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--table', choices=tuple(BANKS)); p.add_argument('--ticks', type=int, default=32)
    p.add_argument('--service', type=lambda value: int(value, 0), choices=(0x90, 0x84, 0x88), default=0x90)
    p.add_argument('--preempt', action='store_true', help='Start base music before the 84/88 request')
    p.add_argument('--scheduler', action='store_true', help='Run the Retail service scheduler before each tracker tick')
    p.add_argument('--warm-ticks', type=int, default=1, help='Number of prior base tracker/mixer ticks')
    p.add_argument('--same-bank', action='store_true', help='Compare switches to the same bank')
    p.add_argument('--representative', action='store_true', help='Run the nine selected longer transition cases')
    p.add_argument('--effect8', action='store_true', help='Run selected Mean orders containing instrument-only effect 8')
    p.add_argument('--require-exact', action='store_true'); p.add_argument('--allow-original-unresolved', action='store_true')
    p.add_argument('--allow-f00-boundary', action='store_true', help='Permit the two documented isolated-tracker F00 boundary differences')
    a = p.parse_args(); assert 1 <= a.ticks <= 2048 and 1 <= a.warm_ticks <= 2048 and (not a.preempt or a.service != 0x90) and (not a.scheduler or a.preempt); a.work.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, LD_LIBRARY_PATH=str(a.library.absolute().parent))
    assert str(a.library.absolute()) in subprocess.check_output(['ldd', str(a.native.resolve())], env=env, text=True)
    native_sha, library_sha = sha(a.native.read_bytes()), sha(a.library.read_bytes())
    rows = []
    for table, offsets in BANKS.items():
        if a.table and a.table != table: continue
        dat = (GAME/'DAT'/f'{table.upper()}.DAT').read_bytes(); assert sha(dat) == TABLES[table][0]
        modules, lengths = [], []
        for bank, offset in enumerate(offsets):
            data, meta = extract(dat, 0, (offset,)); path = a.work/f'{table}-{bank}.stim'
            path.write_bytes(data); modules.append(path.resolve()); lengths.append(meta['orders'])
        warm_orders = (5, 7) if table == 'mean' else (0, TABLES[table][2])
        for source in range(len(offsets)):
            for target in range(len(offsets)):
                if (source == target) != a.same_bank: continue
                for warm in warm_orders:
                    if warm >= lengths[source]: continue
                    selected_cases = EFFECT8 if a.effect8 else REPRESENTATIVE
                    selected = (sorted(o for t, s, d, w, o in selected_cases
                                       if t == table and s == source and d == target and w == warm)
                                if a.representative or a.effect8 else sorted({0, lengths[target]//2, lengths[target]-1}))
                    for order in selected:
                        work = a.work/f'{table}-{source}-{target}-{warm}-{order}'
                        cmd = [sys.executable, str(ROOT/'tools/verify_retail_tracker_pcm.py'), '--table', table,
                               '--warm-order', str(warm), '--warm-bank-offset', hex(offsets[source]),
                               '--warm-ticks', str(a.warm_ticks),
                               '--bank-offset', hex(offsets[target]), '--order', str(order), '--ticks', str(a.ticks),
                               '--dynamic-voices', '--allow-silent', '--output', str(work)]
                        if a.scheduler: cmd += ['--scheduler-service', hex(a.service)]
                        proc = subprocess.run(cmd, capture_output=True, text=True)
                        key = {'table': table, 'warm_bank': source, 'target_bank': target,
                               'warm_order': warm, 'order': order}
                        if proc.returncode:
                            rows.append(dict(key, status='ORIGINAL_UNRESOLVED', error_tail=proc.stderr[-400:])); continue
                        original = (work/f'{table}-first-tick.s16le').read_bytes()
                        native_cmd = [str(a.native.resolve()), str(modules[source]), str(modules[target]),
                                      str(warm), str(order), str(a.ticks), str(a.service)]
                        if a.preempt or a.warm_ticks != 1:
                            native_cmd += ['preempt' if a.preempt else 'same', str(a.warm_ticks)]
                        probe = subprocess.run(native_cmd, env=env, capture_output=True)
                        if probe.returncode:
                            rows.append(dict(key, status='NATIVE_UNRESOLVED', error_tail=probe.stderr.decode(errors='replace')[-400:])); continue
                        actual = probe.stdout; assert len(actual) == len(original) == a.ticks*882*4
                        same = sum(original[i:i+4] == actual[i:i+4] for i in range(0, len(original), 4))
                        rows.append(dict(key, status='EXACT' if original == actual else 'DIFFERENT',
                                         exact_frames=same, frames=a.ticks*882,
                                         first_mismatch_tick=next((i//(882*4) for i in range(0, len(original), 4)
                                                                   if original[i:i+4] != actual[i:i+4]), None),
                                         original_sha256=sha(original), native_sha256=sha(actual)))
                        print(table, source, target, warm, order, rows[-1]['status'], flush=True)
    if sha(a.library.read_bytes()) != library_sha or sha(a.native.read_bytes()) != native_sha:
        raise RuntimeError('Probe or library changed during comparison')
    report = {'status': 'MEASURED_BOUNDED', 'scope': __doc__, 'exe_sha256': EXE_SHA,
              'dat_sha256': {k: v[0] for k, v in TABLES.items()}, 'library_sha256': library_sha,
              'native_sha256': native_sha, 'service': hex(a.service), 'preempt': a.preempt,
              'scheduler': a.scheduler, 'warm_ticks': a.warm_ticks,
              'same_bank': a.same_bank, 'ticks': a.ticks, 'cases': rows}
    a.output.parent.mkdir(parents=True, exist_ok=True); a.output.write_text(json.dumps(report, indent=2)+'\n')
    permitted = ('EXACT', 'ORIGINAL_UNRESOLVED') if a.allow_original_unresolved else ('EXACT',)
    known_f00 = {('mean', 0, 1, 5, 31): 205, ('pirate', 0, 1, 34, 27): 176}
    def acceptable(row):
        if row['status'] in permitted:
            return True
        key = (row['table'], row['warm_bank'], row['target_bank'], row['warm_order'], row['order'])
        boundary = known_f00.get(key)
        return (a.allow_f00_boundary and a.service in (0x84, 0x88) and boundary is not None and
                row['status'] == 'DIFFERENT' and row.get('first_mismatch_tick') in (boundary, boundary+2))
    if a.require_exact and (not any(r['status'] == 'EXACT' for r in rows) or any(not acceptable(r) for r in rows)):
        raise SystemExit('Differing or unresolved cases; see report')
    print('PASS: report written; unresolved cases remain explicitly labeled')


if __name__ == '__main__': main()
