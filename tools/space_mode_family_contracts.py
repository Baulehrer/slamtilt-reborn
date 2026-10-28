"""Bounded outcomes from actual original callbacks; video failure is not success."""
def contracts(t):
 case=t['case'];m={r['label']:r for r in t['milestones']};p=t['payments'];selected={'sabre':1,'planet':2,'walker':3,'bikes':4}[case]
 assert t['original_reset_exact'] and m['selected']['selected']==selected and m['mode_started']['selected']==selected
 assert m['normal_return_verified']['phase']==2 and m['normal_return_verified']['ball_count']==1
 if case=='sabre':
  assert m['damage_before']['field_46ee20']==44 and m['damage_complete']['field_46ee20']==0
  assert [r['amount']for r in p if r['return_address']=='0x44b172']==[2000000]*44
  assert [r['amount']for r in p if r['return_address']=='0x44273d']==[30000000]
  assert not any(r['amount']==30000000 and r['tick']<=m['unearned_finish_guard_released']['tick']for r in p)
  assert int(m['normal_return_verified']['score'])==119805800
  return dict(outcome='success',bumper_damage_hits=44,per_hit=2000000,finish=30000000,unearned_finish_guard=True)
 if case=='bikes':
  paid=[r for r in p if r['return_address']=='0x448a46'];assert [r['amount']for r in paid]==[30000000]*3
  assert not any(r['tick']<=m['wrong_side_guard']['tick']for r in paid)
  assert m['normal_return_verified']['tick']-m['mode_started']['tick']==12921
  return dict(outcome='three_hits_then_expiry',matching_side_award=30000000,wrong_side_guard=True,expiry_steps=12921)
 if case=='walker':
  assert 71<=m['walker_aim']['field_46ee4e']<=87
  assert [r['amount']for r in p if r['return_address']=='0x444752']==[15000000]
  assert m['walker_spawned_balls']['ball_count']==3
  assert m['pool_3_to_2']['ball_count']==2 and m['pool_2_to_1']['ball_count']==1
  return dict(outcome='aimed_hit_then_ball_loss_return',award=15000000,observed_balls=3,manual_balls=2,retail_sets_two_extra=True,manual_difference_reason="UNKNOWN")
 assert m['mode_started']['video_flag']==1 and m['mode_started']['phase']==2
 assert m['planet_failed_naturally']['video_flag']==0
 assert m['planet_failed_naturally']['field_466b78']==0
 assert m['planet_ball_released']['state']==2 and m['planet_ball_released']['tick']-m['planet_failed_naturally']['tick']==520
 return dict(outcome='no_input_failure_and_return',success_path_verified=False,video_flag='0x46c6c0')
