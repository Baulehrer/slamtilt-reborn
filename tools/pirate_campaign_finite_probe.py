#!/usr/bin/env python3
"""Bounded natural finite-game continuation after retained final-campaign prefix.

Discovery only. Existing prefix includes documented diagnostic waypoints; after
its endpoint only original keys are used, with no further state writes/shots.
"""
import json
import time
from pirate_adventure_oracle import ROOT, BUILD_SHA, DAT_SHA, digest
from pirate_mode_feedback_oracle import Feedback
from verify_pirate_multiball_campaign import integrity


def main():
    started = time.monotonic()
    deadline = started + 60
    game = ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    source = ROOT/'analysis/traces/pirate-final-campaign.json'
    fixture = json.loads(source.read_text())
    trace = json.loads((ROOT/'build/oracle/pirate-modes/final-campaign/trace.json').read_text())
    integrity(trace, fixture, BUILD_SHA, DAT_SHA)
    m = Feedback.fresh_original()
    m.run(0x40df1e, until=0x40df5f)
    g = m.get
    tick = 0
    end = fixture['tick_count']
    assert end == 54760
    limit = end + 30000
    events = []
    milestones = []
    letters = [0x1e, 0x30, 0x2e, 0x1c]

    def mark(label):
        player = g(0x46b758)
        row = dict(tick=tick, label=label, phase=g(0x46c6ac),
            phase_substate=g(0x46c61c), ball_state=g(0x46c1b4, 2),
            ball_substate=g(0x46c1b6, 2), ball_count=g(0x46c67c),
            ball_number=g(player+14, 2), extra_balls=g(player+16, 2),
            score_bcd=bytes(m.u.mem_read(player, 6)).hex(),
            highscore_hex=bytes(m.u.mem_read(0x46c542, 50)).hex(),
            x=g(0x46c15c), y=g(0x46c160))
        milestones.append(row)
        print(tick, label, 'phase', row['phase'], 'ball', row['ball_number'],
              'score', row['score_bcd'], flush=True)
        return row

    def step():
        nonlocal tick
        if tick >= limit or time.monotonic() >= deadline:
            raise TimeoutError('hard continuation bound reached')
        m.step(tick)
        tick += 1

    def event(action, down=True, scan=None):
        events.append(dict(tick=tick, action=action, down=down,
                           **({} if scan is None else dict(scan=scan))))
        if action == 'key':
            assert g(0x46c6ac) == 3 and g(0x46c61c) == 6
            m.run(0x405d54, scan)
        elif action == 'new_game':
            assert g(0x46c6ac) == 0
            m.run(0x408ae0, 1)
        else:
            m.run(0x40404c, 0 if down else 1,
                  {'enter': 0x1c, 'left': 0x2a, 'right': 0x36}[action])

    inputs = {}
    for e in fixture['inputs']:
        inputs.setdefault(e['tick'], []).append(e)
    shots = {e['tick']: e for e in fixture['diagnostic_shots']}
    endpoint_exact = False
    result = dict(schema=1, status='BOUNDED PROBE', build_sha256=BUILD_SHA,
        dat_sha256=DAT_SHA, source_fixture_sha256=digest(source.read_bytes()),
        prefix_steps=end, continuation_limit_steps=30000,
        continuation_diagnostic_shots=[], continuation_inputs=events,
        milestones=milestones,
        scope='Original discovery after unchanged retained diagnostic final-campaign prefix. Post-prefix only Enter, admitted initials, F1; no new free-ball waypoints or game-state writes. No native/reset proof claimed.')
    try:
        while tick < end:
            for e in inputs.get(tick, []):
                m.run(0x40404c, 0 if e['down'] else 1,
                      {'enter': 0x1c, 'left': 0x2a, 'right': 0x36}[e['action']])
            if tick in shots:
                e = shots[tick]
                m.shot(e['layer'], e['x'], e['y'], e.get('ball', 0))
            step()
        sample = m.sample()
        assert m.ball() == trace['states'][-1]
        assert sample['timing'] == trace['timing'][-1]
        assert sample['lifecycle'] == trace['lifecycle'][-1]
        endpoint_exact = True
        mark('retained_endpoint_exact')
        phase = g(0x46c6ac)
        while g(0x46c6ac) != 0:
            if g(0x46c6ac) == 1 and tick % 200 == 0:
                event('enter'); event('enter', False)
            if g(0x46c6ac) == 3 and g(0x46c61c) == 6:
                if len(letters) == 4:
                    mark('initials_admitted')
                if tick % 4 == 0 and letters:
                    event('key', scan=letters.pop(0))
            step()
            if g(0x46c6ac) != phase:
                phase = g(0x46c6ac)
                mark('phase_changed')
        mark('game_over')
        frozen = m.ball()
        records = bytes(m.u.mem_read(0x46c542, 50))
        for _ in range(64):
            step()
            assert g(0x46c6ac) == 0 and m.ball() == frozen
        mark('game_over_stable64')
        event('new_game')
        assert bytes(m.u.mem_read(0x46c542, 50)) == records
        mark('new_game_retains_highscore')
        while not (g(0x46c6ac) == 2 and g(0x46c1b4, 2) == 2):
            if g(0x46c6ac) == 1 and tick % 200 == 0:
                event('enter'); event('enter', False)
            step()
        mark('next_game_free_ball')
        result['status'] = 'DISCOVERY SUCCESS'
        result['initials_completed'] = not letters
    except Exception as error:
        result['status'] = 'BOUNDED INCOMPLETE'
        result['reason'] = repr(error)
        mark('bounded_stop')
    result.update(endpoint_ball_timing_lifecycle_exact=endpoint_exact,
                  final_tick=tick, continuation_steps=max(0, tick-end),
                  elapsed_seconds=round(time.monotonic()-started, 3))
    (ROOT/'build/oracle/pirate-campaign-finite-probe.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], tick, 'elapsed', result['elapsed_seconds'], flush=True)


if __name__ == '__main__':
    main()
