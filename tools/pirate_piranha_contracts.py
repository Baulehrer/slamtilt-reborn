"""Original-observed Piranha paired targets and ten paid bumper-hit contract."""

def contracts(t):
    marks={v['label']:v for v in t['milestones']}
    def m(label):return marks[label]
    assert m('left_only')['pair_flags']==[1,0]and m('left_only')['pops_remaining']==0
    assert m('same_left_again')['pair_flags']==[1,0]and m('same_left_again')['pops_remaining']==0
    assert m('pair_earned')['pair_flags']==[0,0]and m('pair_earned')['pops_remaining']==10
    for index in range(1,11):
        before=m(f'paid_{index}_before');after=m(f'paid_{index}_after')
        assert before['pops_remaining']==11-index and after['pops_remaining']==10-index
        assert after['paid_calls']==before['paid_calls']+1
        assert after['score_number']-before['score_number']>=2000000
    before=m('eleventh_before');after=m('eleventh_after')
    assert before['pops_remaining']==after['pops_remaining']==0
    assert before['paid_calls']==after['paid_calls']==10
    assert 0<after['score_number']-before['score_number']<2000000
    assert m('second_pair_earned')['pops_remaining']==10
    assert m('partial_spent')['pops_remaining']==7
    assert m('partial_same_left_again')['pops_remaining']==7
    assert m('partial_rearmed')['pops_remaining']==10
    assert m('after_rearm_paid')['pops_remaining']==9
    assert len(t['paid_events'])==14
    assert all(e['amount']==2000000 and 0<=e['remaining']<=9 for e in t['paid_events'])
    assert any(e['target']==0x42cf8c for e in t['piranha_dispatches'])
    assert any(e['target']==0x42dc64 for e in t['piranha_dispatches'])
    assert t['diagnostic_shots']and all(s['layer']==0 for s in t['diagnostic_shots'])
    return dict(paid_hits=14,first_window_paid_hits=10,eleventh_paid=False,rearm_from=7,rearm_to=10,remaining_after_final_hit=9,
        earned_callback='0x42cf8c',paid_callback='0x42dc64')
