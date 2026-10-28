"""Seven earned modes -> original final jackpot/replenishment/return contracts."""
def contracts(t):
 assert t['original_reset_exact']and t['table']=='demon'and t['case']=='final-campaign'
 m={r['label']:r for r in t['milestones']};p=t['payments']
 assert m['unearned_final_guard_released']['phase']==2 and not m['unearned_final_guard_released']['final_ready']
 for name,phase in [('bat',9),('grave',8),('meatball',10),('zombie',5),('witch',11),('twice',6),('vampires',7)]:
  assert m[name+'_started']['phase']==phase and m[name+'_returned']['phase']==2
 assert m['bat_started']['ball_number']==m['bat_returned']['ball_number']==1
 assert m['zombie_started']['ball_number']==m['zombie_returned']['ball_number']==1
 assert m['witch_started']['ball_number']==1 and m['witch_returned']['ball_number']==2
 assert m['all_seven_played']['ball_number']==2
 assert m['all_seven_played']['played']==[1]*7 and m['all_seven_played']['final_ready']
 assert m['ready_clock_not_admission_released']['phase']==2 and m['ready_clock_not_admission_released']['final_ready']
 assert m['final_admitted']['phase']==12 and m['final_admitted']['played']==[0]*7 and m['final_admitted']['final_ready']==0
 assert m['final_admitted']['wolf_selected']==0 and m['final_admitted']['spirit_selected']==0
 assert m['four_balls']['ball_count']==4 and max(r[1]for r in t['lifecycle'])==4
 for label,amount in [('four_ball_bank',10000000),('two_ball_bank',7000000),('three_ball_bank',8500000),('cap_four_bank',10000000)]:
  first=m[label+'_0_done']['tick'];last=m[label+'_paid']['tick'];rows=[r['amount']for r in p if first<=r['tick']<=last and r['return_address']=='0x418ee3'];assert rows==[amount]*5,(label,rows)
 assert [r['amount']for r in p if r['return_address']=='0x418f2a']==[35000000]*2
 assert m['two_balls']['ball_count']==2 and m['three_balls']['ball_count']==3 and m['restored_four']['ball_count']==4
 assert m['final_returned']['phase']==2 and m['final_returned']['ball_count']==1 and m['final_returned']['played']==[0]*7
 assert m['final_returned']['tick']-m['pool_2_to_1']['tick']==1
 for label in ['four_ball_bank_paid','two_ball_bank_paid','three_ball_bank_paid','cap_four_bank_paid']:assert m[label]['final_count']==0
 assert m['fresh_bank_armed']['wolf_selected']==3 and m['fresh_bank_armed']['played']==[0]*7
 assert m['final_rewards_done']['mode_total']==257500000
 return dict(seven_earned_modes=True,wins_not_required=True,initial_pool=4,jackpot_by_pool={'2':7000000,'3':8500000,'4':10000000},every_fifth_replenish=True,cap_awards=[35000000]*2,cleared_played_flags=True,fresh_wolf_selection=True,mode_total=257500000,last_ball_return_steps=1)
