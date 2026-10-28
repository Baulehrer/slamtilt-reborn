#!/usr/bin/env python3
"""Four multiballs + six Adventures + finale -> natural finite game -> restart."""
import argparse
import json
import os
import subprocess
from pathlib import Path
from verify_pirate_modes import ROOT, read, sha
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity

CASE = 'campaign-finite'
PREFIX = 54760
ACTIONS = [
    dict(tick=tick, action='enter', down=down)
    for tick in [56400, 59200, 59400] for down in [True, False]
] + [dict(tick=tick, action='key', down=True, scan=scan)
     for tick, scan in [(62176, 0x1e), (62180, 0x30), (62184, 0x2e), (62188, 0x1c)]
] + [dict(tick=62704, action='new_game', down=True)
] + [dict(tick=62800, action='enter', down=down) for down in [True, False]]
SCOPE = ('Retained diagnostic four-multiball/six-Adventure/Treasure-Island prefix; '
         'after54760 only original Enter, admitted ABC/Enter and new-game actions. '
         'No post-prefix waypoints or rule/score/timer/completion injection. '
         'Integer full game state; inherited x87 render omission; not a legal-key-only whole campaign.')


def bookends(t):
    def mark(label):
        rows = [m for m in t['milestones'] if m['label'] == 'campaign_finite:'+label]
        assert len(rows) == 1, label
        return rows[0]
    start = mark('retained_endpoint')
    initials = mark('initials_admitted')
    over = mark('game_over')
    stable = mark('game_over_stable64')
    restart = mark('new_game_retains_highscore')
    free = mark('next_game_free_ball')
    assert start['tick'] == PREFIX and start['phase'] == 2
    assert initials['tick'] == 62176 and initials['phase'] == 3 and initials['phase_substate'] == 6
    assert over['tick'] == 62640 and over['phase'] == 0 and over['ball_count'] == 0
    assert over['score_bcd'] == '001486839210'
    assert over['highscore_hex'].startswith('00148683921041424300')
    assert stable['tick'] == restart['tick'] == 62704
    assert stable['phase'] == 0 and stable['score_bcd'] == over['score_bcd']
    assert restart['phase'] == 1 and restart['score_bcd'] == '000000000000'
    assert free['tick'] == 62910 and free['phase'] == 2 and free['ball_state'] == 2 and free['ball_count'] == 1
    assert free['score_bcd'] == '000000000000'
    assert all(row['highscore_hex'] == over['highscore_hex'] for row in [stable, restart, free])
    assert all(t['states'][tick] == t['states'][62640] for tick in range(62640, 62705))
    assert all(t['lifecycle'][tick-1][0] == 0 for tick in range(62640, 62705))
    assert [e for e in t['inputs'] if e['tick'] >= PREFIX] == ACTIONS
    assert not any(e['tick'] >= PREFIX for e in t['diagnostic_shots'])
    assert t['tick_count'] == 62992
    return dict(game_over_tick=62640, score=1486839210, initials='ABC',
                stable_steps=64, new_game_tick=62704, next_free_ball_tick=62910)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, default=ROOT/'build/native/pirate_session_probe')
    p.add_argument('--viewer', type=Path, default=ROOT/'build/native/slamview')
    p.add_argument('--original-only', action='store_true')
    args = p.parse_args()
    game = ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    dat = game/'DAT/PIRATE.DAT'
    prepared = ROOT/'build/oracle/pirate-full-tick'
    bsha, dsha = sha((game/'SLAMTILT.EXE').read_bytes()), sha(dat.read_bytes())
    folder = ROOT/'build/oracle/pirate-modes'/CASE
    path = folder/'trace.json'
    t = read(path)
    f = read(ROOT/f'analysis/traces/pirate-{CASE}.json')
    n = integrity(t, f, bsha, dsha)
    source_path = ROOT/'analysis/traces/pirate-final-campaign.json'
    source = read(ROOT/'build/oracle/pirate-modes/final-campaign/trace.json')
    sf = read(source_path)
    assert integrity(source, sf, bsha, dsha) == PREFIX
    for key in ['prefix_case', 'prefix_steps', 'prefix_fixture_sha256', 'continuation_inputs', 'continuation_diagnostic_shots', 'scope']:
        assert t[key] == f[key], key
    assert t['prefix_case'] == 'final-campaign' and t['prefix_steps'] == PREFIX
    assert t['prefix_fixture_sha256'] == sha(source_path.read_bytes())
    assert t['continuation_inputs'] == ACTIONS and t['continuation_diagnostic_shots'] == []
    assert t['scope'] == SCOPE
    for key in KEYS:
        count = PREFIX + (key == 'states')
        assert t[key][:count] == source[key], ('retained final campaign', key)
    for key in ['inputs', 'diagnostic_shots']:
        assert [e for e in t[key] if e['tick'] < PREFIX] == source[key], key
    assert t['milestones'][:len(source['milestones'])] == source['milestones']
    boundary = read(ROOT/'analysis/pirate-campaign-finite-boundary.json')
    assert boundary['cases'] == [CASE] and boundary['gameplay_stubs'] == []
    assert boundary['build_sha256'] == bsha and boundary['dat_sha256'] == dsha
    summary = bookends(t)
    if not args.original_only:
        native, rendered = folder/'native-verified.json', folder/'rendered-verified.json'
        subprocess.run([args.native, prepared, dat, native, str(n), '--full', '--lamps',
                        '--replay', path, '--diagnostic-shots', path], check=True)
        subprocess.run([args.viewer, dat, '--pirate-play', prepared, '--frames', str(n//4),
                        '--no-audio', '--replay', path, '--diagnostic-shots', path,
                        '--trace-output', rendered], check=True,
                       env=dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy'))
        for label, out in [('native/reset', read(native)), ('SDL', read(rendered))]:
            assert out['tick_count'] == n and out.get('error', '') == ''
            for key in KEYS:
                assert out[key] == t[key], (CASE, label, key)
    result = dict(status='ORIGINAL VERIFIED' if args.original_only else 'VERIFIED',
                  case=CASE, total_steps=n, prefix_steps=PREFIX,
                  continuation_steps=n-PREFIX, build_sha256=bsha, dat_sha256=dsha,
                  scope=SCOPE, **summary)
    (ROOT/'build/oracle/pirate-campaign-finite-verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print(CASE, n, result['status'], summary)


if __name__ == '__main__':
    main()
