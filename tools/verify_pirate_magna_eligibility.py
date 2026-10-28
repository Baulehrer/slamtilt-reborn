#!/usr/bin/env python3
"""Original earned eligibility -> native/reset/SDL fallback reward chains."""
import argparse,json,os,subprocess
from pathlib import Path
from verify_pirate_modes import ROOT,read,sha,score
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity
CASES=['magna-mode-lit','magna-bonus-held','magna-kickback-lit','magna-all-played']

def candidate(raw,row):
    if raw<1:return 0
    if raw<3:return 1
    if raw<15 and row['mode_lit']==0 and 0 in row['played']:return 2
    if raw<30:return 3
    if raw<40 and row['bonus_hold']==0:return 4
    if raw<55:return 5
    if raw<65:return 6
    if raw<75:return 7
    if raw<90:return 8
    if raw<100:return 9
    if raw<110 and row['kickback']==0:return 10
    return 11

def contracts(case,t):
    def mark(label):
        rows=[x for x in t['milestones']if x['label']==label];assert len(rows)==1,(case,label)
        return rows[0]
    for row in t['milestones']:
        if row['label'].endswith(':initialized'):
            assert row['candidates']==[candidate(v,row)for v in row['raw_candidates']],(case,row['label'],'selection')
    init=mark('fallback:initialized');before=mark('fallback:before_award');after=mark('fallback:award_applied');end=mark('fallback:normal_return')
    slot=before['selected'];raw=init['raw_candidates'][slot];wanted=init['candidates'][slot]
    assert init['active']==before['active']==65535 and init['phase']==2
    assert after['active']==end['active']==0 and after['capture']==6 and after['ball_state']==3
    assert after['magnets']==end['magnets']==[0,0]and end['phase']==2 and end['ball_state']==2
    if case in ('magna-mode-lit','magna-all-played'):
        assert 3<=raw<15 and wanted==3
        if case=='magna-mode-lit':assert init['mode_lit']==65535 and 0 in init['played']
        else:
            assert init['mode_lit']==0 and init['played']==[1]*6
            prefix=mark('earned_prefix:all_six_played');assert prefix['tick']==t['prefix_ticks']==48328
    else:
        reward=4 if case=='magna-bonus-held' else 10
        earned=mark('earned:before_award');applied=mark('earned:award_applied')
        assert earned['candidates'][earned['selected']]==reward
        returned=mark('reenable:normal_return');lock=mark('reenable:new_first_lock_released')
        assert returned['phase']==2 and returned['ball_count']==1 and returned['locks']==0 and returned['played_multiballs']==1
        assert lock['locks']==1 and lock['enabled']==65535
        key='bonus_hold'if reward==4 else'kickback'
        assert applied[key]==init[key]==(65535 if reward==4 else 1)
        assert (30<=raw<40 and wanted==5)if reward==4 else(100<=raw<110 and wanted==11)
    amount={3:20000000,5:10000000,11:5000000}[wanted]
    assert score(after)-score(before)==amount
    for key in ['bonus_hold','mode_lit','kickback','extra_credits','extra_ball_lit','locks']:
        assert after[key]==before[key],(case,'fallback changed eligibility',key)
    held={'left':False,'right':False}
    for e in t['inputs']:
        if e['action']in held:
            assert held[e['action']]!=e['down'],(case,'redundant edge',e)
            held[e['action']]=e['down']
    return dict(case=case,ticks=t['tick_count'],raw=raw,slot=slot,actual_reward=wanted,amount=amount,
        mode_lit=init['mode_lit'],played=init['played'],bonus_hold=init['bonus_hold'],kickback=init['kickback'])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe')
    p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview');a=p.parse_args()
    prepared=ROOT/'build/oracle/pirate-full-tick';game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    dat=game/'DAT/PIRATE.DAT';build_sha,dat_sha=sha((game/'SLAMTILT.EXE').read_bytes()),sha(dat.read_bytes())
    reports=[];env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
    for case in CASES:
        folder=ROOT/'build/oracle/pirate-modes'/case;path=folder/'trace.json';t=read(path);f=read(ROOT/f'analysis/traces/pirate-{case}.json')
        n=integrity(t,f,build_sha,dat_sha);assert t['scope']==f['scope']and t['prefix_ticks']==f['prefix_ticks']
        report=contracts(case,t)
        if t['prefix_ticks']:
            prefix=read(ROOT/'build/oracle/pirate-modes/final-campaign/trace.json');count=t['prefix_ticks']
            for key in KEYS:assert t[key][:count+(key=='states')]==prefix[key][:count+(key=='states')],key
            for key in ['inputs','diagnostic_shots']:
                assert[e for e in t[key]if e['tick']<count]==[e for e in prefix[key]if e['tick']<count],key
        native=folder/'native-verified.json';rendered=folder/'rendered-verified.json';capture=folder/'verified.bmp'
        subprocess.run([a.native,prepared,dat,native,str(n),'--full','--lamps','--replay',path,'--diagnostic-shots',path],check=True)
        subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames',str(n//4),'--replay',path,'--diagnostic-shots',path,'--trace-output',rendered,'--capture',capture],env=env,check=True)
        for name,file in [('native/reset',native),('SDL',rendered)]:
            actual=read(file);assert actual['tick_count']==n and actual.get('error','')==''
            for key in KEYS:assert actual[key]==t[key],(case,name,key)
        assert capture.read_bytes()[:2]==b'BM'
        reports.append(report);print(case,n,'original/native/reset/SDL exact',flush=True)
    (ROOT/'build/oracle/pirate-modes/magna-eligibility-verification.json').write_text(json.dumps(dict(
        status='VERIFIED bounded earned-state eligibility/fallback',cases=reports,tick_count=sum(x['ticks']for x in reports)),indent=2)+'\n')
if __name__=='__main__':main()
