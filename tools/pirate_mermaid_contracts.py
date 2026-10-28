"""Semantic assertions independent of Unicorn and the native implementation."""
BANKS={'base':1000000,'growth-2m':3000000,'growth-3m':4000000,'hold-bonus':1000000,'hold-tilt':1000000,'hold-tilt-combo':1000000,'hold-multiplier':1000000}
def contracts(t):
    case=t['mermaid_case'];bank=BANKS[case];marks={m['label']:m for m in t['milestones']};calls=t['bonus_score_calls']
    ready=marks['reward_ready'];assert ready['mermaid_bank']==bank
    for i in range(1,4):
        a=marks[f'collection_{i}_before'];b=marks[f'collection_{i}_after']
        assert a['mermaid_bank']==b['mermaid_bank']==bank
        payments=[e for e in calls if a['tick']<e['tick']<=b['tick'] and e['return_address']=='0x432b7f']
        assert len(payments)==1 and payments[0]['amount']==bank
        assert int(b['score_bcd'])-int(a['score_bcd'])==bank
        assert b['bonus_base']-a['bonus_base']==400000
    held=case.startswith('hold-');tilted=case.startswith('hold-tilt')
    for i in range(1,3):
        a=marks[f'drain_{i}_bonus_entered'];b=marks[f'drain_{i}_settled'];assert b['phase']==1 and b['ball_number']==i+1
        assert b['mermaid_bank']==bank and b['bonus_hold']==0 and b['bonus_multiplier']==1
        assert b['bonus_base']==(a['bonus_base'] if held and i==1 else 0)
        payments=[e for e in calls if a['tick']<e['tick']<=b['tick'] and e['return_address']=='0x407d1e']
        table_pay=[e for e in calls if a['tick']<e['tick']<=b['tick'] and e['return_address']=='0x4351ef']
        assert len(table_pay)==1 and table_pay[0]['amount']==a['ordinary_ramp_count']*1000000
        if tilted and i==1:assert not payments and int(b['score_bcd'])-int(a['score_bcd'])==table_pay[0]['amount']
        else:
            assert len(payments)==1 and payments[0]['amount']==a['bonus_base']*a['bonus_multiplier']
            assert int(b['score_bcd'])-int(a['score_bcd'])==payments[0]['amount']+table_pay[0]['amount']
    if case=='growth-3m':
        assert marks['game_over']['mermaid_bank']==bank
        assert marks['new_game_bank_reset']['mermaid_bank']==1000000
    assert ready['bonus_hold']==(65535 if held else 0)
    assert marks['launched']['tilt']==0
    if case=='hold-multiplier':assert marks['drain_1_bonus_entered']['bonus_multiplier']==2
    if case=='hold-tilt-combo':assert marks['combos_earned']['ordinary_ramp_count']==2
    if tilted:assert marks['tilt_reached']['tilt']!=0
    return dict(bank=bank,collections=3,persists_across_ball=True,hold_once=held,tilt_suppresses_first_payout=tilted,hold_preserved_under_tilt=tilted)
