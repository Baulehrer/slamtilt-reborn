#!/usr/bin/env python3
"""Original discovery: earned campaign -> MagnaTable + Magnasaver -> finite game.

Frozen diagnostic prefix; subsequent diagnostic shots only reposition a genuine
free canonical ball. After the standalone outlane shot, keys only. No rule,
score, timer, phase, force, capture-state or callback writes.
"""
import json
import time
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EBX, UC_X86_REG_ESI
from pirate_adventure_oracle import ROOT, BUILD_SHA, DAT_SHA, digest
from pirate_mode_feedback_oracle import Feedback
from verify_pirate_multiball_campaign import integrity


def snapshot(m, tick, label, input_count, shot_count, force_count):
    """Recompute a sparse observation directly from the current original state."""
    g = m.get
    player = g(0x46b758)
    return dict(tick=tick, label=label, phase=g(0x46c6ac),
        phase_substate=g(0x46c61c), ball_state=g(0x46c1b4, 2),
        ball_substate=g(0x46c1b6, 2), ball_count=g(0x46c67c),
        ball_number=g(player+14, 2), extra_balls=g(player+16, 2),
        score_bcd=bytes(m.u.mem_read(player, 6)).hex(),
        highscore_hex=bytes(m.u.mem_read(0x46c542, 50)).hex(),
        x=g(0x46c15c), y=g(0x46c160), vx=g(0x46c170), vy=g(0x46c174),
        locks=g(0x46e2bc, 2), played_multiballs=g(0x46e2be, 2),
        magna_enabled=g(0x46e2dc, 2), magna_window=g(0x46e540, 2),
        magna_active=g(0x46e542, 2), magna_intro=g(0x4659b4),
        magna_selected=g(0x4659b8),
        magna_candidates=[g(0x46e240+i*4) for i in range(3)],
        mermaid=g(0x46e2d4),
        magna_magnets=[g(0x465864, 2), g(0x465858, 2)],
        capture_cooldown=g(0x465a68), capture_hold=g(0x465a6c),
        saver_earned=g(0x46e536, 2), saver_window=g(0x46e552, 2),
        saver_force=g(0x46584c, 2), force_applications=force_count,
        ms_earned=g(0x46e536, 2), ms_window=g(0x46e552, 2),
        ms_force=g(0x46584c, 2), ms_lamp=g(0x46e450, 1),
        tilt=g(0x46b764), pending_credits=g(player+16, 2),
        input_count=input_count, shot_count=shot_count,
        original_timing=m.timing(), ball_bytes=m.ball())


