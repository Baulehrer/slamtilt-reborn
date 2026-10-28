"""Bounded physical kickback and all twelve genuine Clock award outcomes."""
CASES=['kickback-on','kickback-off']+['clock-award-'+str(i)for i in range(12)]
def contracts(t):
 assert t['original_reset_exact']and t['table']=='demon';m={r['label']:r for r in t['milestones']};case=t['case'];p=t['payments']
 if case.startswith('kickback'):
  assert m['same_ball_before']['tick']==1000
  if case=='kickback-off':
   assert m['partial_skull_guard']['skulls']==[1,1,0]and m['after_contact']['kickback']==0
   assert m['after_80']['ball_bytes'][4:8]!=m['after_contact']['ball_bytes'][4:8]
   return dict(armed=False,partial_bank_guard=True,contact=[0,16,520])
  assert [r['amount']for r in p if r['return_address']=='0x41b59b']==[600000,600000]
  assert m['earned_skulls']['skulls']==[0]*3 and m['earned_skulls']['kickback']==0xffffffff
  assert m['after_contact']['kickback']==250 and int.from_bytes(bytes(m['after_contact']['ball_bytes'][24:28]),'little',signed=True)==-3*65536
  assert m['grace_contact']['kickback']==210 and m['expired']['tick']==2000 and m['expired_guard']['kickback']==0
  assert m['second_save']['kickback']==250
  return dict(armed=True,bank_award=600000,initial_grace=250,grace_repeat_does_not_extend=True,expiry_tick=2000,rearmed=True,contact=[0,16,520])
 i=int(case.rsplit('-',1)[1]);before=m['award_before'];after=m['award_applied'];released=m['award_released']
 assert [r['amount']for r in p if r['return_address']=='0x41b6e3']==[600000]
 assert m['clock_bank_armed']['right_flags']==[0]*5 and m['clock_bank_armed']['clock_armed']==0xffffffff
 assert m['spin_selected']['clock_armed']==0 and m['spin_selected']['clock_index']==i
 assert m['stop_keys']['spin_elapsed']>=312 and released['state']==2
 assert [r['amount']for r in p if r['return_address']=='0x41648c']==[500000]*2
 awards=lambda a:[r['amount']for r in p if r['return_address']==a]
 if i==0:assert after['video_armed']==1
 if i==1:assert awards('0x415ef6')==[10000000]
 if i==2:assert after['spirit_selected']==1
 if i==3:assert before['bonus_base']==250000 and awards('0x415e77')==[250000]and after['bonus_base']==before['bonus_base']
 if i==4:assert after['kickback']==0xffffffff
 if i==5:assert awards('0x415ee3')==[5000000]
 if i==6:assert after['extra_balls']==before['extra_balls']+1 and m['extra_ball_consumed']['extra_balls']==0 and m['extra_ball_consumed']['ball_number']==1
 if i==7:assert after['field_0c']==before['field_0c']+8
 if i==8:assert before['bonus_base']==250000 and after['bonus_base']==500000
 if i==9:assert awards('0x415f09')==[20000000]
 if i==10:assert after['field_46d604']==before['field_46d604']+1500 and m['saver_restored']['ball_number']==1 and m['saver_restored']['state']==2
 if i==11:assert after['field_0c']==before['field_0c']+5
 return dict(index=i,earned_right_bank=True,real_elapsed_selection=True,both_flipper_stop=True,ordinary_clock_awards_retained=True,extra_ball_consumed=i==6,actual_ball_save=i==10)
