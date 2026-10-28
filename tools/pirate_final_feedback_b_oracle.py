#!/usr/bin/env python3
"""Original bonus multiplier and used-kickback displays from actual DAT events.

Diagnostic waypoints reposition only a canonical FREE ball. No gameplay,
priority, phase, callback, score or timer writes. Each case independently replays
its frozen action schedule from reset through Recorder.finish.
"""
import argparse
from collections import Counter
import json

from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP

from pirate_mode_feedback_oracle import Feedback
from pirate_adventure_oracle import ROOT, BUILD_SHA, DAT_SHA, compact, digest


CASES = {'multiplier': 0x42c03c, 'kickback': 0x42e5bc}
SCOPE = ('Canonical original reset, actual Enter edges and explicit FREE-ball DAT '
         'waypoints; actual407c09 dispatch, independent original replay of all9 '
         'Recorder vectors; no rule/score/timer/capture/phase/priority/callback '
         'writes. Not a legal-key-only trajectory; existing integer-render cut.')


class FinalFeedbackB(Feedback):
    def __init__(self):
        super().__init__(0)
        self.events = []
        self.entries = []
        self.registrations = []
        self.hooks = []
        for address in CASES.values():
            self.hooks.append(self.m.u.hook_add(
                UC_HOOK_CODE, self.entered, begin=address, end=address))
        for address in [0x437247, 0x4378af]:
            self.hooks.append(self.m.u.hook_add(
                UC_HOOK_CODE, self.registered, begin=address, end=address))
        self.m.u.ctl_remove_cache(0x400000, 0x452000)

    def entered(self, u, address, size, _):
        self.entries.append(dict(tick=self.tick + 1, target=hex(address),
                                 return_address=hex(self.m.get(u.reg_read(UC_X86_REG_ESP)))))

    def registered(self, u, address, size, _):
        self.registrations.append(dict(tick=self.tick + 1, address=hex(address),
                                       **self.fields()))

    def fields(self):
        g = self.m.get
        return dict(multiplier=g(g(0x46b758) + 18, 2),
                    multiplier_lit=g(0x46e54e, 2), skull_progress=g(0x46e526, 2),
                    mermaid_targets=list(self.m.u.mem_read(0x46e2cc, 3)),
                    kickback=g(0x46e534, 2), phase=g(0x46c6ac),
                    ball_motion=g(0x46c1b8, 2), ball_state=g(0x46c1b4, 2))

    def mark(self, label):
        row = super().mark(label)
        row.update(self.fields())
        return row

    def initial(self):
        while self.tick < 600:
            if self.tick in (200, 201):
                event = dict(tick=self.tick, action='enter', down=self.tick == 200)
                self.apply_input(self.m, event)
                self.inputs.append(event)
            self.step()
        assert self.m.get(0x46c6ac) == 2
        self.mark('normal_start')
        self.idle()


