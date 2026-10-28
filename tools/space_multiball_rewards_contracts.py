"""Original-callsite rewards, duplicate guards and complete three-ball return."""
def contracts(t):
 m={r['label']:r for r in t['milestones']};case=t['case'];p=t['payments'];assert t['original_reset_exact']
 assert m['three_balls']['ball_count']==3
 for label,count in [('pool_3_to_2',2),('pool_2_to_1',1),('normal_return_verified',1)]:
  assert m[label]['ball_count']==count and m[label]['ball_states']==[2]*count
 assert m['normal_return_verified']['phase']==2
 assert m['pool_3_to_2']['phase']==m['pool_2_to_1']['phase']==(4 if case=='multiball'else 6)
 assert int(m['unearned_top_guard_released']['score'])-int(m['three_balls']['score'])==500000
 if case=='multiball':
  awards=[r for r in p if r['return_address']=='0x442251'];assert [r['amount']for r in awards]==[10000000,20000000,30000000]
  for i in range(1,4):
   row=m['jackpot_'+str(i)+'_released'];assert row['field_46ee40']==0 and row['standard_flags']==[1,0,0,0,0,1,1]
  assert int(m['normal_return_verified']['score'])==65250000
  result=dict(jackpots=[10000000,20000000,30000000],ramps=[0,5,6],rearmed_after_each=True)
 else:
  awards=[r for r in p if r['return_address']=='0x4488f9'];assert [r['amount']for r in awards]==[10000000]*7
  supers=[r for r in p if r['return_address']=='0x44267f'];assert [r['amount']for r in supers]==[30000000]
  first=[r for r in t['milestones']if r['label']=='ramp_0_done'][0]
  assert int(m['duplicate_guard']['score'])-int(first['score'])==250000
  assert int(m['alien_super_duplicate_released']['score'])-int(m['alien_super_jackpot_released']['score'])==500000
  assert int(m['normal_return_verified']['score'])==104000000
  result=dict(distinct_events=list(range(7)),per_alien=10000000,super_jackpot=30000000,duplicate_guards=True)
 assert m['normal_return_verified']['tick']-m['pool_2_to_1']['tick']==801
 result.update(losses=[3,2,1],return_steps=m['normal_return_verified']['tick']-m['pool_2_to_1']['tick'],final_score=int(m['normal_return_verified']['score']))
 return result
