"""Original observed extra-ball combo thresholds and redemption."""
def contracts(t):
    m={v['label']:v for v in t['milestones']}
    assert m['count_24']['combo_count']==24 and m['count_24']['extra_ball_threshold']==25 and m['count_24']['pending_extra_ball']==0
    assert m['count_25']['combo_count']==25 and m['count_25']['extra_ball_threshold']==50 and m['count_25']['pending_extra_ball']==1
    assert m['count_49']['combo_count']==49 and m['count_49']['extra_ball_threshold']==50 and m['count_49']['pending_extra_ball']==1
    assert m['count_50']['combo_count']==50 and m['count_50']['extra_ball_threshold']==100 and m['count_50']['pending_extra_ball']==2
    for i in range(1,4):
        assert m[f'redemption_{i}']['pending_extra_ball']==max(0,2-i)
        assert m[f'redemption_{i}']['extra_credits']==min(i,2)
    assert [(e['count'],e['old_threshold'])for e in t['threshold_events']]==[(25,25),(50,50)]
    assert [e['pending_before']for e in t['redemption_events']]==[2,1]
    return dict(thresholds=[25,50,100],earned=2,redeemed=2,duplicate_trap_credit=False,final_credits=2,
        counting='Original player+0c successful combo count; first ramp/expired window do not increment')
