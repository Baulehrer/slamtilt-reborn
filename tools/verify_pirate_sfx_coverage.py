#!/usr/bin/env python3
"""Replay the retained Pirate knife scenario and validate both missing SFX.

The underlying fixture includes diagnostic contacts and a synthetic startup
request corrected from the independently verified Retail reset. It does not
prove natural gameplay reachability, final original PCM or physical listening.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from retail_audio_fixture import corrected_audio_events

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT/'analysis/traces/pirate-knife-auto-audio.json'
BUILD_SHA = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
DAT_SHA = '6050b576678ec9b1878c203c057089b1c2499cdfd4a1ebdd7220f9d665fac7d6'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--viewer', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    fixture = json.loads(FIXTURE.read_text())
    assert fixture['build_sha256'] == BUILD_SHA and fixture['dat_sha256'] == DAT_SHA
    assert len(fixture['cases']) == 1 and fixture['cases'][0]['case'] == 'knife-auto-success'
    before_native, before_viewer = sha(a.native), sha(a.viewer)
    subprocess.run([sys.executable, str(ROOT/'tools/verify_pirate_audio.py'),
                    '--fixture', str(FIXTURE), '--work', str(a.output),
                    '--native', str(a.native.resolve()), '--viewer', str(a.viewer.resolve()),
                    '--all-sdl-cases'], check=True, cwd=ROOT)
    assert (sha(a.native),sha(a.viewer)) == (before_native,before_viewer)
    native = json.loads((a.output/'native.json').read_text())
    audio = json.loads((a.output/'knife-auto-success-sdl.json').read_text())
    expected = corrected_audio_events(fixture['cases'][0]['events'], 'pirate')
    assert audio['events'] == expected and audio['enabled'] and not audio['error']
    assert native['cases'][0]['ticks'] == fixture['cases'][0]['tick_count']
    counts = {hex(desc):sum(event[1] == 0x5c and event[4] == desc for event in expected)
              for desc in (0x46505c,0x465080)}
    assert all(counts.values())
    report = {'status':'VERIFIED_BOUNDED', 'scope':__doc__, 'build_sha256':BUILD_SHA,
              'dat_sha256':DAT_SHA, 'fixture_sha256':sha(FIXTURE),
              'native_sha256':before_native, 'viewer_sha256':before_viewer,
              'case':'knife-auto-success', 'ticks':fixture['cases'][0]['tick_count'],
              'service_requests':len(expected), 'target_descriptor_counts':counts,
              'pcm_cases':native['pcm_cases']}
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: Pirate knife scenario, both previously unobserved descriptors matched SDL')


if __name__ == '__main__':
    main()
