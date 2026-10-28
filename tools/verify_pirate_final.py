#!/usr/bin/env python3
"""Verify earned Treasure Island against original/native/reset/SDL traces."""
import argparse
import json
import os
from pathlib import Path
import subprocess

from verify_pirate_modes import ROOT, read, sha, score
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import (
    contracts as campaign_contracts,
    frozen_prefix as campaign_frozen_prefix,
    integrity,
)


CASE = 'final-campaign'
PREFIX_CASE = 'multiball-campaign'
PREFIX_TICKS = 25780
ADVENTURES = [('knife', 5), ('plank', 0), ('sword', 1),
              ('dive', 2), ('monkey', 3), ('shark', 4)]
SCOPE = ('Integer-only original four-multiball prefix -> six actual Adventures -> '
         'Treasure Island; diagnostic canonical free-ball waypoints, real inputs, '
         'no rule/score/timer/capture/completion writes. Excludes post-prefix x87 '
         'render XY/visibility/sorting; not a legal-key-only full game.')


def frozen_prefix(trace, build_sha, dat_sha):
    prefix = read(ROOT / 'build/oracle/pirate-modes' / PREFIX_CASE / 'trace.json')
    fixture = read(ROOT / 'analysis/traces/pirate-multiball-campaign.json')
    assert integrity(prefix, fixture, build_sha, dat_sha) == PREFIX_TICKS
    for key in ['compactions', 'prefix_case', 'scope']:
        assert prefix[key] == fixture[key], ('retained prefix', key)
    campaign_frozen_prefix(prefix, build_sha, dat_sha)
    campaign_contracts(prefix)
    assert trace['prefix_case'] == PREFIX_CASE and trace['tick_count'] > PREFIX_TICKS
    for key in KEYS:
        count = PREFIX_TICKS + (key == 'states')
        assert trace[key][:count] == prefix[key], ('frozen multiball prefix', key)
    for key in ['inputs', 'diagnostic_shots']:
        assert [event for event in trace[key] if event['tick'] < PREFIX_TICKS] == prefix[key], key
    assert trace['milestones'][:len(prefix['milestones'])] == prefix['milestones']


def marker(trace):
    rows = trace['milestones']
    def get(label):
        found = [row for row in rows if row['label'] == label]
        assert len(found) == 1, (CASE, label, 'unique milestone')
        return found[0]
    return get


def adventure_contracts(mark):
    summaries = []
    previous_tick = PREFIX_TICKS
    completed = set()
    for ordinal, (name, mode) in enumerate(ADVENTURES, 1):
        prepare = mark(name + ':prepare')
        entered = mark(name + ':entered')
        returned = mark(name + ':normal_return')
        before_flags = [int(index in completed) for index in range(6)]
        completed.add(mode)
        after_flags = [int(index in completed) for index in range(6)]
        assert previous_tick <= prepare['tick'] < entered['tick'] <= returned['tick'], name
        assert prepare['phase'] == returned['phase'] == 2, name
        assert entered['phase'] == 5 and entered['adventure'] == mode, name
        assert prepare['played'] == before_flags, (name, 'earned prefix')
        assert entered['played'] == returned['played'] == after_flags, (name, 'played flag')
        assert all(row['played_multiballs'] == 4 for row in [prepare, entered, returned]), name
        assert returned['ball_count'] == 1 and returned['ball_states'] == [2], name
        if name == 'knife':
            result = mark('knife:video_result')
            assert entered['video'] == 1 and result['video'] == returned['video'] == 0
            assert entered['tick'] <= result['tick'] <= returned['tick']
        summaries.append(dict(adventure=name, adventure_id=mode, ordinal=ordinal,
            entered_tick=entered['tick'], returned_tick=returned['tick'],
            played_flags=after_flags))
        previous_tick = returned['tick']
    return summaries


def jackpot_event(before, after, ident, amount):
    flags = list(before['jackpot_flags'])
    assert 0 <= ident < 5 and flags[ident] == 1
    flags[ident] = 0
    assert after['jackpot_flags'] == flags, (after['label'], 'only hit target clears')
    assert after['jackpot'] == before['jackpot'] == amount
    assert after['collected'] == before['collected'] + amount
    assert after['aggregate'] == before['aggregate'] + amount
    assert after['last_award'] == amount and after['super_jackpot'] != 0
    assert after['phase'] == 4 and after['adventure'] == 6
    assert score(after) - score(before) >= amount


def super_event(before, after):
    amount = before['aggregate']
    assert before['super_jackpot'] != 0 and amount > 0
    assert after['collected'] == before['collected'] + amount
    assert after['aggregate'] == 0 and after['super_jackpot'] == 0
    assert after['last_award'] == amount and after['jackpot_flags'] == [1] * 5
    assert after['jackpot'] == before['jackpot']
    assert after['phase'] == 4 and after['adventure'] == 6
    assert score(after) - score(before) >= amount
    return amount


