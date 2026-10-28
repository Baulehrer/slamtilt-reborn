#!/usr/bin/env python3
"""Promote same-game MagnaTable/Magnasaver discovery to original/reset proof."""
import json
from collections import Counter
from pirate_adventure_oracle import ROOT,BUILD_SHA,DAT_SHA,compact,digest
from pirate_legal_cave_oracle import Legal
from pirate_magnasaver_oracle import Magnasaver
from pirate_campaign_magnets_probe import snapshot
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity
from verify_pirate_campaign_magnets import CASE,SCOPE,contracts


class Combined(Magnasaver):
    @staticmethod
    def apply_input(m,e):
        if e['action']in ['key','new_game']:return Legal.apply_input(m,e)
        return Magnasaver.apply_input(m,e)


def main():
    path=ROOT/'build/oracle/pirate-campaign-magnets-probe.json'
    probe=json.loads(path.read_text());assert probe['status']=='DISCOVERY SUCCESS'
    prefix_path=ROOT/'analysis/traces/pirate-final-campaign.json'
    f=json.loads(prefix_path.read_text())
    source=json.loads((ROOT/'build/oracle/pirate-modes/final-campaign/trace.json').read_text())
    assert integrity(source,f,BUILD_SHA,DAT_SHA)==54760
    assert probe['prefix_fixture_sha256']==digest(prefix_path.read_bytes())
    r=Combined();keys={};shots={s['tick']:s for s in source['diagnostic_shots']}
    for e in source['inputs']:keys.setdefault(e['tick'],[]).append(e)
    while r.tick<54760:
        for e in keys.get(r.tick,[]):r.inputs.append(e);r.apply_input(r.m,e)
        if r.tick in shots:
            s=shots[r.tick];r.shots.append(s);r.m.shot(s['layer'],s['x'],s['y'],s.get('ball',0))
        r.step()
        assert r.states[-1]==source['states'][r.tick],('prefix ball',r.tick)
        for key in KEYS[1:]:assert r.samples[-1][key]==source[key][r.tick-1],('prefix',r.tick,key)
    r.milestones=json.loads(json.dumps(source['milestones']))
    prefix_inputs,prefix_shots=len(r.inputs),len(r.shots)
    for op in probe['operations']:
        assert op['tick']>=r.tick
        while r.tick<op['tick']:r.step()
        if op['kind']=='key':
            e={k:v for k,v in op.items()if k!='kind'}
            r.inputs.append(e);r.apply_input(r.m,e)
        elif op['kind']=='shot':
            e={k:v for k,v in op.items()if k!='kind'}
            r.shots.append(e);r.m.shot(e['layer'],e['x'],e['y'],e.get('ball',0))
        else:
            assert op['kind']=='mark'
            row=snapshot(r.m,r.tick,op['label'],len(r.inputs)-prefix_inputs,
                len(r.shots)-prefix_shots,len(r.force_applications))
            assert row==op['state'],('fresh observation',op['label'],r.tick)
            r.milestones.append(row)
    assert r.tick==probe['final_tick']==65310
    force=dict(count=len(r.force_applications),first=r.force_applications[:1],last=r.force_applications[-1:])
    assert force==probe['force_observations']
    trace=r.finish(CASE)
    meta=dict(prefix_case='final-campaign',prefix_steps=54760,
        prefix_fixture_sha256=digest(prefix_path.read_bytes()),probe_sha256=digest(path.read_bytes()),
        postprefix_inputs=probe['postprefix_inputs'],postprefix_diagnostic_shots=probe['postprefix_diagnostic_shots'],
        last_diagnostic_shot_tick=probe['last_diagnostic_shot_tick'],force_observations=force,scope=SCOPE)
    trace.update(meta);contracts(trace)
    (ROOT/f'build/oracle/pirate-modes/{CASE}/trace.json').write_bytes(compact(trace)+b'\n')
    public_path=ROOT/f'analysis/traces/pirate-{CASE}.json';public=json.loads(public_path.read_text())
    public.pop('magnasaver_state')
    public.update(meta,magnasaver_state_sha256=digest(compact(trace['magnasaver_state'])))
    public_path.write_text(json.dumps(public,indent=2)+'\n')
    edges=Counter()
    for e in source['executed_call_edges']:
        if int(e['callsite'],16)!=0x407c09:edges[e['callsite'],e['target']]+=e['count']
    for e in trace['executed_call_edges']:edges[e['callsite'],e['target']]+=e['count']
    (ROOT/'analysis/pirate-campaign-magnets-boundary.json').write_text(json.dumps(dict(
        schema=1,build_sha256=BUILD_SHA,dat_sha256=DAT_SHA,cases=[CASE],gameplay_stubs=[],
        executed_call_edges=[dict(callsite=a,target=b,count=n)for(a,b),n in sorted(edges.items())],
        scope=SCOPE),indent=2)+'\n')
    print(CASE,trace['tick_count'],'original/freshreset10vectors exact;2magnet systems+finite ending')


if __name__=='__main__':main()
