#!/usr/bin/env python3
"""Legal-input repeated-game Original/reset/native/SDL equivalence."""
import argparse,json,os,subprocess
from pathlib import Path
from verify_pirate_modes import ROOT,read,sha,jsha
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity

CASES={'acceptance-nudge':5,'acceptance-tilt':7,'acceptance-multiball':8}
SCOPE=('Bounded legal-input repeated-game acceptance: Enter/Shift/LeftCtrl/Nudge, '
       'admitted ABC and F1 only; no waypoints or game-state injection. Two finite '
       'games then third free ball, original clock/RNG/highscores retained across F1. '
       'Original deterministic reset, native/reset and SDL; inherited x87 raster omission. '
       'Not an exhaustive legal-key-only all-mode campaign or physical-host acceptance.')


def contracts(t):
    assert not t['diagnostic_shots'] and t['scope']==SCOPE
    phases=[v[0]for v in t['lifecycle']]
    overs=[n+1 for n,v in enumerate(phases)if v==0 and (n==0 or phases[n-1]!=0)]
    restarts=[e['tick']for e in t['inputs']if e['action']=='new_game']
    assert len(overs)==len(restarts)==2,(t['case'],overs,restarts)
    assert all(r-o>=64 for o,r in zip(overs,restarts))
    for over,restart in zip(overs,restarts):
        assert all(t['states'][n]==t['states'][over]for n in range(over,restart+1))
        assert len(set(t['highscore_sha256'][over-1:restart+1]))==1
        assert phases[restart]==1
    end=t['source_steps']
    assert phases[end-1]==2 and int.from_bytes(bytes(t['states'][end][88:90]),'little')==2
    actions={e['action']for e in t['inputs']}
    assert actions<={'enter','key','new_game','left','right','nudge_left','nudge_right','nudge_up','special_left'}
    assert {'key','new_game'}<=actions
    if t['case']=='acceptance-nudge':assert {'nudge_left','nudge_right','nudge_up'}<=actions
    if t['case']=='acceptance-tilt':assert any(v[4] for v in t['magnasaver_state'])
    if t['case']=='acceptance-multiball':assert 4 in phases
    return dict(game_overs=overs,restarts=restarts,actions=sorted(actions))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe')
    p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview')
    p.add_argument('--original-only',action='store_true');a=p.parse_args()
    game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    dat=game/'DAT/PIRATE.DAT';prepared=ROOT/'build/oracle/pirate-full-tick'
    report=[]
    for case in CASES:
        path=ROOT/f'build/oracle/pirate-modes/{case}/trace.json';t=read(path)
        f=read(ROOT/f'analysis/traces/pirate-{case}.json')
        n=integrity(t,f,sha((game/'SLAMTILT.EXE').read_bytes()),sha(dat.read_bytes()))
        assert jsha(t['magnasaver_state'])==f['magnasaver_state_sha256']
        for k in ['scope','source_candidate_sha256','source_policy','source_steps']:assert t[k]==f[k]
        summary=contracts(t)
        if not a.original_only:
            native=path.parent/'native-verified.json';rendered=path.parent/'rendered-verified.json'
            subprocess.run([a.native,prepared,dat,native,str(n),'--full','--lamps','--replay',path,'--full-state-trace'],check=True)
            subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames',str(n//4),'--no-audio',
                '--replay',path,'--full-state-trace','--trace-output',rendered],check=True,
                env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
            for label,out in [('native/reset',read(native)),('SDL',read(rendered))]:
                assert out['tick_count']==n and not out.get('error','')
                for key in KEYS+['magnasaver_state']:assert out[key]==t[key],(case,label,key)
        report.append(dict(case=case,tick_count=n,**summary))
        print(case,n,'ORIGINAL VERIFIED'if a.original_only else'VERIFIED',flush=True)
    (ROOT/'build/oracle/pirate-acceptance-verification.json').write_text(json.dumps(dict(
        status='ORIGINAL VERIFIED'if a.original_only else'VERIFIED',cases=report,scope=SCOPE),indent=2)+'\n')


if __name__=='__main__':main()
