"""Evidence contracts for reachable Retail repeat/ramp/target/aim variants."""
def contracts(t):
 assert t['original_reset_exact'];m={r['label']:r for r in t['milestones']};p=t['payments'];case=t['case']
 if case=='sabre-variants':
  assert m['sabre_started']['field_46ee20']==44
  for i in range(4):assert m['target_'+str(i)+'_before']['field_46ee20']==44-i and m['target_'+str(i)+'_after']['field_46ee20']==43-i
  assert m['target_duplicate_guard']['field_46ee20']==43 and m['excluded_ramp_guard']['field_46ee20']==40
  for i in range(6):assert m['ramp_'+str(i)+'_before']['field_46ee20']==40-3*i and m['ramp_'+str(i)+'_after']['field_46ee20']==37-3*i
  assert [m[k]['field_46ee20']for k in ['near_finish','one_internal_left','zero_internal','one_displayed_unit','defeated_ramp_guard']]==[4,1,0,0,0]
  assert [r['amount']for r in p if r['return_address']=='0x44b172']==[2000000]*4
  assert [r['amount']for r in p if r['return_address']=='0x448b78']==[6000000]*13
  assert [r['amount']for r in p if r['return_address']=='0x448c5a']==[2000000]
  assert [r['amount']for r in p if r['return_address']=='0x44273d']==[30000000]
  assert {0:1,44:45}.items()<=dict((o['field_46ee20'],o['displayed_units'])for o in t['power_display_observations']).items()
  assert m['sabre_finished']['phase']==2
  return dict(targets=4,target_damage=1,target_award=2000000,duplicate_guard=True,ramp_events=[0,2,3,4,5,6],ramp_damage=3,ramp_award=6000000,excluded_ramp1=True,partial_damage_cap_award=2000000,power_display_field_plus1_verified=True,finish=30000000)
 if case=='multiball-repeat':
  assert m['second_cycle_ready']['threshold']==3
  below=m['below_higher_threshold'];armed=m['second_cycle_armed'];spawn=m['second_three_balls'];end=m['second_cycle_returned']
  assert below['locks']==3 and below['airlock_timer']==65535 and below['phase']==2
  assert 0<armed['airlock_timer']<100 and armed['phase']==2
  assert spawn['ball_count']==3 and spawn['phase']==4 and spawn['threshold']==4
  assert m['pool_3_to_2']['ball_count']==2 and m['pool_2_to_1']['ball_count']==1
  assert end['phase']==2 and end['threshold']==4
  return dict(second_cycle_lock_contacts=4,three_contacts_not_enough=True,threshold_after_first=3,threshold_after_second=4,second_pool=3,drain_return=True,cap9_evidence='STATIC only; not seven extra runtime cycles')
 elif case=='walker-repeat':
  assert [r['amount']for r in p if r['return_address']=='0x444752']==[15000000]*2
  assert m['walker_recaptured']['state']==3 and m['walker_recaptured']['ball_count']==3
  assert m['walker_second_aim']['field_46ee4e']==71 and m['walker_second_aim']['state']==6
  assert int(m['walker_second_shot']['score'])-int(m['walker_second_aim']['score'])==15000000
  assert m['walker_after_second_shot']['ball_count']==3
  assert m['walker_repeat_returned']['phase']==2 and m['walker_repeat_returned']['ball_count']==1
  return dict(two_awards=[15000000,15000000],actual_mode_trap_recapture=True,second_sight=True,pool_stays3=True,drain_return=True)
 elif case=='race-variants':
  assert m['race_started']['field_46ee42']==1 and m['passive_ramp_guard']['field_46ee42']==1
  assert [r['amount']for r in p if r['return_address']=='0x448601']==[5000000*i for i in range(1,6)]
  assert [r['amount']for r in p if r['return_address']=='0x44857d']==[2500000]*10
  for i in range(1,6):
   before=m['goal_'+str(i)+'_before'];after=m['goal_'+str(i)+'_after']
   assert before['field_46ee42']==i and before['field_46ee4a']==65535
   assert after['field_46ee42']==1 and after['field_46ee4a']==i-1
   assert after['timer']-before['timer']==100*i-221
  assert m['rank_cap_guard']['field_46ee42']==5
  assert len([x for x in m if x.startswith('goal_gate_')])==10
  return dict(goal_awards=[5000000*i for i in range(1,6)],ordinary_advances=10,advance_award=2500000,cap5=True,gate_passes=10,goal_timer_extension_per_counter=100,below_fifth='Not manufactured: Retail starts/reset at fifth; static guard only, alias/writer search bounded')
 elif case.startswith('walker-aim'):
  target=int(case.removeprefix('walker-aim'));before=m['aim_edge_before'];after=m['aim_edge_fired']
  assert before['field_46ee4e']==target and after['field_46ee4e']==65535
  assert m['early_enter_before']==dict(m['early_enter_ignored'],label='early_enter_before')
  assert [r['amount']for r in p if r['return_address']=='0x444752']==([15000000]if target==87 else[])
  assert m['pool_3_to_2']['ball_count']==2 and m['pool_2_to_1']['ball_count']==1
  assert m['aim_edge_returned']['phase']==2
  return dict(aim=target,hit=target==87,early_enter_ignored=True,miss_also_spawns3=True,drain_return=True)
 else:raise AssertionError(case)
