#!/usr/bin/env python3
"""Original/native/SDL agreement for Pirate's complete clock and legal controls."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TIMING = ['previous_ms', 'physics_accumulator', 'frame_accumulator', 'frame_count',
          'crt_seed', 'rng_b4', 'rng_b8', 'phase', 'dmd_state',
          'field_46e554', 'field_46e53a']


def state_hash(states):
    return hashlib.sha256(bytes(v for state in states for v in state)).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', type=Path, default=ROOT / 'build/native/pirate_session_probe')
    parser.add_argument('--viewer', type=Path, default=ROOT / 'build/native/slamview')
    parser.add_argument('--steps', type=int, choices=[1000, 10000], default=1000)
    parser.add_argument('--flippers', action='store_true')
    args = parser.parse_args()
    case = 'pirate-full-input' if args.flippers else ('pirate-full-tick' if args.steps == 1000 else 'pirate-full-10000')
    path = ROOT / 'build/oracle' / case
    original = json.loads((path / 'trace.json').read_text())
    fixture = json.loads((ROOT / 'analysis/traces' / f'{case}.json').read_text())
    assert args.steps == original['tick_count'] == fixture['tick_count']
    assert original['errors'] == [] and original['gameplay_stubs'] == []
    states = original['states']
    assert len(states) == args.steps + 1 and all(len(s) == 100 for s in states)
    assert state_hash(states) == fixture['states_sha256']
    globals_ = original['globals']
    timing = [[row[key] for key in TIMING] for row in globals_]
    dmd = [row['dmd_sha256'] for row in globals_]
    assert hashlib.sha256(json.dumps(timing, separators=(',', ':')).encode()).hexdigest() == fixture['timing_sha256']
    assert hashlib.sha256(''.join(dmd).encode()).hexdigest() == fixture['dmd_sequence_sha256']
    prepared = ROOT / 'build/oracle/pirate-full-tick'
    dat = ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT'
    native_path = path / 'native-verified.json'
    command = [args.native, prepared, dat, native_path, str(args.steps), '--full']
    if args.flippers:
        command.append('--flippers')
    subprocess.run(command, check=True)
    native = json.loads(native_path.read_text())
    assert native['states'] == states, 'Native ball differs from original'
    assert native['timing'] == timing, 'Original clock/rules/RNG differ'
    assert native['dmd_sha256'] == dmd, 'Original DMD pixels differ'
    rendered_path = path / 'rendered-verified.json'
    screenshot = path / 'native-verified.bmp'
    command = [args.viewer, dat, '--pirate-play', prepared, '--autoplay', '--no-lamps',
               '--frames', str(args.steps // 4), '--trace-output', rendered_path,
               '--capture', screenshot]
    if args.flippers:
        command.append('--autoplay-flippers')
    subprocess.run(command, env=dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy'), check=True)
    rendered = json.loads(rendered_path.read_text())
    assert rendered['error'] == '' and rendered['tick_count'] == args.steps
    assert rendered['states'] == states and rendered['timing'] == timing
    assert rendered['dmd_sha256'] == dmd, 'Rendering altered original DMD state'
    assert screenshot.read_bytes()[:2] == b'BM'
    report = dict(status='VERIFIED', tick_count=args.steps, ball_bytes_per_tick=100,
                  timing_fields_per_tick=len(TIMING), original_dmd_frames=args.steps // 4,
                  native_reset_and_sdl_exact=True, flipper_inputs=args.flippers,
                  mode_changes=original['mode_changes'], gameplay_stubs=[],
                  scope='Bounded original full-clock trajectory; complete table/all-mode acceptance pending')
    (path / 'native-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'Pirate {args.steps}: ball/clock/rules/RNG/DMD/reset/SDL exact; flippers={args.flippers}')


if __name__ == '__main__':
    main()
