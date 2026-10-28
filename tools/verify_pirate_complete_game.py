#!/usr/bin/env python3
"""Verify the retained complete Pirate game, lamps and native score persistence."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
STEPS = 12000
TIMING = ['previous_ms', 'physics_accumulator', 'frame_accumulator', 'frame_count',
          'crt_seed', 'rng_b4', 'rng_b8', 'phase', 'dmd_state',
          'field_46e554', 'field_46e53a']
SEQUENCES = ['dmd_sha256', 'highscore_sha256', 'lamp_sha256']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_digest(value):
    return digest(json.dumps(value, separators=(',', ':')).encode())


def read_json(path):
    return json.loads(path.read_text())


def compare_trace(actual, expected, label):
    assert actual['tick_count'] == STEPS, f'{label}: incomplete replay'
    if 'error' in actual:
        assert actual['error'] == '', f'{label}: {actual["error"]}'
    for key, wanted in expected.items():
        found = actual[key]
        assert len(found) == len(wanted), f'{label}: {key} sample count differs'
        for tick, (a, b) in enumerate(zip(found, wanted)):
            assert a == b, f'{label}: {key} differs at sample {tick}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', type=Path,
                        default=ROOT / 'build/native/pirate_session_probe')
    parser.add_argument('--viewer', type=Path,
                        default=ROOT / 'build/native/slamview')
    parser.add_argument('--prepared', type=Path,
                        default=ROOT / 'build/oracle/pirate-complete-game-lamps-ready')
    parser.add_argument('--dat', type=Path,
                        default=ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT')
    args = parser.parse_args()
    replay = args.prepared / 'trace.json'
    original = read_json(replay)
    fixture = read_json(ROOT / 'analysis/traces/pirate-complete-game.json')
    assert original['tick_count'] == fixture['tick_count'] == STEPS
    assert original['errors'] == [] and original['gameplay_stubs'] == []
    assert original['deterministic_replay_globals']
    assert original['deterministic_replay_all_ball_bytes']
    assert original['build_sha256'] == fixture['build_sha256']
    assert original['dat_sha256'] == fixture['dat_sha256'] == digest(args.dat.read_bytes())
    assert original['context_hashes'] == fixture['context_hashes']
    for name, wanted in fixture['context_hashes'].items():
        assert Path(name).name == name, 'Invalid context filename in fixture'
        assert digest((args.prepared / name).read_bytes()) == wanted, name
    if 'inputs' in fixture:
        assert original['inputs'] == fixture['inputs'], 'Original inputs differ'
    if 'mode_changes' in fixture:
        assert original['mode_changes'] == fixture['mode_changes']
    if 'timing_fields' in fixture:
        assert fixture['timing_fields'] == TIMING

    states = original['states']
    assert len(states) == STEPS + 1 and all(len(s) == 100 for s in states)
    assert digest(bytes(v for state in states for v in state)) == fixture['states_sha256']
    globals_ = original['globals']
    assert len(globals_) == STEPS
    timing = [[row[key] for key in TIMING] for row in globals_]
    assert json_digest(timing) == fixture['timing_sha256']
    lifecycle = original['lifecycle']
    assert len(lifecycle) == STEPS and all(len(row) == 15 for row in lifecycle)
    assert json_digest(lifecycle) == fixture['lifecycle_sha256']
    expected = dict(states=states, timing=timing, lifecycle=lifecycle)
    for key in SEQUENCES:
        values = ([row[key] for row in globals_] if key == 'dmd_sha256'
                  else original[key])
        assert len(values) == STEPS and all(len(value) == 64 for value in values)
        pinned = key.replace('_sha256', '_sequence_sha256')
        assert digest(''.join(values).encode()) == fixture[pinned], pinned
        expected[key] = values
    assert any(row[6] == 6 for row in lifecycle), 'Initials admission was not reached'
    assert any(row[0] == 0 for row in lifecycle), 'GameOver was not reached'
    assert any(change['before'] == 0 and change['after'] == 1
               for change in original['mode_changes']), 'New game was not reached'

    native_path = args.prepared / 'native-complete-verified.json'
    subprocess.run([args.native, args.prepared, args.dat, native_path,
                    str(STEPS), '--full', '--lamps', '--replay', replay], check=True)
    # The native probe also repeats the entire replay after session.reset().
    compare_trace(read_json(native_path), expected, 'Native/reset')

    rendered_path = args.prepared / 'rendered-complete-verified.json'
    screenshot = args.prepared / 'complete-game-verified.bmp'
    restart_path = args.prepared / 'restart-complete-verified.json'
    environment = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy')
    with tempfile.TemporaryDirectory(prefix='slam-pirate-complete-') as temporary:
        profile = Path(temporary) / 'profile.json'
        assert not profile.exists(), 'Complete replay requires a fresh profile'
        command = [args.viewer, args.dat, '--pirate-play', args.prepared,
                   '--frames', str(STEPS // 4), '--replay', replay,
                   '--highscore-file', profile, '--trace-output', rendered_path,
                   '--capture', screenshot]
        subprocess.run(command, env=environment, check=True)
        compare_trace(read_json(rendered_path), expected, 'SDL')
        assert screenshot.read_bytes()[:2] == b'BM', 'Missing SDL capture'
        assert screenshot.stat().st_size > 320 * 400 * 3

        saved_bytes = profile.read_bytes()
        saved = json.loads(saved_bytes)
        assert type(saved['version']) is int and saved['version'] == 1
        records = saved['records']
        assert len(records) == 50 and all(type(v) is int and 0 <= v <= 255
                                         for v in records)
        final_score_hash = expected['highscore_sha256'][-1]
        assert digest(bytes(records)) == final_score_hash, 'Saved original scores differ'
        assert bytes(records[6:10]) == b'ABC\0', 'Original ABC initials were not saved'
        before = profile.stat()

        # A separate process must load the native profile. One SDL frame runs
        # four steps and precedes the replay's first input at tick 200.
        assert all(event['tick'] >= 4 for event in original['inputs'])
        subprocess.run([args.viewer, args.dat, '--pirate-play', args.prepared,
                        '--frames', '1', '--replay', replay,
                        '--highscore-file', profile, '--trace-output', restart_path],
                       env=environment, check=True)
        restarted = read_json(restart_path)
        assert restarted['error'] == '' and restarted['tick_count'] == 4
        assert restarted['highscore_sha256'] == [final_score_hash] * 4, 'Profile not loaded'
        assert restarted['states'] == states[:5], 'Restart altered initial ball state'
        assert restarted['timing'] == timing[:4], 'Restart altered initial timing'
        assert profile.read_bytes() == saved_bytes, 'Restart changed saved profile bytes'
        after = profile.stat()
        identity = lambda stat: (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)
        assert identity(before) == identity(after), 'Restart rewrote saved profile'

    report = dict(status='VERIFIED', tick_count=STEPS, ball_bytes_per_sample=100,
                  timing_fields_per_tick=len(TIMING), lifecycle_fields_per_tick=15,
                  sdl_frames=STEPS // 4, native_reset_and_sdl_exact=True,
                  lamp_states_exact=True, saved_highscore_sha256=final_score_hash,
                  saved_initials='ABC', fresh_private_profile=True,
                  restart_loaded_without_rewrite=True, gameplay_stubs=[],
                  scope='Retained legal three-ball game, initials, GameOver and new game; not all-mode coverage')
    (args.prepared / 'complete-game-verification.json').write_text(
        json.dumps(report, indent=2) + '\n')
    print('Pirate 12000: ball/timing/DMD/lifecycle/highscores/lamps/reset/SDL exact; '
          'ABC saved and reloaded without rewrite')


if __name__ == '__main__':
    main()
