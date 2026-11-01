#!/usr/bin/env python3
"""Compare a queued lower cue after an upper F00 with pinned Windows Retail.

The service request and tick timing are synthetic. The original x86 request,
scheduler, tracker, voice adapter and mixer run without instruction patches;
this does not establish gameplay reachability or physical-device timing.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from extract_mean_stim import extract
from verify_retail_tracker_pcm import EXE_SHA, GAME, ROOT, TABLES
from verify_stim_crossbank_pcm import BANKS


def digest(data):
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
    assert str(library) in subprocess.check_output(['ldd', str(native)], env=env, text=True)
    native_hash, library_hash = digest(native.read_bytes()), digest(library.read_bytes())
    cases = []
    for table, banks in BANKS.items():
        dat = (GAME / 'DAT' / (table.upper() + '.DAT')).read_bytes()
        assert digest(dat) == TABLES[table][0]
        offsets = (banks[0], banks[-1])
        modules = []
        for i, offset in enumerate(offsets):
            data, _ = extract(dat, 0, (offset,))
            path = (a.work / f'{table}-{i}.stim').resolve()
            path.write_bytes(data)
            modules.append(path)
        scenarios = [(0, TABLES[table][2], 0, TABLES[table][2], 20),
                     (1, 0, 0, TABLES[table][2], 20)]
        if table == 'mean':
            scenarios.append((0, 16, 31, 5, 20))
        if table == 'pirate':
            trace = json.loads((ROOT / 'analysis/traces/pirate-audio-events.json').read_text())
            case = next(c for c in trace['cases'] if c['case'] == 'nudge-tilt-knife')
            assert [657, 136, 1, 2, 0] in case['events'] and [657, 132, 0, 53, 0] in case['events']
            scenarios.append((0, 53, 2, TABLES[table][2], 0))
        for lower_bank, lower_order, upper_order, base_order, queued in scenarios:
            work = a.work / f'{table}-{lower_bank}-{lower_order}-{upper_order}-{queued}'
            trace = work / 'scheduler.json'
            command = [sys.executable, str(ROOT / 'tools/verify_retail_tracker_pcm.py'),
                       '--table', table, '--warm-order', str(base_order),
                       '--warm-bank-offset', hex(offsets[0]), '--warm-ticks', '40',
                       '--bank-offset', hex(offsets[1]), '--order', str(upper_order), '--ticks', '512',
                       '--dynamic-voices', '--allow-silent', '--scheduler-service', '0x88',
                       '--deferred-bank-offset', hex(offsets[lower_bank]), '--deferred-order', str(lower_order),
                       '--deferred-tick', str(queued), '--scheduler-log', str(trace), '--output', str(work)]
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
            states = json.loads(trace.read_text())
            transitions = [s['tick'] for s in states if s['tick'] > queued and s['services'] == 1]
            assert transitions, f'{table}: lower service never activated'
            original = (work / f'{table}-first-tick.s16le').read_bytes()
            actual = subprocess.check_output([str(native), *(str(m) for m in modules),
                str(base_order), str(upper_order), str(lower_bank), str(lower_order), '40', str(queued), '512'], env=env)
            assert len(original) == len(actual) == 512 * 882 * 4
            first = next((i // (882 * 4) for i in range(0, len(original), 4)
                          if original[i:i + 4] != actual[i:i + 4]), None)
            cases.append({'table': table, 'base_order': base_order, 'upper_order': upper_order,
                          'lower_bank': lower_bank, 'lower_order': lower_order, 'queue_tick': queued,
                          'request_evidence': 'pirate nudge-tilt-knife step 657' if table == 'pirate' and queued == 0 else 'synthetic',
                          'activation_tick': transitions[0], 'frames': len(original) // 4,
                          'first_mismatch_tick': first, 'status': 'EXACT' if first is None else 'DIFFERENT',
                          'original_sha256': digest(original), 'native_sha256': digest(actual)})
            print(table, lower_bank, cases[-1]['status'], 'activation', transitions[0], flush=True)
    assert digest(native.read_bytes()) == native_hash and digest(library.read_bytes()) == library_hash
    report = {'status': 'MEASURED_BOUNDED', 'scope': __doc__, 'exe_sha256': EXE_SHA,
              'dat_sha256': {k: v[0] for k, v in TABLES.items()}, 'native_sha256': native_hash,
              'library_sha256': library_hash, 'cases': cases}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    if len(cases) != 10 or any(c['status'] != 'EXACT' for c in cases):
        raise SystemExit('Original/native mismatch; see report')
    print('PASS: 10 controlled deferred-service cases matched')


if __name__ == '__main__':
    main()
