#!/usr/bin/env python3
"""Recheck the 33 previously differing STIM starts against Retail PCM.

A case covers 32 manually clocked ticks, not real game scheduling or full songs.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from verify_retail_tracker_pcm import ROOT

BANKS = {'mean': (0x5c2d2, 0x61590), 'pirate': (0x51876, 0x568e8),
         'space': (0x53642, 0x5b8e0, 0x5fef8),
         'demon': (0x6ffb4, 0x6b2bc, 0x6e2ce)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--library', type=Path, required=True)
    p.add_argument('--baseline', type=Path, default=ROOT / 'analysis/stim-pcm-all-orders-survey.json')
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    cases = [x for x in json.loads(a.baseline.read_text())['cases'] if x['status'] == 'DIFFERENT']
    assert len(cases) == 33
    rows = []
    for case in cases:
        table, bank, order = case['table'], case['bank'], case['order']
        name = f'{table}-{bank}-{order}'
        work = a.work / name
        report = work / 'report.json'
        cmd = [sys.executable, str(ROOT / 'tools/verify_stim_dynamic_pcm.py'),
               '--native', str(a.native.resolve()), '--library', str(a.library.absolute()),
               '--table', table, '--bank-offset', hex(BANKS[table][bank]), '--order', str(order),
               '--ticks', '32', '--allow-silent', '--min-correlation=-1.1',
               '--work', str(work), '--output', str(report)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if proc.returncode:
            rows.append({'case': name, 'status': 'UNRESOLVED', 'error_tail': proc.stderr[-500:]})
        else:
            result = json.loads(report.read_text())['cases'][0]
            rows.append({'case': name, 'status': 'EXACT' if result['exact_frames'] == result['frames'] else 'DIFFERENT',
                         'first_mismatches': result['first_mismatches'][:3]})
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps({'status': 'MEASURED_BOUNDED', 'scope': __doc__, 'cases': rows}, indent=2) + '\n')
    assert all(row['status'] == 'EXACT' for row in rows), 'regression or unresolved case; see report'
    print(f'PASS: {len(rows)} former differences are bit-exact')


if __name__ == '__main__':
    main()
