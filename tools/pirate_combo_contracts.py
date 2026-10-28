"""Original-observed combo growth, cap and inclusive timer boundary."""
def contracts(t):
    case=t['combo_case'];marks={m['label']:m for m in t['milestones']};pays=t['combo_pays']
    if case=='chain':
        assert [p['amount']for p in pays]==[1000000,2000000,3000000,3000000]
        assert marks['armed']['combo_count']==0
        assert marks['four_paid']['combo_count']==4 and marks['four_paid']['combo_value']==3000000
        assert marks['expired']['combo_value']==1000000 and marks['expired']['combo_window']==65535
        assert marks['fresh_arm_after_expiry']['combo_count']==4 and marks['fresh_arm_after_expiry']['combo_value']==1000000
    elif case=='last-tick':
        assert len(pays)==1 and pays[0]['amount']==1000000
        assert t['combo_checks'][-1]['tick']==1916 and t['combo_checks'][-1]['window']==0
    elif case=='expired':
        assert not pays and t['combo_checks'][-1]['tick']==1917 and t['combo_checks'][-1]['window']==65535
        assert marks['boundary_result']['combo_count']==0
    else:raise AssertionError(case)
    if pays:assert any(e['target']==0x42f44c for e in t['combo_dispatches'])
    return dict(case=case,amounts=[p['amount']for p in pays],cap=3000000,last_accepted_tick=1916,first_expired_tick=1917,counter='player+0c increments paid combos only')