def main():
    started = time.monotonic()
    source_path = ROOT/'analysis/traces/pirate-final-campaign.json'
    f = json.loads(source_path.read_text())
    t = json.loads((ROOT/'build/oracle/pirate-modes/final-campaign/trace.json').read_text())
    assert integrity(t, f, BUILD_SHA, DAT_SHA) == 54760
    m = Feedback.fresh_original()
    m.run(0x40df1e, until=0x40df5f)
    g = m.get
    tick = 0
    inputs, shots, marks, forces, operations = [], [], [], [], []
    limit = 84760
    pending_force = None
    inputs_by_tick = {}
    for e in f['inputs']:
        inputs_by_tick.setdefault(e['tick'], []).append(e)
    shots_by_tick = {e['tick']: e for e in f['diagnostic_shots']}

    def force_before(u, pc, size, data):
        nonlocal pending_force
        if u.reg_read(UC_X86_REG_ESI) == 0x465848 and g(0x46584c, 2) == 65535:
            ball = u.reg_read(UC_X86_REG_EBX)
            pending_force = (ball, [g(ball+o) for o in [0, 4, 20, 24]])

    def force_after(u, pc, size, data):
        nonlocal pending_force
        if u.reg_read(UC_X86_REG_ESI) == 0x465848 and pending_force:
            ball, state = pending_force
            forces.append(dict(tick=tick+1, ball=hex(ball), before=state,
                               after_velocity=[g(ball+20), g(ball+24)]))
            pending_force = None

    def mark(label):
        row = snapshot(m, tick, label, len(inputs), len(shots), len(forces))
        marks.append(row)
        operations.append(dict(tick=tick, kind='mark', label=label, state=row))
        print(tick, label, 'phase', row['phase'], 'ball', row['ball_state'],
              'score', row['score_bcd'], flush=True)
        return row

    def step():
        nonlocal tick
        assert tick < limit, '30000-post-prefix hard step limit'
        m.dispatch_tick = tick+1
        m.step(tick)
        tick += 1

    def until(end):
        while tick < end:
            step()

    def wait(predicate, maximum=5000):
        start = tick
        while not predicate():
            step()
            assert tick-start < maximum, 'bounded wait failed'

    def key(action, down=True, scan=None):
        e = dict(tick=tick, action=action, down=down)
        if scan is not None:
            e['scan'] = scan
        inputs.append(e)
        operations.append(dict(kind='key', **e))
        if action == 'key':
            assert g(0x46c6ac) == 3 and g(0x46c61c) == 6
            m.run(0x405d54, scan)
        elif action == 'new_game':
            assert g(0x46c6ac) == 0
            m.run(0x408ae0, 1)
        else:
            m.run(0x40404c, 0 if down else 1,
                  dict(left=0x2a, right=0x36, enter=0x1c, special_left=0x1d)[action])

    def shot(label, layer, x, y):
        assert g(0x46c1b4, 2) == 2
        event = dict(tick=tick, label=label, layer=layer, x=x, y=y)
        shots.append(event)
        operations.append(dict(kind='shot', **event))
        m.shot(layer, x, y)
        step()
        return mark(label)

    def free():
        wait(lambda: g(0x46c1b4, 2) == 2)

    result = dict(schema=1, status='BOUNDED PROBE', build_sha256=BUILD_SHA,
        dat_sha256=DAT_SHA, prefix_case='final-campaign', prefix_steps=54760,
        prefix_fixture_sha256=digest(source_path.read_bytes()),
        postprefix_inputs=inputs, postprefix_diagnostic_shots=shots,
        milestones=marks, operations=operations, attempts=1, scope=__doc__)
    try:
        while tick < 54760:
            for e in inputs_by_tick.get(tick, []):
                m.run(0x40404c, 0 if e['down'] else 1,
                      dict(left=0x2a, right=0x36, enter=0x1c)[e['action']])
            if tick in shots_by_tick:
                e = shots_by_tick[tick]
                m.shot(e['layer'], e['x'], e['y'], e.get('ball', 0))
            step()
        assert m.ball() == t['states'][-1]
        for name, value in m.sample().items():
            assert value == t[name][-1], ('prefix endpoint', name)
        result['prefix_endpoint_all_nine_vectors_exact'] = True
        mark('retained_campaign_endpoint')
        m.u.hook_add(UC_HOOK_CODE, force_before, begin=0x40ada6, end=0x40ada6)
        m.u.hook_add(UC_HOOK_CODE, force_after, begin=0x40aeb9, end=0x40aeb9)
        # One genuinely earned Cave opens the still-unused MagnaTable admission.
        shot('cave_lock', 0, 43, 198)
        assert g(0x46c1b4, 2) == 3
        free(); mark('cave_released')
        shot('cave_return_lane', 2, 70, 340)
        wait(lambda: g(0x465a44) >= 0x80000000)
        shot('left_lane_arms_magna', 0, 34, 468)
        assert g(0x46e540, 2) == 400
        shot('top_trap_enters_magna', 0, 86, 10)
        wait(lambda: g(0x46e542, 2) != 0)
        mark('magna_initialized')
        key('left'); key('right')
        mark('magna_both_magnets_pressed')
        assert [g(0x465864, 2), g(0x465858, 2)] == [2, 2]
        free(); mark('magna_free_ball')
        key('right', False); step(); mark('magna_left_only')
        assert [g(0x465864, 2), g(0x465858, 2)] == [2, 0]
        key('left', False); key('right'); step(); mark('magna_right_only')
        assert [g(0x465864, 2), g(0x465858, 2)] == [0, 2]
        key('right', False); step(); mark('magna_both_released')
        selected = g(0x4659b8)
        award = g(0x46e240+selected*4)
        mark('magna_before_reward')
        shot('magna_reward_capture', 1, 120, 14)
        assert g(0x46c1b4, 2) == 3 and g(0x46c1b6, 2) == 6
        assert g(0x46e542, 2) == g(0x465864, 2) == g(0x465858, 2) == 0
        result['magna_award_id'] = award
        result['magna_selected_slot'] = selected
        free(); mark('magna_reward_released')
        shot('magna_return_lane', 2, 70, 340)
        # Paired material5 targets + real right trap earn standalone Magnasaver.
        shot('saver_left_target', 0, 92, 144)
        shot('saver_right_target', 0, 232, 141)
        assert g(0x46e53c, 2) == 65535
        shot('saver_right_trap_collect', 0, 302, 185)
        free(); mark('saver_earned')
        shot('saver_return_lane', 2, 70, 340)
        assert g(0x46e536, 2) == 65535
        activated = tick
        key('special_left'); key('special_left', False)
        mark('saver_activated')
        assert g(0x46584c, 2) == 65535 and g(0x46e552, 2) == 200
        shot('saver_actual_left_outlane', 0, 25, 530)
        result['last_diagnostic_shot_tick'] = tick-1
        until(activated+200)
        row = mark('saver_upward_motion_200steps')
        assert row['y'] < 530*65536 and forces
        assert any((v['after_velocity'][1] >= 0x80000000) for v in forces)
        wait(lambda: g(0x46584c, 2) == 0, 900)
        assert g(0x46e552, 2) == 65535
        mark('saver_original_expiry')
        until(activated+1000)
        key('left'); until(activated+1120); key('left', False)
        until(activated+1600); mark('saver_flipper_rescue_observed')
        letters = [0x1e, 0x30, 0x2e, 0x1c]
        admitted = False
        phase = g(0x46c6ac)
        mark('key_only_finite_continuation')
        while g(0x46c6ac) != 0:
            if g(0x46c6ac) == 1 and tick % 200 == 0:
                key('enter'); key('enter', False)
            if g(0x46c6ac) == 3 and g(0x46c61c) == 6:
                if not admitted:
                    mark('initials_admitted'); admitted = True
                if tick % 4 == 0 and letters:
                    key('key', scan=letters.pop(0))
            step()
            if g(0x46c6ac) != phase:
                phase = g(0x46c6ac)
                mark('phase_changed')
        assert admitted and not letters
        mark('game_over')
        frozen = m.ball()
        records = bytes(m.u.mem_read(0x46c542, 50))
        for _ in range(64):
            step()
            assert g(0x46c6ac) == 0 and m.ball() == frozen
        mark('game_over_stable64')
        key('new_game')
        assert bytes(m.u.mem_read(0x46c542, 50)) == records
        mark('new_game_retains_highscore')
        while not (g(0x46c6ac) == 2 and g(0x46c1b4, 2) == 2):
            if g(0x46c6ac) == 1 and tick % 200 == 0:
                key('enter'); key('enter', False)
            step()
        mark('next_game_free_ball')
        result['status'] = 'DISCOVERY SUCCESS'
    except Exception as error:
        result['status'] = 'BOUNDED INCOMPLETE'
        result['reason'] = repr(error)
        mark('bounded_stop')
    result.update(final_tick=tick, postprefix_steps=max(0, tick-54760),
        elapsed_seconds=round(time.monotonic()-started, 3),
        force_observations=dict(count=len(forces), first=forces[:1], last=forces[-1:]))
    (ROOT/'build/oracle/pirate-campaign-magnets-probe.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], tick, result.get('reason', ''), flush=True)


if __name__ == '__main__':
    main()
