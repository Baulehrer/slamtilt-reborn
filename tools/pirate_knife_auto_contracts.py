"""Original automatic knives: legal left/right-only complete video win."""
from verify_pirate_modes import score

def contract(case,t):
    marks={m['label']:m for m in t['milestones']}
    start=marks['video_initialized'];active=marks['video_active'];end=marks['video_result']
    assert start['phase']==5 and start['ball_state']==3 and start['video']==1
    assert start['adventure']==5 and start['played']==[0,0,0,0,0,1]
    assert start['player_x']==48 and start['remaining']==24 and start['award_flag']==0
    assert active['intro']==364 and active['video']==1
    assert [marks[f'bumper_select_{i+1}']['adventure']for i in range(5)]==list(range(1,6))
    assert end['video']==0 and end['phase']==5 and end['ball_state']==3
    if case=='knife-auto-success':
        kills=[m for m in t['milestones']if m['label'].startswith('kill_')]
        assert len(kills)==25
        assert [k['remaining']for k in kills]==list(range(23,-1,-1))+[0xffffffff]
        assert [k['kill_score']for k in kills]==[3000000*i for i in range(1,26)]
        assert [k['spawn_period']for k in kills]==[100-3*i for i in range(1,26)]
        assert end['award_flag']==1 and end['kill_score']==75000000
        assert score(end)-score(active)==75000000
        actions=[e for e in t['inputs']if e['tick']>=active['tick']]
        assert all(any(e['action']==action and e['down']for e in actions)for action in ['left','right'])
        assert actions and all(e['action'] in ['left','right'] for e in actions), 'Automatic-only video must not receive Enter'
        assert min(k['player_x']for k in kills)<48<max(k['player_x']for k in kills)
        guard=marks['upper_trap_does_not_collect'];collected=marks['extra_ball_collected']
        assert guard['award_flag']==1 and guard['extra_credits']==0
        assert collected['award_flag']==0 and collected['extra_credits']==1
        assert collected['phase']==2 and collected['ball_state']==2
    else:
        assert end['award_flag']==0 and end['remaining']==24 and end['kill_score']==0
        assert score(end)==score(active)
        assert all(e['tick']<active['tick']for e in t['inputs'])
    returned=marks['normal_play_return']
    assert returned['phase']==2 and returned['ball_state']==2 and returned['video']==0 and returned['adventure']==0
    # No diagnostic coordinate change while the video simulation is active.
    assert not any(start['tick']<=s['tick']<returned['tick']for s in t['diagnostic_shots'])
    return returned
