"""Observed mission-family contracts; retain extra payments separately."""
def contracts(t):
 case=t['mission'];m={v['label']:v for v in t['milestones']};mode={'race':1,'hack':2,'blam':3,'blam-guard':3}[case];s=m['mission_started'];end=m['normal_return'];p=t['payments']
 assert m['all_four_armed']['armed']==[1]*4
 assert s['phase']==5 and s['mode']==mode and s['armed']==[0]*4 and s['played']==[int(i==mode)for i in range(4)]
 assert end['phase']==2 and end['played']==s['played'] and t['original_reset_exact']
 if case=='race':
  assert m['top_sets_first_after']['field_46ee42']==5
  paid=[v for v in p if v['return_address']=='0x448601'];assert [v['amount']for v in paid]==[25000000]
  assert m['race_goal_paid']['phase']==5 and end['tick']-s['tick']==12501
  extra=[v for v in p if v['return_address']=='0x441690'];assert [v['amount']for v in extra]==[5000000]
  assert int(end['score'])==33000000
  return dict(first_place_goal=25000000,expiry_additional_5000000_return='0x441690',expiry_steps=12501,goal_does_not_end_mission=True)
 if case=='hack':
  target=s['field_46ee54'];assert target<7
  w=m['wrong_password_guard'];assert w['phase']==5 and target==w['field_46ee54'] and w['flags_edfa'][target]==1
  assert not any(v['amount']==75000000 and v['tick']<=w['tick']for v in p)
  paid=[v for v in p if v['return_address']=='0x448705'];assert [v['amount']for v in paid]==[75000000]
  assert m['hack_paid']['field_46ee52']==400 and end['tick']-m['hack_paid']['tick']==401
  assert int(end['score'])==78000000
  return dict(winning_event=target,wrong_event_no_award=True,award=75000000,success_countdown_steps=401)
 paid=[v for v in p if v['return_address']=='0x4487ca'];want=5 if case=='blam-guard'else 6
 assert [v['amount']for v in paid]==[10000000]*want
 assert int(m['duplicate_guard']['score'])-int(m['blam_first_after']['score'])==250000
 final=[v for v in p if v['return_address']=='0x442517']
 if case=='blam-guard':
  assert m['one_target_remaining']['flags_edec']==[1,0,1,1,1,1,0]
  assert m['unearned_final_guard']['phase']==5 and not final and int(end['score'])==54500000
  return dict(paid_targets=5,missing_target=6,unearned_final_rejected=True,wrong_branch_point=[1,187,82])
 assert m['all_targets_hit']['flags_edec']==[1,0,1,1,1,1,1] and m['all_targets_hit']['timer']==3000
 assert [v['amount']for v in final]==[30000000] and m['blam_paid']['phase']==2
 assert int(end['score'])==94500000
 return dict(paid_targets=6,per_target=10000000,duplicate_no_target_award=True,final_target=30000000,correct_event6_point=[1,269,51])
