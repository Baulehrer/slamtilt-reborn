#!/usr/bin/env python3
"""Replay targeted retained Original Space/Demon SFX events through SDL.

Original fixtures include diagnostic contacts except legal-game. The comparison
checks recorded service requests, not final audio waveform or complete gameplay.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

from verify_retail_music_events import ROOT, GAME, BUILD_SHA, DAT_SHA, run_case, sha

CASES = {'space': ('base-rules', 'kickback-off', 'race-variants'),
         'demon': ('twice-cycles', 'legal-game', 'video-wolf-shoot')}
EXPECTED = {'space': {0x465d74, 0x465de0, 0x465e28},
            'demon': {0x463278, 0x463350, 0x4633e0, 0x463398, 0x463428}}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--jobs', type=int, default=3)
    a = p.parse_args()
    binary = a.native.resolve()
    before = sha(binary)
    assert sha(GAME/'SLAMTILT.EXE') == BUILD_SHA
    for table, expected in DAT_SHA.items():
        assert sha(GAME/f'DAT/{table.upper()}.DAT') == expected
    a.output.mkdir(parents=True, exist_ok=True)
    jobs = [(table, case) for table, cases in CASES.items() for case in cases]
    with ThreadPoolExecutor(max_workers=max(1, a.jobs)) as pool:
        rows = list(pool.map(lambda item: run_case(*item, binary, a.output), jobs))
    assert sha(binary) == before
    observed = {table:set() for table in CASES}
    for table, case in jobs:
        source = json.loads((ROOT/f'build/oracle/{table}-modes/{case}-rewards.json').read_text())
        observed[table].update(event[4] for event in source['audio_events'] if event[1] == 0x5c)
    for table in CASES:
        assert EXPECTED[table] <= observed[table], (table, EXPECTED[table]-observed[table])
    report = {'status':'VERIFIED_BOUNDED', 'scope':__doc__, 'exe_sha256':BUILD_SHA,
              'native_sha256':before, 'cases':rows,
              'newly_covered_descriptors':{k:[hex(v) for v in sorted(values)] for k,values in EXPECTED.items()},
              'observed_descriptors':{k:[hex(v) for v in sorted(values)] for k,values in observed.items()}}
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: six retained Original/SDL SFX event replays and eight targeted descriptors')


if __name__ == '__main__':
    main()
