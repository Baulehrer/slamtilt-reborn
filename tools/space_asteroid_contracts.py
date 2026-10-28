"""Bounded Asteroid event/score/expiry/played-state semantics, no emulator."""
def contracts(t):
 m={r['label']:r for r in t['milestones']};start=m['asteroid_started'];payments=t['payments']
 assert m['asteroid_armed']['armed']==[1,1,1,1]
 assert start['phase']==5 and start['mode']==0 and start['timer']==12000
 assert start['award']==5000000 and start['armed']==[0]*4 and start['played_0']==1
 asteroid=[p for p in payments if p['return_address']=='0x441e9e']
 assert [p['amount']for p in asteroid]==[5000000,5500000,6000000]
 for i,award in enumerate([5000000,5500000,6000000]):
  a,b=m[f'award_{i}_before'],m[f'award_{i}_after']
  assert a['award']==award and b['award']==award+500000
  assert int(b['score'])-int(a['score'])==award+500000
  assert sum(a['tick']<p['tick']<=b['tick']for p in asteroid)==1
 a,b=m['ramps_guard_before'],m['ramps_guard_after'];assert a['award']==b['award']==6000000
 assert int(b['score'])-int(a['score'])==500000 and b['phase']==5
 expired=m['mission_expired'];assert expired['tick']-start['tick']==12001
 assert expired['phase']==2 and expired['timer']==65535 and expired['played_0']==1
 guarded=m['played_not_rearmed'];assert guarded['phase']==2 and guarded['armed'][0]==0 and guarded['played_0']==1
 # A further20M is observed at a distinct original call; no invented narrative label.
 extra=[p for p in payments if p['return_address']=='0x4413d5'];assert [p['amount']for p in extra]==[20000000]
 for i,ball in [(1,2),(2,3),(3,4)]:
  r=m[f'drain_{i}_settled'];assert r['played_0']==1 and r['ball_number']==ball and r['phase']==(0 if i==3 else 1)
 assert int(m['drain_3_settled']['score'])==46000000
 new=m['new_game_reset'];assert new['phase']==1 and new['played_0']==0 and new['ball_number']==1 and int(new['score'])==0
 assert [e['scan']for e in t['inputs']if e['action']=='key'and e['down']]==[0x1e,0x30,0x2e,0x1c]
 assert len(set(t['highscore_sha256']))>1
 assert t['original_reset_exact']
 return dict(asteroid_awards=[5000000,5500000,6000000],ordinary_trap_award=500000,ramp_asteroid_guard=True,expiry_steps=12001,played_survives_ball_changes=True,F1_clears_played=True,final_score=46000000,additional_20m_source='0x4413d5; narrative meaning UNKNOWN')
