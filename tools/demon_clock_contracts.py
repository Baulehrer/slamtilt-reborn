"""Earned Demon ClockTower admission, jackpot lock counts and real x8 bonus."""
def contracts(t):
 assert t['original_reset_exact']and t['table']=='demon';m={r['label']:r for r in t['milestones']};p=t['payments'];case=t['case']
 if case=='clock-tower':
  assert [m['clock_'+str(i)+'_released']['observed_words'].get('0x46d658',0)for i in range(3)]==[1,2,0]
  assert [m['clock_'+str(i)+'_released']['phase']for i in range(3)]==[2,2,4]
  assert m['three_balls']['ball_count']==3 and m['three_balls']['ball_states']==[2]*3
  assert [r['amount']for r in p if r['return_address']=='0x41648c']==[500000]*3
  assert m['three_balls']['bonus_base']==750000
  assert m['pool_3_to_2']['ball_count']==2 and m['pool_2_to_1']['ball_count']==1
  assert m['clock_returned']['phase']==2 and m['clock_returned']['tick']-m['pool_2_to_1']['tick']==4001
  return dict(trap=[0,21,196],captures_to_admit=3,ordinary_capture_award=500000,bonusbase_per_capture=250000,spawned_pool=3,return_after_last_loss_steps=4001)
 if case=='clock-bonus':
  assert [m['bonus_bank_'+str(i)]['multiplier']for i in range(4)]==[2,4,6,8]
  assert m['earned_bonusbase']['bonus_base']==250000 and m['earned_bonusbase']['multiplier']==8
  assert [r['amount']for r in p if r['return_address']=='0x407d1e']==[2000000]
  assert m['following_ball']['multiplier']==1 and m['following_ball']['ball_number']==2 and int(m['following_ball']['score'])==2500000
  return dict(earned_multiplier=8,earned_bonusbase=250000,actual_payout=2000000,next_ball_multiplier=1)
 assert case=='clock-rewards'
 assert m['unarmed_trap_guard_contact']['state']==3 and m['rearm_trap_guard_contact']['state']==3
 assert t['clock_state'][m['held_1']['tick']-1][:2]==[3,1] and t['clock_state'][m['held_2']['tick']-1][:2]==[3,2]
 assert t['clock_state'][m['three_ball_jackpot']['tick']-1][:2]==[3,3] and t['clock_state'][m['single_ball_paid']['tick']-1][:2]==[1,1]
 assert m['unarmed_released']['requirement']==1 and m['unarmed_released']['field_34']==0
 assert m['first_ramp_after']['requirement']==0 and m['armed_duplicate_ramp_after']['requirement']==0
 assert [m['held_'+str(i)]['field_34']for i in [1,2]]==[1,2]
 assert [r['amount']for r in p if r['return_address']=='0x414544']==[60000000,20000000]
 first=next(r for r in p if r['return_address']=='0x414544');assert first['tick']>m['held_2']['tick']
 assert m['three_ball_jackpot']['clock_total']==3 and m['three_ball_jackpot']['requirement']==4
 assert m['rearm_guard_released']['field_34']==0 and m['rearm_guard_released']['requirement']==4
 assert [m['rearm_ramp_'+str(i)+'_after']['requirement']for i in range(4)]==[3,2,1,0]
 assert m['last_ball_armed']['ball_count']==1 and m['single_ball_paid']['clock_total']==4 and m['single_ball_paid']['requirement']==5
 assert m['rewards_returned']['phase']==2 and m['rewards_returned']['ball_count']==1
 return dict(jackpots=[60000000,20000000],lock_factor=[3,1],all_active_held_guard=True,rearm_requirements=[1,4,5],unarmed_and_rearm_trap_guards=True,ramps=[1,130,30],ordinary_awards_retained=True)
