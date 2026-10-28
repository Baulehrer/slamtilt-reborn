"""Bounded direction-switch/loop path contracts for the supported Retail build."""
def contracts(t):
 m={x['label']:x for x in t['milestones']};a=m['initial_direction'];b=m.get('mid_loop_selected',m['selected_direction']);end=m['loop_400_steps'];case=t['case']
 assert t['original_reset_exact'] and a['direction']==0 and a['passage']==65535
 toggled=case in ['lane-toggle','lane-live']
 assert b['direction']==(65535 if toggled else 0)
 assert b['direction_lamps'][:1]==([4]if toggled else [2]if case=='lane-double' else[0])
 assert end['state']==2 and end['phase']==2
 raw=bytes(t['states'][708]);assert int.from_bytes(raw[92:94],'little')==(13 if toggled else 11)
 assert int.from_bytes(raw[28:30],'little')==(5 if toggled else 25)
 # Entry point stays fixed; source-selected DAT path, not replacement physics.
 s=bytes(end['ball']);x=int.from_bytes(s[:4],'little',signed=True)/65536;y=int.from_bytes(s[4:8],'little',signed=True)/65536
 assert (70<x<110 and 260<y<300) if toggled else (220<x<260 and 415<y<460)
 return dict(direction=b['direction'],original_path_id_at_708=int.from_bytes(raw[92:94],'little'),end_xy=[x,y],actual_special_scan='0x1d',flipper_is_not_direction_switch=case=='lane-shift')
