"""Bounded earned admissions, original rewards and physical mode returns."""
MODES={'bat':(9,3),'grave':(8,2),'meatball':(10,1),'zombie':(5,1),'witch':(11,2),'twice':(6,3),'vampires':(7,4)}
def contracts(t):
 assert t['original_reset_exact'] and t['table']=='demon'
 name=t['case'].removeprefix('mode-');phase,selection=MODES[name];m={r['label']:r for r in t['milestones']};p=t['payments'];started=m['mode_started'];assert started['phase']==phase
 assert m['mode_returned']['phase']==2 and m['mode_returned']['state']==2
 if name in ['bat','grave','meatball']:
  assert m['unarmed_wolf_guard_contact']['state']==3 and m['unarmed_wolf_guard_released']['phase']==2
  assert m['wolf_select_done']['wolf_selected']==selection and started['wolf_selected']==0
  assert started['wolf_played']==[int(i==selection-1)for i in range(3)]
 else:
  assert m['unarmed_spirit_guard_done']['phase']==2 and m['unarmed_spirit_guard_done']['spirit_selected']==0
  assert m['spirit_arm_contact']['state']==3 and m['spirit_arm_released']['spirit_selected']==1
  assert [m['spirit_cycle_'+str(i)+'_done']['spirit_selected']for i in range(selection-1)]==list(range(2,selection+1))
  assert started['spirit_selected']==0 and started['spirit_played']==[int(i==selection-1)for i in range(4)]
 awards=lambda address:[r['amount']for r in p if r['return_address']==address]
 out=dict(phase=phase,selector=selection,earned_admission=True,unarmed_guard=True,return_phase=2,ordinary_awards_retained=True)
 if name=='bat':assert awards('0x418c44')==[25000000];out['bat_hit']=25000000
 if name=='grave':assert awards('0x4190c8')==[46370000];out['treasure_observed']=46370000;out['scope']='One deterministic treasure selection/value, not all seeds/coffins'
 if name=='meatball':assert awards('0x414c72')==[50000000];out['escape_award']=50000000
 if name=='vampires':
  assert awards('0x41918e')==[10000000]*4 and awards('0x4191c9')==[20000000]
  assert m['reward_ramp_3_done']['timer']==0
  out.update(vampires=4,per_vampire=10000000,final_extra=20000000)
 if name=='zombie':
  assert awards('0x4104c6')==[5000000]*4;out['ramp_awards']=[5000000]*4
 if name=='witch':
  assert awards('0x4104c6')==[2000000]*4+[5000000];out['ramp_award']=2000000;out['trap_award']=5000000
 if name=='twice':
  assert max(r[1]for r in t['lifecycle'])==2 and awards('0x416209')==[15000000]
  out.update(spawned_pool=2,clock_head_award=15000000)
 return out