def final_event_contracts(trace, mark, released):
    labels = ['unarmed_trap_guard', 'other_ball_jackpot', 'guard_super_return',
        'first_jackpot_settled', 'duplicate_guard', 'before_growth', 'after_growth',
        'raised_jackpot_settled', 'super_jackpot_return',
        *['sweep_' + str(index) + '_settled' for index in range(5)],
        'all_targets_cleared', 'second_super_return']
    events = {name: mark('final:' + name) for name in labels}
    previous_tick = released['tick']
    for name in labels:
        row = events[name]
        assert previous_tick <= row['tick'], (name, 'event order')
        assert row['phase'] == 4 and row['adventure'] == 6, name
        assert row['played'] == [0] * 6 and row['played_multiballs'] == 0, name
        previous_tick = row['tick']

    unarmed = events['unarmed_trap_guard']
    assert unarmed['collected'] == unarmed['aggregate'] == 0
    assert unarmed['super_jackpot'] == 0 and unarmed['jackpot_flags'] == [1] * 5
    assert unarmed['jackpot'] == released['jackpot'] == 15000000
    other = events['other_ball_jackpot']
    jackpot_event(unarmed, other, 4, 15000000)
    assert any(unarmed['tick'] <= shot['tick'] < other['tick'] and shot.get('ball', 0) == 1
        for shot in trace['diagnostic_shots']), 'nonzero ball slot must perform the shot'
    guard_super = events['guard_super_return']
    assert super_event(other, guard_super) == 15000000
    assert guard_super['collected'] == 30000000

    first = events['first_jackpot_settled']
    duplicate = events['duplicate_guard']
    jackpot_event(guard_super, first, 4, 15000000)
    for key in ['jackpot', 'collected', 'aggregate', 'last_award',
                'super_jackpot', 'jackpot_flags']:
        assert duplicate[key] == first[key], ('duplicate target', key)
    before_growth, after_growth = events['before_growth'], events['after_growth']
    for key in ['jackpot', 'collected', 'aggregate', 'last_award',
                'super_jackpot', 'jackpot_flags']:
        assert before_growth[key] == duplicate[key], ('growth preparation', key)
    assert after_growth['jackpot'] == before_growth['jackpot'] + 1000000 == 16000000
    # This frozen capture/release interval also includes a target-0 jackpot.
    # The sampled transition does not identify its source ball or assign that
    # award to Cave itself; Cave's own rule changes the jackpot by +1M.
    growth_flags = list(before_growth['jackpot_flags'])
    assert growth_flags[0] == 1
    growth_flags[0] = 0
    assert after_growth['jackpot_flags'] == growth_flags
    assert after_growth['collected'] == before_growth['collected'] + 16000000 == 61000000
    assert after_growth['aggregate'] == before_growth['aggregate'] + 16000000 == 31000000
    assert after_growth['last_award'] == 16000000 and after_growth['super_jackpot'] != 0
    raised = events['raised_jackpot_settled']
    jackpot_event(after_growth, raised, 2, 16000000)
    assert raised['aggregate'] == 47000000 and raised['collected'] == 77000000
    first_super = events['super_jackpot_return']
    assert super_event(raised, first_super) == 47000000
    assert first_super['collected'] == 124000000

    previous = first_super
    for ident in range(5):
        after = events['sweep_' + str(ident) + '_settled']
        jackpot_event(previous, after, ident, 16000000)
        previous = after
    cleared = events['all_targets_cleared']
    assert cleared['jackpot_flags'] == [0] * 5
    assert cleared['aggregate'] == 80000000 and cleared['collected'] == 204000000
    for key in ['jackpot', 'collected', 'aggregate', 'last_award', 'super_jackpot']:
        assert cleared[key] == previous[key], ('completed target sweep', key)
    second_super = events['second_super_return']
    assert super_event(cleared, second_super) == 80000000
    assert second_super['collected'] == 284000000
    return dict(jackpot_growth=1000000, growth_interval_target_0_jackpot=16000000,
        first_super_jackpot=47000000,
        second_super_jackpot=80000000, guard_super_jackpot=15000000,
        collected=284000000, last_event_tick=second_super['tick'])


def next_cycle_contract(trace, mark, returned):
    prepare = mark('next_plank:prepare')
    entered = mark('next_plank:entered')
    end = mark('next_plank:normal_return')
    assert returned['tick'] <= prepare['tick'] < entered['tick'] <= end['tick']
    assert prepare['phase'] == end['phase'] == 2
    assert prepare['played'] == [0] * 6 and prepare['adventure'] == 0
    assert entered['phase'] == 5 and entered['adventure'] == 0
    assert entered['played'] == end['played'] == [1, 0, 0, 0, 0, 0]
    assert all(row['played_multiballs'] == 0 for row in [prepare, entered, end])
    assert end['ball_count'] == 1 and end['ball_states'] == [2]
    return dict(adventure='plank', entered_tick=entered['tick'], returned_tick=end['tick'])


