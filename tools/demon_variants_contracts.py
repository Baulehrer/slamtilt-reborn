"""Bounded Original force response, both Witch rescues, head cycles and value ladder."""
CASES=['witch-force-on','witch-force-off','witch-left','twice-cycles','zombie-values']
def contracts(t):
 assert t['original_reset_exact']and t['table']=='demon'and 'variant_state'in t
 m={r['label']:r for r in t['milestones']};case=t['case'];p=t['payments'];awards=lambda a:[r['amount']for r in p if r['return_address']==a]
 if case.startswith('witch'):
  assert m['mode_started']['phase']==11 and m['mode_started']['force_state'][0]==1
  assert m['witch_returned']['phase']==2 and m['witch_returned']['state']==2 and m['witch_returned']['force_state'][0]==0 and m['witch_returned']['ball_number']==1
  if case=='witch-left':
   assert m['left_sidelane_contact']['phase']==11 and m['left_sidelane_restored']['ball_number']==1
   return dict(left_sidelane_rescue=True,magnet_disabled=True,ball_number_unchanged=True)
  assert m['force_initial']['tick']==3000
  b=bytes(m['force_20']['ball_bytes']);x=int.from_bytes(b[:4],'little',signed=True)/65536;y=int.from_bytes(b[4:8],'little',signed=True)/65536
  if case.endswith('-on'):assert x>187 and y<296 and m['force_initial']['force_state'][0]==1
  else:assert x==175 and y>301 and m['force_initial']['force_state'][0]==0
  assert m['right_sidelane_contact']['phase']==2 and int.from_bytes(bytes(m['right_sidelane_contact']['ball_bytes'][24:28]),'little',signed=True)==-4*65536
  return dict(magnet_active=case.endswith('-on'),steps=20,x=x,y=y,right_sidelane_rescue=True,ball_number_unchanged=True)
 if case=='zombie-values':
  assert m['mode_started']['phase']==5
  assert [m[k]['zombie_value']for k in ['base_value','value_0','value_1','value_2']]==[5000000,6000000,7000000,8000000]
  assert awards('0x4104c6')==[5000000,6000000,7000000,8000000]
  assert m['zombie_returned']['phase']==2
  return dict(trap_value_ladder=[5000000,6000000,7000000,8000000],four_ramp_kills=True,physical_loss_return=True)
 assert case=='twice-cycles'and m['two_balls']['ball_count']==2
 assert m['after_double']['bonus_base']==2*m['before_double']['bonus_base']>0
 assert m['after_double_duplicate']['bonus_base']==m['after_double']['bonus_base']
 assert m['after_double']['head_flags']==m['after_double_duplicate']['head_flags']==4
 assert m['clock_head_released']['head_flags']==m['clock_head_duplicate_released']['head_flags']==5
 for k in ['first_pair_complete','second_pair_complete']:assert m[k]['head_flags']==0 and m[k]['head_count']==0
 assert m['after_rearmed_double']['bonus_base']==2*m['first_pair_complete']['bonus_base']
 assert awards('0x416209')==[15000000]*2 and awards('0x415486')==[15000000]*2
 assert m['twice_returned']['phase']==2
 base=m['before_bonus_drain'];assert awards('0x407d1e')==[base['bonus_base']*base['multiplier']]
 assert m['following_ball']['ball_number']==2 and m['following_ball']['bonus_base']==0
 return dict(head_pairs=2,head_awards=[15000000]*4,double_bonus=True,duplicate_guards=True,head_pair_rearms_double=True,actual_bonus_payout=awards('0x407d1e')[0],next_ball=2)
