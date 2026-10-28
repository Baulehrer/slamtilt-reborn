"""Original skillshot eligibility, exact expiry boundary and next-ball rearm."""
def contracts(t):
    case=t['skillshot_case'];marks={m['label']:m for m in t['milestones']};calls=t['skillshot_pay_calls'];checks=t['skillshot_consumer_checks']
    assert all(c['amount']==10000000 for c in calls)
    if case=='success-rearm':
        assert len(calls)==2
        assert marks['duplicate_after_consumption']['paid_count']==1
        assert marks['next_ball_window']['ball_number']==2 and 0<=marks['next_ball_window']['window']<=200
        assert marks['second_ball_skillshot']['paid_count']==2
    elif case=='wrong-route':
        assert marks['other_ramp_no_skillshot']['paid_count']==0
        assert 0<=marks['other_ramp_no_skillshot']['window']<=200
        assert len(calls)==1
    elif case=='last-tick':
        assert len(calls)==1 and checks[0]['tick']==1112 and checks[0]['window']==0
    elif case=='expired':
        assert not calls and checks[0]['tick']==1113 and checks[0]['window']==65535
    else:raise AssertionError(case)
    if calls:assert any(e['target']==0x42dd00 for e in t['skillshot_dispatches'])
    return dict(case=case,paid=len(calls),amount=10000000,consumer='0x43898c',pay='0x4389eb',callback='0x42dd00',last_accepted_tick=1112,first_expired_tick=1113)
