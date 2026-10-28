"""Earned credits replay ball1 twice; next ordinary drain advances to ball2."""
def contracts(t):
    marks={m['label']:m for m in t['milestones']}
    assert marks['two_credits_ready']['extra_credits']==2
    for i in range(1,4):
        m=marks[f'drain_{i}_settled']
        assert m['phase']==1 and m['extra_credits']==max(0,2-i)
        assert m['ball_number']==(1 if i<3 else 2)
    assert t['prefix_steps']==3940
    return dict(earned_credits=2,credits_after_drains=[1,0,0],ball_numbers_after_drains=[1,1,2],same_ball_replayed_twice=True)
