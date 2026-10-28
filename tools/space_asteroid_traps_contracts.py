"""Allfour actual capture IDs pay the shared Asteroid ladder."""
TRAPS=[(1,5000000,'0x441e9e'),(2,5500000,'0x4423ff'),(5,6000000,'0x443958'),(3,6500000,'0x4484d1')]
def contracts(t):
 m={r['label']:r for r in t['milestones']};s=m['matrix_started'];assert s['phase']==5 and s['mode']==0 and s['award']==5000000 and s['played_0']==1
 for cap,award,ret in TRAPS:
  a,b=m[f'capture_{cap}_before'],m[f'capture_{cap}_after'];assert a['phase']==b['phase']==5 and a['mode']==b['mode']==0
  assert a['award']==award and b['award']==award+500000
  assert int(b['score'])-int(a['score'])==award+500000
  calls=[p for p in t['payments']if a['tick']<p['tick']<=b['tick']]
  assert len(calls)==2 and sorted(p['amount']for p in calls)==[500000,award]
  assert any(p['amount']==award and p['return_address']==ret for p in calls)
 assert int(m['capture_3_after']['score'])==27250000 and t['original_reset_exact']
 return dict(captures=[1,2,5,3],asteroid_awards=[5000000,5500000,6000000,6500000],ordinary_trap_award=500000,next_award=7000000,final_score=27250000)
