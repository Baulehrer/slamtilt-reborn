#!/usr/bin/env python3
"""Verify the bounded original Space station sequence after the Super Jackpot.

The existing original trace uses diagnostic physical ball contacts before this
sequence. The complete station sequence itself contains no further contacts.
Original sound *requests* and DMD memory are compared, not mixed audio PCM.
"""
from retail_audio_fixture import corrected_audio_events
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
SOURCE = ROOT / 'build/oracle/space-modes/mission-campaign-rewards.json'
PIN = ROOT / 'analysis/traces/space-mission-campaign-rewards.json'
KEYS = ('states', 'globals', 'poses', 'lifecycle', 'highscore_sha256',
        'lamp_sha256', 'raw_state_sha256', 'ball_pool_sha256',
        'aux_state_sha256', 'weapon_state')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', type=Path, default=ROOT / 'build/native/slamslice')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/space-post-jackpot')
    parser.add_argument('--report', type=Path,
                        default=ROOT / 'analysis/traces/space-post-jackpot-original.json')
    args = parser.parse_args()
    source, pinned = json.loads(SOURCE.read_text()), json.loads(PIN.read_text())
    require(sha(GAME / 'SLAMTILT.EXE') == source['build_sha256'] == pinned['build_sha256'], 'Original EXE hash')
    require(sha(GAME / 'DAT/SPACE.DAT') == source['dat_sha256'] == pinned['dat_sha256'], 'Original DAT hash')
    require(source['original_reset_exact'] and pinned['original_reset_exact'], 'Original reset not verified')
    for key in KEYS:
        require(digest(source[key]) == pinned['sequence_sha256'][key], 'Original vector changed: ' + key)
    for key in ('inputs', 'diagnostic_shots', 'milestones', 'payments', 'audio_events'):
        require(source[key] == pinned[key], 'Original trace metadata changed: ' + key)

    shots = [s for s in source['diagnostic_shots'] if s['label'] == 'earned_station_super']
    payments = [p for p in source['payments'] if p['return_address'] == '0x441f47']
    require(len(shots) == len(payments) == 1, 'Expected one station capture and Super Jackpot')
    trigger, jackpot = shots[0]['tick'], payments[0]['tick']
    released = next(m['tick'] for m in source['milestones'] if m['label'] == 'super_collected')
    prize = [p for p in source['payments'] if p['return_address'] == '0x4413a5' and jackpot < p['tick'] <= released]
    require(payments[0]['amount'] == 75000000 and len(prize) == 1 and prize[0]['amount'] == 5000000,
            'Super Jackpot or following station payout')
    payout = prize[0]['tick']
    require(not any(trigger < s['tick'] < released for s in source['diagnostic_shots']),
            'Sequence contains a diagnostic physical contact after station entry')

    def transitions(rows):
        result = []
        for tick in range(trigger, released + 1):
            status = int.from_bytes(bytes(rows[tick][88:90]), 'little')
            if not result or result[-1][1] != status:
                result.append((tick, status))
        return result

    expected = [(trigger, 2), (trigger + 1, 3), (jackpot, 6), (payout, 3), (released, 2)]
    require(transitions(source['states']) == expected, 'Original capture/release status sequence')
    audio = [e for e in source['audio_events'] if trigger < e[0] <= released]
    require(audio == [[trigger+1, 0x5c, 6, 5, 0x465d98], [jackpot, 0x84, 0, 45, 0],
                      [payout, 0x80, 0, 0, 0], [released, 0x5c, 6, 5, 0x465dbc]],
            'Original audio service sequence')

    args.output.mkdir(parents=True, exist_ok=True)
    native_trace, native_audio = args.output / 'native.json', args.output / 'audio.json'
    require(source['tick_count'] % 4 == 0, 'Tick count is not frame-aligned')
    cmd = [str(args.native.resolve()), 'space', str(ROOT / 'build/oracle/space-full-game'),
           str(GAME / 'DAT/SPACE.DAT'), '--frames', str(source['tick_count'] // 4),
           '--replay', str(SOURCE), '--diagnostic-shots', str(SOURCE), '--replay-only',
           '--presentation', '--windowed', '--audio', '--trace', str(native_trace),
           '--audio-trace', str(native_audio)]
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy',
               SDL_RENDER_DRIVER='software', XDG_DATA_HOME=str(args.output.resolve() / 'profile'),
               SLAM_TABLE_PROFILES=str(ROOT / 'analysis/table-profiles.json'))
    native_binary_sha256 = sha(args.native.resolve())
    subprocess.run(cmd, env=env, check=True)
    require(sha(args.native.resolve()) == native_binary_sha256, 'Native executable changed during replay')
    native = json.loads(native_trace.read_text())
    sound = json.loads(native_audio.read_text())
    require(native['tick_count'] == source['tick_count'], 'Native tick count')
    for key in KEYS:
        require(native[key] == source[key], 'Original/native vector differs: ' + key)
    require(sound['enabled'] and sound['queued_bytes'] > 0 and sound['events'] == corrected_audio_events(source['audio_events'], 'space'),
            'Native SDL queue or audio request sequence')
    require(transitions(native['states']) == expected, 'Native capture/release status sequence')

    def score(tick):
        return bytes(native['lifecycle'][tick-1][8:14]).hex()

    before, after_jackpot, after_prize = score(trigger), score(jackpot), score(payout)
    require(int(after_jackpot) - int(before) == 75500000, 'Native station + jackpot score')
    require(int(after_prize) - int(after_jackpot) == 5000000, 'Native station prize score')
    report = {'status': 'VERIFIED_BOUNDED', 'table': 'space',
              'original_build_sha256': source['build_sha256'], 'dat_sha256': source['dat_sha256'],
              'original_trace_sha256': sha(SOURCE), 'pinned_fixture_sha256': sha(PIN),
              'native_sha256': native_binary_sha256, 'whole_replay_ticks': source['tick_count'],
              'station_tick': trigger, 'jackpot_tick': jackpot, 'prize_tick': payout,
              'release_tick': released, 'ball_state_transitions': expected,
              'scores': {'before': before, 'after_jackpot': after_jackpot, 'after_prize': after_prize},
              'audio_events': audio, 'compared_vectors': list(KEYS),
              'scope': 'Original x86 capture/reset vs current native replay/reset; diagnostic station entry after earlier diagnostic contacts, no contact from entry through release. DMD memory and audio service requests exact; final original audio mix, physical listening and all roulette outcomes unverified.'}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS Space post-jackpot: capture, 75M, 5M, audio requests, release; original/native vectors exact')


if __name__ == '__main__':
    main()
