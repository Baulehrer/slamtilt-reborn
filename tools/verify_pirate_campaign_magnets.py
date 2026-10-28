#!/usr/bin/env python3
"""Same-game fourMB/sixAdventure/final/MagnaTable/Magnasaver -> ABC/F1."""
import argparse,json,os,subprocess
from pathlib import Path
from verify_pirate_modes import ROOT,read,sha,jsha
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity

CASE='campaign-magnets'
SCOPE=('Unchanged54760-step diagnostic four-multiball/six-played-Adventure/TreasureIsland prefix; '
       'actual earned MagnaTable/reward and standalone Magnasaver/force/flipper return in same game. '
       'Only declared free-ball waypoints through55486, then keys only through ABC/GameOver/F1. '
       'No rule/phase/score/timer/force/capture-state/callback injection. Not a legal-key-only whole campaign; inherited x87 raster omission.')


def contracts(t):
    def m(label):
        rows=[v for v in t['milestones']if v['label']==label]
        assert len(rows)==1,label
        return rows[0]
    init=m('magna_initialized');assert init['tick']==55057
    assert init['magna_enabled']==0 and init['magna_active']==65535 and init['magna_window']==65535
    assert m('magna_both_magnets_pressed')['magna_magnets']==[2,2]
    assert m('magna_left_only')['magna_magnets']==[2,0]
    assert m('magna_right_only')['magna_magnets']==[0,2]
    before=m('magna_before_reward');reward=m('magna_reward_capture');released=m('magna_reward_released')
    assert before['magna_candidates'][before['magna_selected']]==9
    assert reward['mermaid']-before['mermaid']==3000000
    assert reward['score_bcd']==before['score_bcd']
    assert reward['ball_state']==3 and reward['ball_substate']==6 and reward['capture_hold']==150
    assert reward['magna_active']==0 and reward['magna_magnets']==[0,0]
    assert released['ball_state']==2 and released['capture_cooldown']==10
    armed=m('saver_earned');active=m('saver_activated');expired=m('saver_original_expiry')
    assert armed['ms_earned']==65535 and active['tick']==55486
    assert active['ms_earned']==0 and active['ms_force']==65535 and active['ms_window']==200
    assert expired['tick']==56288 and expired['ms_force']==0 and expired['ms_window']==65535
    assert expired['tick']==(active['tick']//4+201)*4
    up=m('saver_upward_motion_200steps');assert up['y']<417*65536 and up['force_applications']==200
    assert t['force_observations']['count']==802
    assert t['force_observations']['first'][0]['tick']==55487
    assert t['force_observations']['last'][0]['tick']==56288
    returned=m('saver_flipper_rescue_observed');assert returned['tick']==57086
    assert returned['ball_state']==2 and returned['phase']==2 and returned['tilt']==0
    # Actual post-expiry left-flipper return, not merely a free final sample.
    assert all(int.from_bytes(bytes(s[88:90]),'little')==2 for s in t['states'][55487:57087])
    assert min(int.from_bytes(bytes(s[4:8]),'little',signed=True)for s in t['states'][56487:57087])<400*65536
    assert t['last_diagnostic_shot_tick']==55486
    assert not any(s['tick']>55486 for s in t['diagnostic_shots'])
    assert [(e['tick'],e['down'])for e in t['postprefix_inputs']if e['action']=='left'and 56000<=e['tick']<57500]==[(56486,True),(56606,False)]
    initials=m('initials_admitted');over=m('game_over');stable=m('game_over_stable64')
    restart=m('new_game_retains_highscore');free=m('next_game_free_ball')
    assert initials['tick']==64576 and initials['phase']==3 and initials['phase_substate']==6
    assert over['tick']==65040 and over['phase']==0 and over['score_bcd']=='001498782380'
    assert over['highscore_hex'].startswith('00149878238041424300')
    assert stable['tick']==restart['tick']==65104 and restart['phase']==1
    assert restart['score_bcd']==free['score_bcd']=='000000000000'
    assert free['tick']==65310 and free['phase']==2 and free['ball_state']==2
    assert all(v['highscore_hex']==over['highscore_hex']for v in [stable,restart,free])
    assert all(t['states'][n]==t['states'][65040]for n in range(65040,65105))
    assert all(t['lifecycle'][n-1][0]==0 for n in range(65040,65105))
    assert t['tick_count']==65392
    assert len(t['magnasaver_state'])==65392 and all(len(v)==5 for v in t['magnasaver_state'])
    assert t['magnasaver_state'][55486][:3]==[0,200,65535]
    assert t['magnasaver_state'][56287][:3]==[0,65535,0]
    return dict(game_over=65040,score=1498782380,initials='ABC',new_game=65104,next_free_ball=65310,
        magna_reward_id=9,mermaid_bank_increment=3000000,saver_force_steps=802,last_waypoint=55486)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native',type=Path,default=ROOT/'build/native/pirate_session_probe')
    p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamview')
    p.add_argument('--original-only',action='store_true');a=p.parse_args()
    game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    dat=game/'DAT/PIRATE.DAT';prepared=ROOT/'build/oracle/pirate-full-tick'
    bsha,dsha=sha((game/'SLAMTILT.EXE').read_bytes()),sha(dat.read_bytes())
    folder=ROOT/f'build/oracle/pirate-modes/{CASE}';path=folder/'trace.json'
    t=read(path);f=read(ROOT/f'analysis/traces/pirate-{CASE}.json');n=integrity(t,f,bsha,dsha)
    assert jsha(t['magnasaver_state'])==f['magnasaver_state_sha256']
    for key in ['prefix_case','prefix_steps','prefix_fixture_sha256','postprefix_inputs',
            'postprefix_diagnostic_shots','last_diagnostic_shot_tick','force_observations','scope']:
        assert t[key]==f[key],key
    source_path=ROOT/'analysis/traces/pirate-final-campaign.json';source=read(ROOT/'build/oracle/pirate-modes/final-campaign/trace.json')
    assert integrity(source,read(source_path),bsha,dsha)==54760
    assert t['prefix_fixture_sha256']==sha(source_path.read_bytes()) and t['scope']==SCOPE
    for key in KEYS:
        count=54760+(key=='states');assert t[key][:count]==source[key],('retained prefix',key)
    for key,post in [('inputs','postprefix_inputs'),('diagnostic_shots','postprefix_diagnostic_shots')]:
        assert [e for e in t[key]if e['tick']<54760]==source[key]
        assert [e for e in t[key]if e['tick']>=54760]==t[post]
    assert t['milestones'][:len(source['milestones'])]==source['milestones']
    b=read(ROOT/'analysis/pirate-campaign-magnets-boundary.json');assert b['cases']==[CASE]and not b['gameplay_stubs']
    summary=contracts(t)
    if not a.original_only:
        native=folder/'native-verified.json';rendered=folder/'rendered-verified.json'
        subprocess.run([a.native,prepared,dat,native,str(n),'--full','--lamps','--replay',path,'--diagnostic-shots',path],check=True)
        subprocess.run([a.viewer,dat,'--pirate-play',prepared,'--frames',str(n//4),'--no-audio',
            '--replay',path,'--diagnostic-shots',path,'--trace-output',rendered],check=True,
            env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
        for label,out in [('native/reset',read(native)),('SDL',read(rendered))]:
            assert out['tick_count']==n and out.get('error','')==''
            for key in KEYS+['magnasaver_state']:assert out[key]==t[key],(CASE,label,key)
    report=dict(status='ORIGINAL VERIFIED'if a.original_only else'VERIFIED',case=CASE,total_steps=n,
        prefix_steps=54760,postprefix_steps=n-54760,key_only_tail_steps=n-55487,
        build_sha256=bsha,dat_sha256=dsha,scope=SCOPE,**summary)
    (ROOT/'build/oracle/pirate-campaign-magnets-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(CASE,n,report['status'],summary)


if __name__=='__main__':main()
