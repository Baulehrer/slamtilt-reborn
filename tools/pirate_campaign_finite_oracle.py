#!/usr/bin/env python3
"""Promote the discovered natural campaign ending to full original/reset fixture."""
import json
from collections import Counter
from pirate_legal_cave_oracle import Legal
from pirate_mode_feedback_oracle import Feedback
from pirate_adventure_oracle import ROOT, BUILD_SHA, DAT_SHA, compact, digest
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity
from verify_pirate_campaign_finite import CASE, PREFIX, ACTIONS, SCOPE, bookends


class Finite(Legal):
    @staticmethod
    def fresh_original():
        m = Feedback.fresh_original()
        m.run(0x40df1e, until=0x40df5f)
        return m

    def step(self):
        self.m.dispatch_tick = self.tick+1
        super().step()

    def mark(self, label):
        row = super().mark('campaign_finite:'+label)
        g = self.m.get
        row.update(phase_substate=g(0x46c61c), ball_number=g(g(0x46b758)+14, 2),
                   extra_balls=g(g(0x46b758)+16, 2))
        return row


def main():
    source_path = ROOT/'analysis/traces/pirate-final-campaign.json'
    source = json.loads((ROOT/'build/oracle/pirate-modes/final-campaign/trace.json').read_text())
    sf = json.loads(source_path.read_text())
    assert integrity(source, sf, BUILD_SHA, DAT_SHA) == PREFIX
    probe = json.loads((ROOT/'build/oracle/pirate-campaign-finite-probe.json').read_text())
    assert probe['status'] == 'DISCOVERY SUCCESS' and probe['continuation_inputs'] == ACTIONS
    assert probe['source_fixture_sha256'] == digest(source_path.read_bytes())
    r = Finite(0)
    keys = {}
    for event in source['inputs']:
        keys.setdefault(event['tick'], []).append(event)
    shots = {event['tick']: event for event in source['diagnostic_shots']}
    assert r.m.ball() == source['states'][0]
    while r.tick < PREFIX:
        for event in keys.get(r.tick, []):
            r.inputs.append(event)
            r.apply_input(r.m, event)
        if r.tick in shots:
            event = shots[r.tick]
            r.shots.append(event)
            r.m.shot(event['layer'], event['x'], event['y'], event.get('ball', 0))
        r.step()
        assert r.states[-1] == source['states'][r.tick], (r.tick, 'prefix ball')
        for key, actual in r.samples[-1].items():
            assert actual == source[key][r.tick-1], (r.tick, 'prefix', key)
    # Preserve every inherited event label and field without regenerating names.
    r.milestones = json.loads(json.dumps(source['milestones']))
    r.mark('retained_endpoint')
    actions = {}
    for event in ACTIONS:
        actions.setdefault(event['tick'], []).append(event)
    g = r.m.get
    frozen_ball = records = None
    while r.tick <= 62910:
        if r.tick == 62176:
            assert g(0x46c6ac) == 3 and g(0x46c61c) == 6
            r.mark('initials_admitted')
        if r.tick == 62640:
            assert g(0x46c6ac) == 0
            assert bytes(r.m.u.mem_read(g(0x46b758), 6)).hex() == '001486839210'
            frozen_ball = r.m.ball()
            records = bytes(r.m.u.mem_read(0x46c542, 50))
            assert records[:10].hex() == '00148683921041424300'
            r.mark('game_over')
        if 62640 <= r.tick <= 62704:
            assert g(0x46c6ac) == 0 and r.m.ball() == frozen_ball
        if r.tick == 62704:
            r.mark('game_over_stable64')
        for event in actions.get(r.tick, []):
            r.inputs.append(event)
            r.apply_input(r.m, event)
        if r.tick == 62704:
            assert bytes(r.m.u.mem_read(0x46c542, 50)) == records
            r.mark('new_game_retains_highscore')
        if r.tick == 62910:
            assert g(0x46c6ac) == 2 and g(0x46c1b4, 2) == 2
            assert bytes(r.m.u.mem_read(0x46c542, 50)) == records
            r.mark('next_game_free_ball')
            break
        r.step()
    trace = r.finish(CASE)
    metadata = dict(prefix_case='final-campaign', prefix_steps=PREFIX,
        prefix_fixture_sha256=digest(source_path.read_bytes()),
        continuation_inputs=ACTIONS, continuation_diagnostic_shots=[],
        call_edge_coverage='Full actual407c09 DMD dispatcher; other prefix edges inherited from byte-identical original trace; no broad call sweep.',
        scope=SCOPE)
    trace.update(metadata)
    bookends(trace)
    (ROOT/f'build/oracle/pirate-modes/{CASE}/trace.json').write_bytes(compact(trace)+b'\n')
    fixture_path = ROOT/f'analysis/traces/pirate-{CASE}.json'
    fixture = json.loads(fixture_path.read_text())
    fixture.update(metadata)
    fixture_path.write_text(json.dumps(fixture, indent=2)+'\n')
    # The only new observed dynamic consumer is407c09; preserve all inherited
    # non-DMD targets, without double-counting the prefix's DMD dispatches.
    edges = Counter()
    for edge in source['executed_call_edges']:
        if int(edge['callsite'], 16) != 0x407c09:
            edges[edge['callsite'], edge['target']] += edge['count']
    for edge in trace['executed_call_edges']:
        edges[edge['callsite'], edge['target']] += edge['count']
    boundary = dict(schema=1, build_sha256=BUILD_SHA, dat_sha256=DAT_SHA,
        cases=[CASE], gameplay_stubs=[], scope=SCOPE,
        call_edge_coverage=metadata['call_edge_coverage'],
        executed_call_edges=[dict(callsite=a, target=b, count=n)
                             for (a, b), n in sorted(edges.items())])
    (ROOT/'analysis/pirate-campaign-finite-boundary.json').write_text(json.dumps(boundary, indent=2)+'\n')
    print(CASE, trace['tick_count'], 'full original/reset9vectors exact; all prefix events retained')


if __name__ == '__main__':
    main()
