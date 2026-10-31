#!/usr/bin/env python3
"""Compare twelve retained Demon clock awards' audio requests with SDL.

Original fixtures use diagnostic contacts and corrected historical startup;
this covers recorded requests, not natural reachability or audible PCM.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from verify_retail_music_events import ROOT, GAME, BUILD_SHA, DAT_SHA, run_case, sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--jobs', type=int, default=2)
    args = p.parse_args()
    binary = args.native.resolve()
    before = sha(binary)
    assert sha(GAME/'SLAMTILT.EXE') == BUILD_SHA
    assert sha(GAME/'DAT/DEMON.DAT') == DAT_SHA['demon']
    args.output.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        rows = list(pool.map(lambda i: run_case('demon', f'clock-award-{i}', binary, args.output), range(12)))
    assert sha(binary) == before
    report = {'status': 'VERIFIED_BOUNDED', 'scope': __doc__, 'exe_sha256': BUILD_SHA,
              'dat_sha256': DAT_SHA['demon'], 'native_sha256': before, 'cases': rows}
    (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f"PASS: {len(rows)} Demon clock awards, {sum(r['ticks'] for r in rows)} steps")


if __name__ == '__main__':
    main()
