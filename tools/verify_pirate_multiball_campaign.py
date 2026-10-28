#!/usr/bin/env python3
"""Verify the original four-multiball campaign against native/reset/SDL."""
import argparse
import json
import os
from pathlib import Path
import subprocess

from verify_pirate_modes import ROOT, read, sha, jsha
from verify_pirate_multiball import KEYS, contract as crocodile_contract


STAGES = [('storm', 2), ('battle', 3), ('mutiny', 4)]
PREFIX_TICKS = 6400


def integrity(t, f, build_sha, dat_sha):
    count = t['tick_count']
    assert count == f['tick_count'] and count % 4 == 0
    assert t['gameplay_stubs'] == f['gameplay_stubs'] == []
    assert t['deterministic_original_replay'] and f['deterministic_original_replay']
    assert t['build_sha256'] == f['build_sha256'] == build_sha
    assert t['dat_sha256'] == f['dat_sha256'] == dat_sha
    for key in ['inputs', 'diagnostic_shots', 'milestones']:
        assert t[key] == f[key], key
    assert len(t['states']) == count + 1
    assert all(len(state) == 100 for state in t['states'])
    assert sha(bytes(v for state in t['states'] for v in state)) == f['states_sha256']
    for key in ['timing', 'lifecycle']:
        assert len(t[key]) == count and jsha(t[key]) == f[key + '_sha256'], key
    for key in KEYS[3:]:
        assert len(t[key]) == count, key
        assert sha(''.join(t[key]).encode()) == f[key.replace('_sha256', '_sequence_sha256')], key
    assert len({s['tick'] for s in t['diagnostic_shots']}) == len(t['diagnostic_shots'])
    assert all(0 <= s['tick'] < count for s in t['diagnostic_shots'])
    assert all(0 <= event['tick'] < count for event in t['inputs'])
    return count


def frozen_prefix(t, build_sha, dat_sha):
    prefix = read(ROOT / 'build/oracle/pirate-modes/crocodile/trace.json')
    fixture = read(ROOT / 'analysis/traces/pirate-crocodile.json')
    assert integrity(prefix, fixture, build_sha, dat_sha) == PREFIX_TICKS
    assert t['prefix_case'] == 'crocodile' and t['tick_count'] > PREFIX_TICKS
    for key in KEYS:
        count = PREFIX_TICKS + (key == 'states')
        assert t[key][:count] == prefix[key], ('frozen_crocodile_prefix', key)
    for key in ['inputs', 'diagnostic_shots']:
        assert [event for event in t[key] if event['tick'] < PREFIX_TICKS] == prefix[key], key
    assert t['milestones'][:len(prefix['milestones'])] == prefix['milestones']
    crocodile_contract('crocodile', prefix)


def expected_flags(before, ident):
    flags = list(before)
    flags[ident] = 0
    flags[(ident + 1) % 5] = 1
    return flags


def jackpot_event(before, after, ident, award):
    assert after['jackpot_flags'] == expected_flags(before['jackpot_flags'], ident), (
        after['label'], 'next-target flags')
    assert after['collected'] - before['collected'] == award, (after['label'], 'jackpot award')
    assert after['jackpot'] == before['jackpot'], (after['label'], 'jackpot value')


