"""Earned five-mode campaign, Retail six-ball finale, bank/rearm and return."""
def contracts(t):
 m={r['label']:r for r in t['milestones']};p=t['payments'];assert t['original_reset_exact']
 for i in range(5):
  row=m['mode_'+str(i)+'_completed'];assert row['phase']==2 and row['played_modes'][:i+1]==[1]*(i+1)
 assert m['all_five_played']['played_modes']==[1]*5 and m['all_five_played']['armed']==[0]*4
 admitted=m['bigblam_admitted'];assert admitted['phase']==7 and admitted['played_modes']==[0]*5 and admitted['field_46ee5e']==5
 assert m['bigblam_spawned']['ball_count']==6 and m['bigblam_spawned']['ball_states']==[2]*6
 assert int(m['unearned_final_guard']['score'])-int(m['bigblam_spawned']['score'])==500000
 assert m['disabled_final_ramp_guard']['score']==m['unearned_final_guard']['score']
 ramps=[r for r in p if r['return_address']=='0x448ae3'];assert [r['amount']for r in ramps]==[10000000]*7
 banks=[r for r in p if r['return_address']=='0x442820'];assert [r['amount']for r in banks]==[25000000,100000000]
 assert m['first_bank_collected']['final_base']==m['bigblam_rewards']['final_base']==10000000
 assert int(m['duplicate_final_top_guard']['score'])-int(m['bigblam_rewards']['score'])==500000
 for n in range(6,1,-1):assert m['final_pool_'+str(n)+'_to_'+str(n-1)]['ball_count']==n-1
 end=m['bigblam_returned'];assert end['phase']==2 and end['ball_count']==1 and end['played_modes']==[0]*5
 assert end['tick']-m['final_pool_2_to_1']['tick']==801
 assert int(end['score'])==346804560
 return dict(earned_modes=list(range(5)),missions_required=False,retail_balls=6,manual_balls=4,per_unique_ramp=10000000,bank_awards=[25000000,100000000],final_mode_awards=195000000,disabled_and_duplicate_guards=True,losses=[6,5,4,3,2,1],return_steps=801,final_score=346804560)