def contracts(trace):
    mark = marker(trace)
    adventures = adventure_contracts(mark)
    ready = mark('final:earned_ready')
    entered = mark('final:entered')
    released = mark('final:all_balls_released')
    assert ready['phase'] == 2 and ready['played'] == [1] * 6
    assert ready['played_multiballs'] == 4 and ready['mode_gate'] != 0
    assert adventures[-1]['returned_tick'] <= ready['tick'] < entered['tick'] < released['tick']
    assert entered['phase'] == 4 and entered['adventure'] == 6
    assert entered['played'] == [0] * 6 and entered['played_multiballs'] == 0
    assert entered['jackpot'] == 15000000 and entered['collected'] == 0
    assert entered['aggregate'] == 0 and entered['super_jackpot'] == 0
    assert entered['jackpot_flags'] == [1] * 5
    assert entered['field_46e562'] == 1 and entered['pending_balls'] == 7
    assert released['phase'] == 4 and released['adventure'] == 6
    assert released['ball_count'] == 8 and released['ball_states'] == [2] * 8
    assert released['field_46e562'] == 3 and released['pending_balls'] == 0
    assert released['jackpot'] == 15000000 and released['aggregate'] == 0
    assert released['super_jackpot'] == 0 and released['jackpot_flags'] == [1] * 5
    events = final_event_contracts(trace, mark, released)
    returned = mark('final:normal_return')
    assert returned['tick'] > events['last_event_tick']
    assert returned['phase'] == 2 and returned['ball_count'] == 1
    assert returned['ball_states'] == [2] and returned['adventure'] == 0
    assert returned['played'] == [0] * 6 and returned['played_multiballs'] == 0
    assert returned['collected'] == events['collected'] + 16000000 == 300000000
    assert returned['aggregate'] == 16000000 and returned['super_jackpot'] == 65535
    compactions = trace['compactions']
    assert len(compactions) == 7 and all(event['stage'] == 'final' for event in compactions)
    assert {(event['old_count'], event['new_count']) for event in compactions} == {
        (count, count - 1) for count in range(2, 9)}
    for event in compactions:
        assert PREFIX_TICKS < entered['tick'] < event['tick'] <= returned['tick']
        assert event['index'] == 0
        assert event['new_count'] == event['old_count'] - 1
        assert event['source_sha256'] == event['destination_sha256']
        assert len(event['source_sha256']) == 64
        int(event['source_sha256'], 16)
    return dict(adventures=adventures, final_balls=8, compactions=len(compactions),
        entered_tick=entered['tick'], returned_tick=returned['tick'], final_events=events,
        return_collected=returned['collected'], return_aggregate=returned['aggregate'],
        next_cycle=next_cycle_contract(trace, mark, returned))


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
    folder = ROOT / 'build/oracle/pirate-modes' / CASE
    path = folder / 'trace.json'
    trace = read(path)
    fixture = read(ROOT / 'analysis/traces/pirate-final-campaign.json')
    count = integrity(trace, fixture, build_sha, dat_sha)
    for key in ['compactions', 'prefix_case', 'scope']:
        assert trace[key] == fixture[key], key
    assert trace['scope'] == SCOPE
    frozen_prefix(trace, build_sha, dat_sha)
    result = contracts(trace)
    native = folder / 'final-native-verified.json'
    rendered = folder / 'final-rendered-verified.json'
    screenshot = folder / 'final-native-verified.bmp'
    subprocess.run([args.native, prepared, dat, native, str(count), '--full', '--lamps',
        '--replay', path, '--diagnostic-shots', path], check=True)
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy')
    subprocess.run([args.viewer, dat, '--pirate-play', prepared, '--frames', str(count // 4),
        '--replay', path, '--diagnostic-shots', path, '--trace-output', rendered,
        '--capture', screenshot], env=env, check=True)
    for label, output in [('native/reset', native), ('SDL', rendered)]:
        actual = read(output)
        assert actual['tick_count'] == count and actual.get('error', '') == ''
        for key in KEYS:
            assert len(trace[key]) == len(actual[key]), (label, key, 'length')
            for tick, (original, value) in enumerate(zip(trace[key], actual[key])):
                assert original == value, (label, key, tick)
        print(label, count, 'steps exact, including complete eight-ball pool', flush=True)
    assert screenshot.read_bytes()[:2] == b'BM'
    report = dict(case=CASE, status='VERIFIED', tick_count=count,
        build_sha256=build_sha, dat_sha256=dat_sha, native_reset_sdl_exact=True,
        frozen_multiball_prefix_ticks=PREFIX_TICKS, ball_bytes=100,
        ball_pool_bytes=800, rule_bytes=864, video_bytes=892, gameplay_stubs=[],
        screenshot=str(screenshot.relative_to(ROOT)), scope=trace['scope'], **result)
    (ROOT / 'build/oracle/pirate-modes/final-verification.json').write_text(
        json.dumps(report, indent=2) + '\n')
    print('Four multiballs -> six Adventures -> Treasure Island PASS', flush=True)


if __name__ == '__main__':
    main()
