#!/usr/bin/env python3
"""Pin original MagnaTable contracts and compare native/reset/SDL at every step."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from verify_pirate_multiball_campaign import integrity
from verify_pirate_multiball import KEYS
from verify_pirate_modes import ROOT,read,sha
from pirate_magna_cases import CASES,SCOPE,AWARDS


def score(mark):
    return int(mark['score_bcd'])


def contract(case,t):
    rows=t['milestones'];marks={row['label']:row for row in rows}
    held={'left':False,'right':False}
    for event in t['inputs']:
        action=event['action']
        if action in held:
            assert event['down']!=held[action],(case,'redundant key edge',event)
            held[action]=event['down']
    def mark(label):
        assert sum(row['label']==label for row in rows)==1,(case,label)
        return marks[label]
    no_lock=mark('no_lock_guard');enabled=mark('enabled_by_lock');armed=mark('armed')
    assert no_lock['locks']==0 and no_lock['window']==65535 and no_lock['active']==0
    assert enabled['locks']==1 and enabled['enabled']==65535 and enabled['active']==0
    assert armed['window']==400 and armed['active']==0 and armed['phase']==2
    assert all(row['phase']==2 for row in [no_lock,enabled,armed])
    if case=='magna-expired':
        expired=mark('window_expired');returned=mark('expired_normal_return')
        assert expired['window']==65535 and expired['active']==0 and expired['enabled']==65535
        assert returned['active']==0 and returned['phase']==2 and returned['ball_state']==2
        assert not any('initialized'==row['label']for row in rows)
        return dict(case=case,ticks=t['tick_count'],outcome='expired admission rejected')
    init=mark('initialized');released=mark('field_released')
    assert init['phase']==2 and init['active']==65535 and init['enabled']==0
    assert init['window']==65535 and init['intro']==575 and init['selected']==0
    assert all(0<=value<=11 for value in init['candidates'])
    assert released['ball_state']==2 and released['active']==65535 and released['intro']==0xffffffff
    assert released['candidates']==init['candidates']
    if case=='magna-idle':
        assert released['tick']-init['tick']>=575*4
        assert not any(e['tick']>=init['tick']for e in t['inputs'])
    else:
        both=mark('both_pressed')
        assert both['magnets']==[2,2] and both['held']==[0xffffffff]*2
        if case.startswith('magna-natural-'):
            flight=mark('magnet_flight');off=mark('flight_keys_released')
            expected=[2,0] if case.endswith('left') else [2,2]
            assert flight['magnets']==expected and flight['active']==65535 and flight['ball_state']==2
            assert flight['tick']-released['tick']==1800 and score(flight)==score(released)
            assert off['magnets']==[0,0]
            top=mark('top_trap')
            assert not any(top['tick']<=shot['tick']<flight['tick']for shot in t['diagnostic_shots'])
        else:
            left=mark('left_only');right=mark('right_only');off=mark('both_released')
            assert left['magnets']==[2,0] and right['magnets']==[0,2] and off['magnets']==[0,0]
            assert all(row['active']==65535 for row in [both,left,right,off])
        assert released['tick']-init['tick']<575*4
    returned=mark('normal_return')
    assert returned['phase']==2 and returned['active']==0 and returned['ball_state']==2
    assert returned['ball_count']==1 and returned['magnets']==[0,0]
    if case in ('magna-idle','magna-escape') or case.startswith('magna-natural-'):
        exit=mark('exit_no_award')
        assert exit['active']==0 and exit['ball_state']==7 and exit['magnets']==[0,0]
        assert score(exit)==score(released)
        for key in ['extra_credits','extra_ball_lit','bonus_hold','mermaid','mode_lit','locks','kickback']:
            assert exit[key]==released[key],(case,key)
        # After entry all movement/escape is real simulation except the declared free-ball exit waypoint.
        return dict(case=case,ticks=t['tick_count'],outcome='no award, real animation return')
    before=mark('before_award');after=mark('award_applied')
    award=int(case.rsplit('-',1)[1]) if case.startswith('magna-award-') else None
    slot=AWARDS[award][1] if award is not None else int(case[-1])
    assert before['selected']==slot and before['active']==65535
    ident=before['candidates'][slot]
    if award is not None:assert ident==award
    assert after['ball_state']==3 and after['capture']==6 and after['active']==0
    assert after['magnets']==[0,0] and after['capture_wait']==150
    assert returned['x']==120*65536 and returned['y']==14*65536
    # 433b2a clears both; the rest of the same original step adds +640 Y.
    assert returned['vx']==0 and returned['vy']==640
    expected={3:20000000,5:10000000,11:5000000}.get(ident,0)
    assert score(after)-score(before)==expected,(case,ident,'score award')
    if ident==0:assert after['extra_credits']==before['extra_credits']+1
    elif ident==1:assert after['extra_ball_lit']==before['extra_ball_lit']+1
    elif ident==2:assert after['mode_lit']==65535
    elif ident==4:assert after['bonus_hold']==65535
    elif ident==6:assert after['field_46e554'] in (999,1000)
    elif ident==7:assert after['locks']==5
    elif ident in (8,9):assert after['mermaid']-before['mermaid']=={8:2000000,9:3000000}[ident]
    elif ident==10:assert after['kickback']==1
    return dict(case=case,ticks=t['tick_count'],outcome='award and normal return',slot=slot,award_id=ident,score_award=expected)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe')
    parser.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview')
    parser.add_argument('--cases',nargs='+',choices=CASES,default=CASES)
    args=parser.parse_args();reports=[]
    prepared=ROOT/'build/oracle/pirate-full-tick'
    game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    dat=game/'DAT/PIRATE.DAT';build_sha,dat_sha=sha((game/'SLAMTILT.EXE').read_bytes()),sha(dat.read_bytes())
    context=read(ROOT/'analysis/traces/pirate-complete-game.json')
    assert context['build_sha256']==build_sha and context['dat_sha256']==dat_sha
    for name,digest in context['context_hashes'].items():assert sha((prepared/name).read_bytes())==digest,name
    env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
    for case in args.cases:
        folder=ROOT/'build/oracle/pirate-modes'/case;path=folder/'trace.json';t=read(path)
        fixture=read(ROOT/f'analysis/traces/pirate-{case}.json')
        count=integrity(t,fixture,build_sha,dat_sha)
        assert t['scope']==fixture['scope']==SCOPE
        result=contract(case,t)
        native=folder/'native-verified.json';rendered=folder/'rendered-verified.json';capture=folder/'native-verified.bmp'
        subprocess.run([args.native,prepared,dat,native,str(count),'--full','--lamps','--replay',path,'--diagnostic-shots',path],check=True)
        subprocess.run([args.viewer,dat,'--pirate-play',prepared,'--frames',str(count//4),'--replay',path,
            '--diagnostic-shots',path,'--trace-output',rendered,'--capture',capture],env=env,check=True)
        for label,output in [('native/reset',native),('SDL',rendered)]:
            actual=read(output)
            assert actual['tick_count']==count and actual.get('error','')==''
            for key in KEYS:assert actual[key]==t[key],(case,label,key)
        assert capture.read_bytes()[:2]==b'BM'
        result.update(status='VERIFIED',native_reset_sdl_exact=True)
        reports.append(result);print(case,count,'original/native/reset/SDL exact',flush=True)
    report=dict(build_sha256=build_sha,dat_sha256=dat_sha,scope=SCOPE,cases=reports,
        tick_count=sum(row['ticks']for row in reports),ball_pool_bytes=800,rule_bytes=864,video_bytes=892,
        gameplay_stubs=[])
    if args.cases==CASES:
        assert {row['award_id']for row in reports if 'award_id'in row}==set(range(12))
        report.update(award_ids=list(range(12)),natural_key_only_flight_steps=2*1800)
    (ROOT/'build/oracle/pirate-modes/magna-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('MagnaTable PASS',flush=True)


if __name__=='__main__':main()
