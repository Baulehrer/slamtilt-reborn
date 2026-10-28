"""Earned bank, identical physical contact, consumed charge and source grace."""
def fixed(b,o):return int.from_bytes(bytes(b[o:o+4]),'little',signed=True)/65536

def contracts(t):
 m={x['label']:x for x in t['milestones']};on=t['case']=='kickback-on';r=m['sidelane_response'];end=m['sidelane_80_steps'];assert t['original_reset_exact']
 if not on:
  assert m['before_sidelane']['grey_flags']==[0,1,1,1] and m['before_sidelane']['kickback_charge']==0
  assert r['kickback_charge']==0 and r['kickback_grace']==65535
  assert 8<fixed(r['ball'],0)<9 and 531<fixed(r['ball'],4)<532
  assert fixed(end['ball'],4)>540
  return dict(unearned_guard=True,three_lamps_insufficient=True,unarmed_y_after80=fixed(end['ball'],4))
 assert [m['grey_'+str(i)]['grey_flags']for i in range(4)]==[[1,0,0,0],[1,1,0,0],[1,1,1,0],[0,0,0,0]]
 assert m['before_sidelane']['kickback_charge']==65535
 assert r['kickback_charge']==0 and r['kickback_grace']==250
 assert 12<fixed(r['ball'],0)<13 and 532<fixed(r['ball'],4)<533
 assert fixed(end['ball'],4)==400 and m['saved_ball_free']['state']==2
 repeat=m['grace_repeat_response'];assert repeat['kickback_charge']==0 and 0<repeat['kickback_grace']<250
 assert repeat['ball'][:32]==r['ball'][:32]
 assert repeat['kickback_grace']==m['saved_ball_free']['kickback_grace']
 expiry=m['grace_expired']['tick'];activation=r['tick']
 assert t['globals'][expiry-1]['frame_count']-t['globals'][activation-1]['frame_count']==251
 assert m['grace_expired']['kickback_grace']==65535
 expired=m['expired_response'];assert expired['kickback_charge']==0 and 8<fixed(expired['ball'],0)<9 and 531<fixed(expired['ball'],4)<532
 assert m['rearm_grey_3']['kickback_charge']==65535 and m['rearm_grey_3']['grey_flags']==[0,0,0,0]
 second=m['rearmed_response'];assert second['kickback_charge']==0 and second['kickback_grace']==250 and second['ball'][:32]==r['ball'][:32]
 return dict(earned_four_lamps=True,charge_consumed=True,static_callback_impulse_y=-3,save_y_after80=400,saved_ball_returns_free=True,grace_repeat=True,expiry_50hz_frames=251,expired_guard=True,rearm_and_second_save=True)
