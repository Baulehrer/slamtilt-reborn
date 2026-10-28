"""Full original Skull-ramp/right-trap multiplier ladder contract."""
VALUES=[1,2,4,6,8,10,12]
REQUIREMENTS=[2,3,4,5,6,7]
def contracts(t):
    rows=t['ladder_stages'];assert len(rows)==6
    marks={m['label']:m for m in t['milestones']}
    for i,row in enumerate(rows):
        assert row['before']==VALUES[i]and row['after']==VALUES[i+1]
        assert row['skull_hits']==REQUIREMENTS[i]
        before=marks[f'stage_{i}_armed'];after=marks[f'stage_{i}_collected']
        assert before['multiplier']==VALUES[i]and before['multiplier_lit']==65535
        assert before['skull_progress']==0
        assert after['multiplier']==VALUES[i+1]and after['multiplier_lit']==0 and after['skull_progress']==0
        for n in range(1,REQUIREMENTS[i]):
            partial=marks[f'stage_{i}_skull_{n}_settled']
            assert partial['multiplier_lit']==0 and partial['skull_progress']==n
    for n in range(1,18):
        m=marks[f'capped_skull_{n}_settled'];assert m['multiplier']==12 and m['multiplier_lit']==0 and m['skull_progress']==0
    end=marks['unlit_cap_trap_collected'];assert end['multiplier']==12 and end['multiplier_lit']==0
    assert t['cap_trap_registration_delta']==0
    assert t['tick_count']<10000
    return dict(values=VALUES,skulls_per_upgrade=REQUIREMENTS,capped_skull_hits=17,cap_trap_rejected_upgrade=True,
        original_display='0x42c03c',drain_payout_verified=False)
