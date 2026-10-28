"""Six original level awards, pending→collected Extra Ball→same-ball replay."""
def contracts(t):
 m={r['label']:r for r in t['milestones']};p=t['payments'];assert t['original_reset_exact']
 assert [r['amount']for r in p if r['return_address']=='0x445df8']==[15000000]*6
 start=m['video_started'];end=m['six_levels_complete'];pending=m['extra_pending'];collected=m['extra_collected'];used=m['extra_consumed_after_bonus'];launched=m['extra_ball_launched']
 assert start['remaining_levels']==6 and start['field_466b78']==3
 assert all(r['field_466b78']==3 for r in t['milestones']if r['label'].startswith('video_transition_'))
 assert end['remaining_levels']==0 and end['field_466b78']==3 and end['video_flag']==0
 assert pending['pending_extra']==1 and pending['extra_credits']==0
 assert collected['pending_extra']==0 and collected['extra_credits']==1
 assert used['extra_credits']==0 and used['ball_number']==start['ball_number']==launched['ball_number']==1
 assert launched['state']==2 and launched['phase']==2 and m['normal_return_verified']['phase']==2
 assert int(m['normal_return_verified']['score'])==92502480
 assert not any(e['tick']>=661 and e['tick']<end['tick']for e in t['diagnostic_shots'])
 assert {e['action']for e in t['inputs']if 661<=e['tick']<end['tick']}=={'left','right'}
 return dict(levels=6,per_level=15000000,mode_total=90000000,lives_remaining=3,extra_ball_earned_collected_consumed=True,replayed_ball_number=1,steering='Frozen left/right only during video')
