"""Bounded Demon first rule bank plus earned scoreboard lifecycle."""
def contracts(t):
 assert t['original_reset_exact']and t['table']=='demon';m={r['label']:r for r in t['milestones']}
 assert m['one_six']['flags']==[4294967295,0,0]and m['duplicate_guard']['flags']==m['one_six']['flags']
 assert m['flipper_cycle']['flags']==[0,0,4294967295]
 assert [m['six_bank_'+str(i)]['multiplier']for i in range(5)]==[2,4,6,8,8]
 assert all(m['six_bank_'+str(i)]['flags']==[0]*3 for i in range(5))
 assert [p['amount']for p in t['payments']if p['return_address']=='0x4197cb']==[15000000]
 assert m['after_drain_1']['multiplier']==1 and m['after_drain_3']['phase']==0
 assert len(set(t['highscore_sha256']))==2
 assert [e['scan']for e in t['inputs']if e['action']=='key'and e['down']]==[0x1e,0x30,0x2e,0x1c]
 assert m['new_game']['score']=='000000000000'and m['new_game_launched']['phase']==2
 return dict(multiplier=[1,2,4,6,8],cap_award=15000000,flipper_cycle=True,duplicate_guard=True,physical_three_drains=True,initials='ABC',new_game=True,nonzero_bonus_payout_not_yet_proven=True)