def contracts(t):
    marks = {row['label']: row for row in t['milestones']}
    summaries = []
    for name, ordinal in STAGES:
        def mark(label):
            qualified = name + ':' + label
            assert sum(row['label'] == qualified for row in t['milestones']) == 1, qualified
            return marks[qualified]

        expected_balls = ordinal + 1
        initial_jackpot = ordinal * 5000000
        prepare = mark('prepare')
        assert prepare['phase'] == 2 and prepare['played_multiballs'] == ordinal - 1
        assert prepare['locks'] == 0 and prepare['ball_count'] == 1
        for index in range(1, expected_balls + 1):
            released = mark(f'lock_{index}_released')
            assert released['locks'] == index and released['ball_count'] == 1
            assert released['played_multiballs'] == ordinal - 1 and released['ball_state'] == 2
        ready, ignored = mark('cannon_ready_intro'), mark('early_fire_ignored')
        fired, result = mark('cannon_fired'), mark('cannon_result')
        assert ready['phase'] == ignored['phase'] == 6 and fired['phase'] == 2
        assert ready['tick'] <= ignored['tick'] < fired['tick'] <= result['tick']
        assert not any(ready['tick'] <= shot['tick'] < result['tick']
                       for shot in t['diagnostic_shots']), (name, 'waypoint during cannon flight')
        entered = mark('mode_entered')
        for row in [result, entered]:
            assert row['phase'] == 4 and row['played_multiballs'] == ordinal
            assert row['locks'] == 0 and row['jackpot'] == initial_jackpot
        flags = [1, 0, 0, 0, 0] if ordinal == 2 else [1] * 5
        assert entered['jackpot_flags'] == flags
        released = mark('all_balls_released')
        assert released['phase'] == 4 and released['ball_count'] == expected_balls
        assert released['ball_states'] == [2] * expected_balls
        assert released['jackpot_flags'] == flags and released['jackpot'] == initial_jackpot
        before = released
        if ordinal == 2:
            unlit = mark('unlit_target_guard')
            jackpot_event(before, unlit, 2, 0)
            before = unlit
        first_id = 3 if ordinal == 2 else 0
        first, duplicate = mark('first_jackpot_settled'), mark('duplicate_guard')
        jackpot_event(before, first, first_id, initial_jackpot)
        jackpot_event(first, duplicate, first_id, 0)
        growth_before, growth_after = mark('before_growth'), mark('after_growth')
        assert growth_before['collected'] == duplicate['collected']
        assert growth_before['jackpot_flags'] == duplicate['jackpot_flags']
        assert growth_after['locks'] == 0
        assert growth_after['jackpot'] == growth_before['jackpot'] + 1000000
        assert growth_before['jackpot'] == initial_jackpot
        assert growth_after['collected'] == growth_before['collected']
        assert growth_after['jackpot_flags'] == growth_before['jackpot_flags']
        next_id = 4 if ordinal == 2 else 1
        raised = mark('raised_jackpot_awarded')
        jackpot_event(growth_after, raised, next_id, initial_jackpot + 1000000)
        before = raised
        for index in range(1, 6):
            after = mark(f'cycle_{index}_settled')
            jackpot_event(before, after, (next_id + index) % 5, initial_jackpot + 1000000)
            before = after
        complete = mark('cycle_complete')
        assert complete['collected'] == before['collected']
        assert complete['jackpot_flags'] == before['jackpot_flags']
        end = mark('normal_return')
        assert end['phase'] == 2 and end['ball_count'] == 1 and end['ball_states'] == [2]
        assert end['played_multiballs'] == ordinal and end['locks'] == 0
        compactions = [event for event in t['compactions'] if event['stage'] == name]
        assert compactions and any(event['index'] == 0 for event in compactions), (name, 'first-slot compaction')
        for event in compactions:
            assert prepare['tick'] < event['tick'] <= end['tick']
            assert 1 <= event['new_count'] == event['old_count'] - 1 < expected_balls
            assert 0 <= event['index'] < event['new_count']
            assert event['source_sha256'] == event['destination_sha256']
            assert len(event['source_sha256']) == 64
            int(event['source_sha256'], 16)
        transitions = {(event['old_count'], event['new_count']) for event in compactions}
        assert transitions == {(count, count - 1) for count in range(2, expected_balls + 1)}, (
            name, 'pool compaction down to one', transitions)
        summaries.append(dict(stage=name, ordinal=ordinal, balls=expected_balls,
            initial_jackpot=initial_jackpot, raised_jackpot=initial_jackpot + 1000000,
            cycle_awards=5, compactions=len(compactions), result=end))
    assert {event['stage'] for event in t['compactions']} == {name for name, _ in STAGES}
    return summaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', type=Path, default=ROOT / 'build/native/pirate_session_probe')
    parser.add_argument('--viewer', type=Path, default=ROOT / 'build/native/slamview')
    args = parser.parse_args()
    prepared = ROOT / 'build/oracle/pirate-full-tick'
    game = ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    dat = game / 'DAT/PIRATE.DAT'
    build_sha, dat_sha = sha((game / 'SLAMTILT.EXE').read_bytes()), sha(dat.read_bytes())
    context = read(ROOT / 'analysis/traces/pirate-complete-game.json')
    assert context['build_sha256'] == build_sha and context['dat_sha256'] == dat_sha
    for name, digest in context['context_hashes'].items():
        assert sha((prepared / name).read_bytes()) == digest, ('prepared context', name)
    folder = ROOT / 'build/oracle/pirate-modes/multiball-campaign'
    path = folder / 'trace.json'
    trace = read(path)
    fixture = read(ROOT / 'analysis/traces/pirate-multiball-campaign.json')
    count = integrity(trace, fixture, build_sha, dat_sha)
    for key in ['compactions', 'prefix_case', 'scope']:
        assert trace[key] == fixture[key], key
    frozen_prefix(trace, build_sha, dat_sha)
    stages = contracts(trace)
    native = folder / 'campaign-native-verified.json'
    rendered = folder / 'campaign-rendered-verified.json'
    screenshot = folder / 'campaign-native-verified.bmp'
    subprocess.run([args.native, prepared, dat, native, str(count), '--full', '--lamps',
        '--replay', path, '--diagnostic-shots', path], check=True)
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy')
    subprocess.run([args.viewer, dat, '--pirate-play', prepared, '--frames', str(count // 4),
        '--replay', path, '--diagnostic-shots', path, '--trace-output', rendered,
        '--capture', screenshot], env=env, check=True)
    for label, output in [('native/reset', native), ('SDL', rendered)]:
        result = read(output)
        assert result['tick_count'] == count and result.get('error', '') == ''
        for key in KEYS:
            assert len(trace[key]) == len(result[key]), (label, key, 'length')
            for tick, (original, actual) in enumerate(zip(trace[key], result[key])):
                assert original == actual, (label, key, tick)
        print(label, count, 'steps exact, including complete eight-ball pool', flush=True)
    assert screenshot.read_bytes()[:2] == b'BM'
    report = dict(case='multiball-campaign', status='VERIFIED', tick_count=count,
        build_sha256=build_sha, dat_sha256=dat_sha, native_reset_sdl_exact=True,
        frozen_crocodile_prefix_ticks=PREFIX_TICKS, stages=stages,
        stage_count=4, ball_bytes=100, ball_pool_bytes=800, rule_bytes=864,
        video_bytes=892, gameplay_stubs=[], screenshot=str(screenshot.relative_to(ROOT)),
        scope=trace['scope'])
    (ROOT / 'build/oracle/pirate-modes/multiball-campaign-verification.json').write_text(
        json.dumps(report, indent=2) + '\n')
    print('Crocodile -> Storm -> Battle -> Mutiny campaign PASS', flush=True)


if __name__ == '__main__':
    main()
