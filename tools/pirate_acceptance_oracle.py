#!/usr/bin/env python3
"""Original/reset proof of frozen native legal-input repeated-game candidates."""
import json
from pirate_campaign_magnets_oracle import Combined
from pirate_adventure_oracle import ROOT, compact, digest
from verify_pirate_acceptance import CASES, SCOPE, contracts


def main():
    for case,index in CASES.items():
        source_path=ROOT/f'build/oracle/pirate-acceptance-sweep/policy-{index}.json'
        source=json.loads(source_path.read_text())
        assert not source['diagnostic_shots'] and source['result']['status']=='TWO_FINITE_GAMES'
        r=Combined();events={};marks={}
        for e in source['inputs']:events.setdefault(e['tick'],[]).append(e)
        for m in source['result']['milestones']:marks.setdefault(m['tick'],[]).append(m)
        while r.tick<source['tick_count']:
            for e in events.get(r.tick,[]):r.inputs.append(e);r.apply_input(r.m,e)
            r.step()
            for expected in marks.get(r.tick,[]):
                # Pre-step restart/initials markers share this tick but describe
                # the state after inputs; validate them through event contracts.
                if expected['label'] not in ('phase_change','game_over','third_game_free_ball'):continue
                m=r.mark(expected['label'])
                assert m['phase']==expected['phase'],(case,r.tick,'phase')
                assert r.m.get(0x46c67c)==expected['ball_count'],(case,r.tick,'pool')
        t=r.finish(case)
        t.update(scope=SCOPE,source_candidate_sha256=digest(source_path.read_bytes()),
                 source_policy=source['policy'],source_steps=source['tick_count'])
        contracts(t)
        (ROOT/f'build/oracle/pirate-modes/{case}/trace.json').write_bytes(compact(t)+b'\n')
        path=ROOT/f'analysis/traces/pirate-{case}.json';f=json.loads(path.read_text())
        f.pop('magnasaver_state')
        f.update({k:t[k]for k in ['scope','source_candidate_sha256','source_policy','source_steps']},
                 magnasaver_state_sha256=digest(compact(t['magnasaver_state'])))
        path.write_text(json.dumps(f,indent=2)+'\n')
        print(case,t['tick_count'],'original/reset exact',flush=True)


if __name__=='__main__':main()
