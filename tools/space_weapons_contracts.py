"""Original weapon bank/payout and paired inactive/active force evidence."""
def contracts(t):
 m={r['label']:r for r in t['milestones']};p=t['payments'];case=t['case'];assert t['original_reset_exact']
 if case=='special-left':
  assert m['special_left_after']['phase']==2 and m['special_left_after']['weapon_state'][5]==0
  assert any(e['callsite']=='0x404ab4'and e['target']=='0x444810'for e in t['executed_call_edges'])
  return dict(original_key_scan='0x1d',input_callback='0x444810',lane_trajectory_not_claimed=True)
 if case=='weapons-ladder':
  assert m['one_lit']['weapon_state'][:3]==[255,0,0] and m['duplicate_weapon_guard']['weapon_state']==m['one_lit']['weapon_state']
  assert m['flipper_rotated']['weapon_state'][:3]==[0,0,255]
  assert [m['weapon_bank_'+str(i)]['weapon_state'][-1]for i in range(6)]==[2,4,6,8,10,10]
  assert [r['amount']for r in p if r['return_address']=='0x448de3']==[10000000]
  assert m['bonus_entered']['bonus_base']==250000 and m['bonus_entered']['weapon_state'][-1]==10
  assert [r['amount']for r in p if r['return_address']=='0x407d1e']==[2500000]
  assert m['following_ball']['weapon_state'][-1]==1
  return dict(multiplier=[1,2,4,6,8,10],cap_award=10000000,flipper_cycle=True,duplicate_guard=True,base=250000,payout=2500000,next_ball_multiplier=1)
 assert m['earned_magna']['weapon_state'][:4]==[0,0,0,65535]
 end=m['magna_20_steps'];s=t['states'][end['tick']];y=int.from_bytes(bytes(s[4:8]),'little',signed=True)/65536;vy=int.from_bytes(bytes(s[24:28]),'little',signed=True)/65536
 if case=='magna-off':
  assert end['weapon_state'][3:6]==[65535,65535,0] and y>450 and vy>0
  return dict(control_force_off=True,ball_y=y,velocity_y=vy)
 assert m['magna_start']['weapon_state'][3:6]==[0,200,65535] and y<420 and vy<0
 assert m['retrigger_guard']['weapon_state'][3:6]==end['weapon_state'][3:6]
 assert m['magna_expired']['weapon_state'][3:6]==[0,65535,0] and m['unarmed_activation_guard']['weapon_state'][3:6]==[0,65535,0]
 assert m['magna_rearmed']['weapon_state'][3]==65535
 a=m['activation_boundary']['tick'];b=m['magna_expired']['tick'];assert t['globals'][b-1]['frame_count']-t['globals'][a-1]['frame_count']==201
 return dict(original_key_scan='0x9d',right_shift_not_activation=True,ball_y=y,velocity_y=vy,expiry_frames=201,retrigger_guard=True,rearmed=True)
