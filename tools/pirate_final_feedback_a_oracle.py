#!/usr/bin/env python3
"""Remaining Pirate threshold and left-Ctrl feature feedback, original execution.

Only explicit free-ball diagnostic positions and original keyboard events drive
play. Original40df1e..40df59 installs default configurable keyboard bindings.
No rule, score, timer, phase, priority, capture or callback writes are injected.
"""
import argparse
from collections import Counter
import json
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from pirate_legal_feedback_oracle import callsite
from pirate_mode_feedback_oracle import Feedback
from pirate_adventure_oracle import ROOT, BUILD_SHA, compact

CASES = ['final-feedback-threshold', 'final-feedback-left-feature']
PRODUCERS = {
    0x436832: 'ordinary_ramp_count_increment',
    0x43534a: 'earned_extra_ball_threshold_doubled',
    0x435366: 'earned_extra_ball_pending_increment',
    0x4396f8: 'paired_material5_targets_pending',
    0x4372da: 'right_trap_arms_left_feature',
    0x43420a: 'left_ctrl_consumes_earned_feature',
    0x434215: 'left_ctrl_enables_magnet_record',
    0x4355ef: 'left_feature_expiry_disables_magnet',
}
SCOPE = ('Original full clock and actual407c09 feedback dispatch; explicit free-ball '
         'diagnostic waypoints on real DAT triggers, original default key bindings '
         'and legal left Ctrl; no rule/score/timer/phase/priority/callback injection; '
         'not a legal-key-only full-table trajectory.')


class RemainingFeedback(Feedback):
    @staticmethod
    def fresh_original():
        m = Feedback.fresh_original()
        # Actual original default-keymap branch. Only configurable input bindings
        # 46c5dc..46c5f0 change: Shift/Ctrl/Alt left and right respectively.
        m.run(0x40df1e, until=0x40df5f)
        def special_entered(u, address, size, data):
            ret = m.get(u.reg_read(UC_X86_REG_ESP))
            observed = callsite(m, ret)
            m.calls[int(observed['callsite'], 16), address] += 1
        m.u.hook_add(UC_HOOK_CODE, special_entered, begin=0x4341dc, end=0x4341dc)
        return m

    @staticmethod
    def apply_input(m, event):
        scan = 0x1d if event['action'] == 'special_left' else {
            'enter': 0x1c, 'left': 0x2a, 'right': 0x36}[event['action']]
        m.run(0x40404c, 0 if event['down'] else 1, scan)

    def __init__(self):
        super().__init__(0)
        self.events = []
        self.producer_events = []
        for address, label in PRODUCERS.items():
            def observed(u, pc, size, data, label=label):
                self.producer_events.append(dict(tick=self.tick + 1,
                    instruction=hex(pc), event=label))
            self.m.u.hook_add(UC_HOOK_CODE, observed, begin=address, end=address)

    def initial(self):
        while self.tick < 600:
            if self.tick in (200, 201):
                event = dict(tick=self.tick, action='enter', down=self.tick == 200)
                self.inputs.append(event)
                self.apply_input(self.m, event)
            self.step()
        self.mark('normal_play_started')
        self.idle()

    def key(self, action, down):
        event = dict(tick=self.tick, action=action, down=down)
        self.inputs.append(event)
        self.apply_input(self.m, event)

    def mark(self, label):
        row = super().mark(label)
        g = self.m.get
        row.update(ordinary_ramp_count=g(g(0x46b758) + 12, 2),
            extra_ball_threshold=g(0x46e2da, 2), pending_extra_ball=g(0x46e2d8, 2),
            left_target=g(0x46e2cf, 1), right_target=g(0x46e2d0, 1),
            pending_paired_targets=g(0x46e53c, 2), earned_left_feature=g(0x46e536, 2),
            left_feature_window=g(0x46e552, 2), left_feature_lamp=g(0x46e450, 1),
            left_feature_magnet=g(0x46584c, 2))
        return row


