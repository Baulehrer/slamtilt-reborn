"""Earned cap12 multiplier -> physical drain -> original score payouts/new ball."""
def contracts(t):
    marks={m['label']:m for m in t['milestones']}
    before=marks['before_cap12_drain'];drain=marks['bonus_entered'];after=marks['next_ball_ready']
    assert before['tick']==8524 and before['multiplier']==12 and before['bonus_base']==20700000
    assert drain['phase']==3 and drain['multiplier']==12 and drain['bonus_base']==before['bonus_base']
    assert drain['score_number']==before['score_number']==20000000
    calls=t['bonus_score_calls'];assert [r['amount']for r in calls]==[7000000,248400000]
    assert calls[1]['amount']==before['bonus_base']*before['multiplier']
    assert all(r['tick']==8588 and r['phase']==3 for r in calls)
    assert after['tick']==9924 and after['phase']==1 and after['ball_number']==2
    assert after['score_number']==275400000 and after['score_number']-before['score_number']==sum(r['amount']for r in calls)
    assert after['multiplier']==1 and after['bonus_base']==0
    assert t['last_diagnostic_shot_tick']==8524
    assert t['tick_count']-8524<=4000
    return dict(bonus_base=20700000,multiplier=12,multiplied_component=248400000,
        additional_component=7000000,total_score_delta=255400000,new_score=275400000,next_ball_tick=9924)
