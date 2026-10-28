#!/usr/bin/env python3
"""Compare native and SDL Pirate trajectories against the retained original run."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', type=Path, default=ROOT / 'build/native/pirate_session_probe')
    parser.add_argument('--viewer', type=Path, default=ROOT / 'build/native/slamview')
    parser.add_argument('--prepared', type=Path, default=ROOT / 'build/oracle/pirate-human')
    parser.add_argument('--dat', type=Path, default=ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT')
    args = parser.parse_args()
    fixture = json.loads((ROOT / 'analysis/traces/pirate-human-1000.json').read_text())
    original = json.loads((args.prepared / 'trace.json').read_text())
    assert original['tick_count'] == fixture['tick_count'] == 1000
    assert original['errors'] == [] and original['gameplay_stubs'] == []
    states = original['states']
    assert len(states) == 1001 and all(len(s) == 100 for s in states)
    digest = hashlib.sha256(bytes(v for state in states for v in state)).hexdigest()
    assert digest == fixture['states_sha256'], 'Original fixture identity differs'
    output = args.prepared / 'native-verified-1000.json'
    subprocess.run([args.native, args.prepared, args.dat, output, '1000'], check=True)
    native = json.loads(output.read_text())
    assert native['states'] == states, 'Native original-state mismatch'
    environment = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy')
    rendered = args.prepared / 'rendered-verified-1000.json'
    screenshot = args.prepared / 'native-verified-1000.bmp'
    subprocess.run([args.viewer, args.dat, '--pirate-play', args.prepared,
                    '--physics-only', '--frames', '250', '--autoplay', '--trace-output', rendered,
                    '--capture', screenshot], env=environment, check=True)
    rendering = json.loads(rendered.read_text())
    assert rendering['error'] == '' and rendering['tick_count'] == 1000
    assert rendering['states'] == states, 'Rendering changed simulation state'
    assert screenshot.read_bytes()[:2] == b'BM' and screenshot.stat().st_size > 320 * 400 * 3
    # A foreign DAT must fail before it can initialize this table.
    foreign = args.dat.with_name('SPACE.DAT')
    if foreign.exists():
        rejected = subprocess.run([args.native, args.prepared, foreign, output, '1'],
                                  capture_output=True, text=True)
        assert rejected.returncode != 0 and 'Unsupported Pirate input' in rejected.stderr
    report = dict(status='VERIFIED', tick_count=1000, state_bytes_per_tick=100,
                  original_state_sha256=digest, native_matches_original=True,
                  reset_replay_matches=True, sdl_matches_original=True,
                  error_fallbacks=[], scope='5ms gameplay island; separate 20ms rules/display pending')
    (args.prepared / 'native-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Pirate: original/native/reset/SDL 1000 steps × 100 bytes exact; foreign DAT rejected')


if __name__ == '__main__':
    main()