def generate(case):
    r = RemainingFeedback()
    r.initial()
    g = r.m.get
    if case == 'final-feedback-threshold':
        for index in range(25):
            r.ramp('skull_ramp_' + str(index + 1), 1)
        assert g(g(0x46b758) + 12, 2) == 24
        assert g(0x46e2da, 2) == 25 and g(0x46e2d8, 2) == 0
        r.admit('twenty_fifth_ordinary_ramp_earns_extra_ball', 0x42c42c,
            lambda: r.ramp('threshold_earning_skull_ramp', 1))
        assert g(0x46e2da, 2) == 50 and g(0x46e2d8, 2) == 1
        r.mark('threshold_doubled_and_extra_ball_pending')
    else:
        r.shot('left_material5_target', 0, 92, 144)
        assert g(0x46e2cf, 1) == 1
        r.shot('right_material5_target', 0, 232, 141)
        assert g(0x46e53c, 2) == 65535
        r.ramp('right_trap_collects_paired_targets', 0)
        r.shot('return_lane', 2, 70, 340)
        assert g(0x46e536, 2) == 65535
        r.mark('paired_targets_earned_left_ctrl_feature')
        def activate():
            r.key('special_left', True)
            r.step()
            r.key('special_left', False)
            r.mark('left_ctrl_activated_earned_feature')
        r.admit('left_ctrl_activates_target_pair_earned_feature', 0x42e41c, activate)
        assert g(0x46e536, 2) == 0
        while g(0x46e552, 2) != 65535:
            r.park()
        assert g(0x46584c, 2) == 0 and g(0x46e450, 1) == 0
        r.mark('left_feature_window_expired_magnet_off')
    trace = r.finish(case)
    extra = dict(feedback_events=r.events, producer_events=r.producer_events,
        keyboard_defaults=dict(original_prefix='0x40df1e..0x40df5f',
            special_left_scan=0x1d, special_right_scan=0x9d), scope=SCOPE)
    trace.update(extra)
    (ROOT/'build/oracle/pirate-modes'/case/'trace.json').write_bytes(compact(trace) + b'\n')
    path = ROOT/'analysis/traces'/('pirate-' + case + '.json')
    fixture = json.loads(path.read_text())
    fixture.update(extra)
    path.write_text(json.dumps(fixture, indent=2) + '\n')
    return trace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', nargs='+', choices=CASES, default=CASES)
    args = parser.parse_args()
    for case in args.cases:
        generate(case)
    edges = Counter()
    included = []
    evidence = []
    for case in CASES:
        path = ROOT/'build/oracle/pirate-modes'/case/'trace.json'
        if not path.exists():
            continue
        trace = json.loads(path.read_text())
        assert trace['build_sha256'] == BUILD_SHA
        included.append(case)
        evidence.append(dict(case=case, tick_count=trace['tick_count'],
            deterministic_original_replay=trace['deterministic_original_replay'],
            feedback_events=trace['feedback_events'], producer_events=trace['producer_events'],
            feature_milestones=[row for row in trace['milestones'] if row['label'] in
                ['paired_targets_earned_left_ctrl_feature', 'left_ctrl_activated_earned_feature',
                 'left_feature_window_expired_magnet_off']]))
        for edge in trace['executed_call_edges']:
            edges[edge['callsite'], edge['target']] += edge['count']
    (ROOT/'analysis/pirate-final-feedback-a-boundary.json').write_text(json.dumps(dict(
        schema=1, build_sha256=BUILD_SHA, cases=included, gameplay_stubs=[], scope=SCOPE,
        executed_call_edges=[dict(callsite=a, target=b, count=n)
            for (a, b), n in sorted(edges.items())]), indent=2) + '\n')
    (ROOT/'analysis/pirate-final-feedback-a-evidence.json').write_text(json.dumps(dict(
        schema=1, status='Original execution and independent original reset replay VERIFIED; native pending',
        build_sha256=BUILD_SHA, cases=evidence,
        static_chain=dict(threshold='436832 increments player+0c;43531c guard threshold25;43534a doubles;435366 increments pending;435384 requests42c42c',
            paired_targets='material5 left/right439164/4391de;43969c sets46e53c;right-trap431c9c invokes437294;4372da arms46e536',
            input='original default40df28/40df42 binds leftCtrl1d to46c5e4;404a7c/404ab4 dispatch descriptor+4c4341dc;43420a consumes46e536;434242 requests42e41c'),
        input_admission=dict(left='404a7c:scan==46c5e4;EAX0keydown;46b764==0;clear menu;404ab4 calls descriptor+4c4341dc;4341e0 requires46e536!=0',
            release='No special callback on keyup; original handler has no special-key held latch',
            right='scan9d;404af7 descriptor+50=46e514→434264 ret, no-op',
            semantics='Standalone left feature/Magnasaver by manual correspondence; not PiranhaPops pair46e2c8/c9 and reward46e2ca'),
        scope=SCOPE), indent=2) + '\n')


if __name__ == '__main__':
    main()