def generate(case):
    r = FinalFeedbackB()
    r.initial()
    g = r.m.get
    target = CASES[case]
    if case == 'multiplier':
        assert g(g(0x46b758) + 18, 2) == 1
        # Two real Skull-ramp events reach the original progress threshold.
        for n in range(2):
            r.ramp('skull_' + str(n + 1), 4)
            r.free()
            r.idle()
        assert g(0x46e54e, 2) == 0xffff
        r.mark('multiplier_armed')
        r.admit('bonus_multiplier_1_to_2', target,
                lambda: r.ramp('right_trap_collect', 0))
        assert g(g(0x46b758) + 18, 2) == 2 and g(0x46e54e, 2) == 0
        meaning = 'Earned bonus multiplier1->2 collected in the right ball-trap'
    else:
        assert g(0x46e534, 2) == 0
        for label, x, y in [('mermaid_left', 60, 321),
                             ('mermaid_right', 96, 305),
                             ('mermaid_middle', 85, 315)]:
            r.shot(label, 0, x, y)
            r.idle()
        assert g(0x46e534, 2) == 1
        r.mark('kickback_armed')
        r.admit('armed_right_outlane_kickback_used', target,
                lambda: r.shot('right_outlane', 0, 307, 560))
        assert g(0x46e534, 2) == 0
        meaning = 'Mermaid-target-earned right sidelane kickback used and consumed'
    r.mark('event_complete')
    name = 'final-feedback-' + case
    trace = r.finish(name)
    entries = [row for row in r.entries if row['target'] == hex(target)]
    assert len(entries) == r.events[0]['dispatch_count'] > 0
    assert len(r.registrations) == 1
    assert all(row['return_address'] == '0x407c0f' for row in entries)
    trace.update(scope=SCOPE, feedback_events=r.events,
                 target_entries=entries, registrations=r.registrations,
                 proven_meaning=meaning)
    folder = ROOT / 'build/oracle/pirate-modes' / name
    (folder / 'trace.json').write_bytes(compact(trace) + b'\n')
    path = ROOT / 'analysis/traces' / ('pirate-' + name + '.json')
    fixture = json.loads(path.read_text())
    fixture.update(scope=SCOPE, feedback_events=r.events,
                   registrations=r.registrations, proven_meaning=meaning,
                   target_entries_sha256=digest(compact(entries)),
                   target_entry_samples=[entries[0], entries[-1]])
    path.write_text(json.dumps(fixture, indent=2) + '\n')
    print('VERIFIED', name, r.tick, r.events, flush=True)
    return trace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', nargs='+', choices=list(CASES), default=list(CASES))
    args = parser.parse_args()
    for case in args.cases:
        generate(case)
    edges = Counter()
    rows = []
    for case, target in CASES.items():
        name = 'final-feedback-' + case
        path = ROOT / 'build/oracle/pirate-modes' / name / 'trace.json'
        if not path.exists():
            continue
        trace = json.loads(path.read_text())
        assert trace['build_sha256'] == BUILD_SHA
        rows.append(dict(case=name, steps=trace['tick_count'], target=hex(target),
                         feedback_events=trace['feedback_events'],
                         proven_meaning=trace['proven_meaning'],
                         deterministic_original_replay=trace['deterministic_original_replay']))
        for edge in trace['executed_call_edges']:
            edges[edge['callsite'], edge['target']] += edge['count']
    common = dict(schema=1, build_sha256=BUILD_SHA, dat_sha256=DAT_SHA,
                  status='VERIFIED original dispatch and reset replay; native integration pending',
                  cases=[row['case'] for row in rows], fixtures=rows,
                  gameplay_stubs=[], scope=SCOPE)
    boundary = dict(common, executed_call_edges=[
        dict(callsite=a, target=b, count=n) for (a, b), n in sorted(edges.items())])
    (ROOT / 'analysis/pirate-final-feedback-b-boundary.json').write_text(
        json.dumps(boundary, indent=2) + '\n')
    evidence = dict(common, semantics={
        '0x42c03c': '437c34 Skull ramp twice arms46e54e; actual right capture '
                    '431ca1->4371e8 consumes it, player+12 WORD1->2, '
                    '437247..437263 registers42c03c outside phase5.',
        '0x42e5bc': 'Three actual Mermaid contacts4392fb/439370/4394a5 call439704 '
                    'and arm46e534. Actual right outlane437800->4378af registers '
                    '42e5bc after434994;437903 consumes kickback1->0. '
                    'This is a right sidelane event, not an upper-trap event.'},
        observation='Concrete target hooks return to407c0f, matching actual407c09 '
                    'dispatch count. Broad indirect-call tracking disabled.',
        serious_failed_attempts=dict(multiplier=0, kickback=0))
    (ROOT / 'analysis/pirate-final-feedback-b-evidence.json').write_text(
        json.dumps(evidence, indent=2) + '\n')


if __name__ == '__main__':
    main()
