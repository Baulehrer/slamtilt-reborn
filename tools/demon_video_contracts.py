"""Bounded bank -> Original video controls/rewards -> physical release."""
CASES=['video-brain-win','video-brain-miss','video-wolf-shoot','video-wolf-idle']
def contracts(t):
 assert t['original_reset_exact']and t['table']=='demon'and t['case']in CASES
 m={r['label']:r for r in t['milestones']};p=t['payments'];case=t['case'];brain='brain'in case
 for i in range(3):assert m['moon_'+str(i)]['moon_flags']==[int(j<=i)for j in range(4)]
 assert m['video_armed']['moon_flags']==[0]*4 and m['video_armed']['video_armed']==1
 assert m['video_started']['video_state'][-1]==1 and m['video_started']['video_armed']==0 and m['video_started']['state']==3
 assert m['video_started']['field_46d6e4']==int(brain)
 assert m['video_ended']['video_state'][-1]==0 and m['video_returned']['state']==2 and m['video_returned']['phase']==2
 awards=lambda a:[r['amount']for r in p if r['return_address']==a]
 out=dict(earned_bank=True,first_bank_award=600000,video_kind=int(brain),returned_free=True)
 assert awards('0x41b500')[0]==600000
 if brain:
  assert m['early_enter_guard']['video_state'][-1]==1 and m['early_enter_guard']['field_46d594']==31
  assert m['choice_ready']['field_46d594']==0xffffffff
  selected=m['choice_selected'];won=case=='video-brain-win';assert bool(selected['cups'][selected['selected']])==won
  assert awards('0x4169c7')==([50000000]if won else[])
  out.update(early_enter_ignored=True,award=50000000 if won else 0,scope='Frozen key schedule chosen from observed cups; not a human visual-tracking proof')
  if won:
   assert m['right_edge']['selected']==m['right_edge_guard']['selected']==4
   assert m['left_edge']['selected']==m['left_edge_guard']['selected']==0
   out['selection_bounds']=[0,4]
 else:
  expected=[5000000,10000000]if case=='video-wolf-shoot'else[];assert awards('0x4170ac')==expected
  out.update(kill_awards=expected,scope='Two earned kills then stop shooting and allow Original failure; idle case no kills')
  if case=='video-wolf-idle':
   assert m['duplicate_moon_guard']['moon_flags']==[1,0,0,0]and m['duplicate_moon_guard']['video_armed']==0
   assert m['armed_bank_repeat']['video_armed']==1 and awards('0x41b500')==[600000,15100000]
   out.update(duplicate_bank_flag_guard=True,already_armed_bank_award=15100000)
 return out
