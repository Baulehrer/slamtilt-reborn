#!/usr/bin/env python3
"""Compare selected original mode/minigame request streams with native SDL audio.

Retained original fixture captures contain diagnostic contacts and a synthetic,
incorrect first music request. Correct only that first row using the separately
executed Retail initialization oracle; subsequent events remain exact.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
from retail_audio_fixture import corrected_audio_events

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
CASES = {'space': ['bigblam', 'mission-campaign', 'multiball'],
         'demon': ['final-campaign', 'video-consecutive', 'kickback-on', 'clock-award-4', 'clock-rewards']}
BUILD_SHA = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
DAT_SHA = {'space': '18a308bdfa9fe141f57d4462a44dc4dd69cb32c35f9e6f83462fce770600115b',
           'demon': '0d78f5dbc069c5082cecce06f9620385288f615c03c83696483a43f272069c4d'}

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def run_case(table, case, binary, work):
    path = ROOT/f'build/oracle/{table}-modes/{case}-rewards.json'
    pin = ROOT/f'analysis/traces/{table}-{case}-rewards.json'
    source, frozen = json.loads(path.read_text()), json.loads(pin.read_text())
    assert source['case'] == case and source['table'] == table
    assert source['original_reset_exact'] and frozen['original_reset_exact']
    assert source['build_sha256'] == frozen['build_sha256'] == BUILD_SHA
    assert source['dat_sha256'] == frozen['dat_sha256'] == DAT_SHA[table]
    for key in ('audio_events', 'inputs', 'diagnostic_shots', 'tick_count'):
        assert source[key] == frozen[key], (table, case, key)
    count = source['tick_count']; assert count > 0 and count % 4 == 0
    work.mkdir(parents=True, exist_ok=True)
    audio = work/f'{table}-{case}-audio.json'
    cmd = [str(binary), table, str(ROOT/f'build/oracle/{table}-full-game'),
           str(GAME/f'DAT/{table.upper()}.DAT'), '--frames', str(count//4),
           '--replay', str(path), '--diagnostic-shots', str(path), '--replay-only',
           '--audio', '--audio-trace', str(audio)]
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy',
               XDG_DATA_HOME=str(work/f'{table}-{case}-profile'))
    p = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
    if p.returncode: raise RuntimeError((table, case, p.returncode, p.stderr[-1500:]))
    actual = json.loads(audio.read_text()); expected = corrected_audio_events(source['audio_events'], table)
    assert actual['enabled'] and actual['queued_bytes'] > 0
    assert actual['events'] == expected, (table, case, 'audio events differ')
    music = sorted({tuple(e[1:4]) for e in expected if e[1] in (0x84,0x88,0x90)})
    print(table, case, count, 'steps;', len(expected), 'audio requests PASS', flush=True)
    return {'table': table, 'case': case, 'ticks': count, 'diagnostic_contacts': len(source['diagnostic_shots']),
            'original_trace_sha256': sha(path), 'pinned_fixture_sha256': sha(pin),
            'music_requests': [list(e) for e in music], 'audio_requests': len(expected)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', type=Path, default=ROOT/'build/native/slamslice')
    parser.add_argument('--output', type=Path, default=ROOT/'build/music-audit/space-demon')
    parser.add_argument('--jobs', type=int, default=2)
    args = parser.parse_args(); binary = args.native.resolve(); before = sha(binary)
    assert sha(GAME/'SLAMTILT.EXE') == BUILD_SHA
    for table, expected in DAT_SHA.items(): assert sha(GAME/f'DAT/{table.upper()}.DAT') == expected
    jobs = [(table, case) for table, cases in CASES.items() for case in cases]
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        rows = list(pool.map(lambda item: run_case(*item, binary, args.output), jobs))
    assert sha(binary) == before
    result = {'status': 'VERIFIED_BOUNDED', 'original_build_sha256': BUILD_SHA,
              'native_sha256': before, 'cases': rows,
              'scope': 'Eight retained original mode/minigame traces; diagnostic contacts; historical synthetic start corrected from separate executed Retail initialization; later SDL audio service events exact. Does not prove final mixed PCM, human listening or unvisited original branches.'}
    (args.output/'report.json').write_text(json.dumps(result, indent=2)+'\n')
    print(len(rows), 'original/native audio-event cases passed')

if __name__ == '__main__': main()
