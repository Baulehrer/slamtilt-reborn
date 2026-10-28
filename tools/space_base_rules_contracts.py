"""Bounded Retail base mechanics, including differences from manual wording."""
COMBO_RETURNS={'0x44a45d','0x449b64','0x4494cf'}
def contracts(t):
 m={r['label']:r for r in t['milestones']};p=t['payments'];case=t['case'];assert t['original_reset_exact']
 assert m['normal_return_verified']['phase']==2
 if case=='base-rules':
  assert [r['amount']for r in p if r['return_address']=='0x44a867']==[10000000,15000000]
  assert m['skillshot_10m']['skillshot_next']==15000000 and m['skillshot_15m']['skillshot_next']==20000000
  assert int(m['skillshot_repeat_guard']['score'])-int(m['skillshot_10m']['score'])==250000
  assert [r['amount']for r in p if r['return_address']in COMBO_RETURNS]==[1000000]*40
  for tier,credits in [(20,1),(40,2)]:
   a=m[f'combo_{tier}_earned'];b=m[f'combo_{tier}_collected'];assert a['combo_count']==tier and a['combo_threshold']==tier*2 and a['pending_extra']==1
   assert b['combo_count']==tier and b['pending_extra']==0 and b['extra_credits']==credits
  assert m['credit_1_consumed']['extra_credits']==1 and m['credit_2_consumed']['extra_credits']==0
  assert m['credit_1_launched']['ball_number']==m['credit_2_launched']['ball_number']==1
  assert m['normal_next_ball_launched']['ball_number']==2 and m['normal_next_ball_launched']['combo_count']==40
  assert [r['amount']for r in p if r['return_address']=='0x4465b2']==[40000000]*3
  assert int(m['normal_return_verified']['score'])==248750000
  return dict(skillshots=[10000000,15000000],retail_direct_combo=1000000,combo_count=40,thresholds=[20,40,80],collected_credits=2,replayed_ball_numbers=[1,1,2],combo_bonus_payouts=[40000000]*3)
 if case=='skillshot-expiry':
  assert m['skillshot_expired']['skillshot_timer']>=0x8000 and m['expired_ramp_guard']['skillshot_next']==10000000
  assert not any(r['return_address']=='0x44a867'for r in p)
  return dict(expired_first_arrival_awarded=False,next_value_unchanged=10000000)
 if case=='combo-mode-guard':
  a=m['armed_timer_in_mode'];b=m['combo_suppressed'];assert a['phase']==b['phase']==6 and a['combo_timers'][0]<0x8000
  assert a['combo_count']==b['combo_count'] and not any(r['return_address']in COMBO_RETURNS and a['tick']<r['tick']<=b['tick']for r in p)
  return dict(genuinely_armed_timer=True,mode_combo_suppressed=True)
 assert case=='speed-rules'
 assert [r['amount']for r in p if r['return_address']=='0x44a0fd']==[4000000,6000000,8000000,10000000,4000000]
 assert [r['amount']for r in p if r['return_address']=='0x44a082']==[20000000]
 assert m['unarmed_speed_guard']['speed_grade']==0
 for i in range(1,5):assert m['speed_grade_'+str(i)]['speed_grade']==i
 assert m['lunatic_paid']['speed_grade']==m['expired_speed_guard']['speed_grade']==0
 assert m['expired_speed_guard']['speed_window']>=0x8000
 assert m['decay_started']['speed_grade']==1 and m['speed_grade_decayed']['speed_grade']==0
 a=m['decay_started']['tick'];b=m['speed_grade_decayed']['tick'];assert t['globals'][b-1]['frame_count']-t['globals'][a-1]['frame_count']==751
 return dict(grades=[4000000,6000000,8000000,10000000],lunatic=20000000,window_expiry_guard=True,unarmed_guard=True,grade_decay_frames=751,passage_counter_not_timer=True)
