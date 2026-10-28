"""Mission played-bank and station prize proof; independent of native output."""
def contracts(t):
 m={r['label']:r for r in t['milestones']};assert t['original_reset_exact']
 for i in range(4):
  start=m['mission_'+str(i)+'_started'];assert start['phase']==5 and start['mode']==i
  assert start['mission_played']==[int(j<=i)for j in range(4)]
  assert start['armed']==[0]*4
 for i in range(2):
  carry=m['mission_'+str(i)+'_carried_to_next_ball'];assert carry['mission_played']==[int(j<=i)for j in range(4)] and carry['phase']==1
 before=m['all_four_played'];after=m['super_collected'];assert before['mission_played']==[1]*4 and before['phase']==2
 assert before['played_modes']==[0]*5 and after['played_modes']==[0]*5
 assert after['mission_played']==[0]*4 and after['armed']==[0]*4 and after['phase']==2 and after['state']==2
 awards=[r for r in t['payments']if r['return_address']=='0x441f47'];assert len(awards)==1 and awards[0]['amount']==75000000
 assert m['three_mission_station_guard_released']['tick']<awards[0]['tick']<=after['tick']
 station=[r for r in t['payments']if before['tick']<r['tick']<=after['tick']]
 assert [(r['amount'],r['return_address'])for r in station]==[(500000,'0x441b4a'),(75000000,'0x441f47'),(5000000,'0x4413a5')]
 assert int(after['score'])-int(before['score'])==80500000
 assert m['duplicate_super_guard']['mission_played']==[0]*4
 fresh=m['fresh_mission_bank'];assert fresh['mission_played']==[1,0,0,0] and fresh['phase']==5
 assert m['new_game_reset']['mission_played']==[0]*4 and m['fresh_game_launched']['state']==2
 return dict(missions_played_in_one_game=[0,1,2,3],partial_played_carry_across_drains=True,victory_not_required_for_first_two=True,station_award=75000000,ordinary_station=500000,observed_slot_result=5000000,total_collection_delta=80500000,award_return='0x441f47',unearned_three_played_and_duplicate_guards=True,bank_cleared=True,fresh_mission_admission=True,new_game_reset=True,bigblam_mode_bank_untouched=True)
