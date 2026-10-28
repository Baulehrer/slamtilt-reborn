#!/usr/bin/env python3
"""Actual mode6 announcement through405f98, scheduler4071e8,410b00,413b04."""
from pathlib import Path
s=(Path(__file__).parent/'verify_mean_reward_display.py').read_text().split('rows=[]')[0]
s=s.replace('callback=0x410910 if reward2 else 0x410a34','callback=0x410b00')
exec(s)
for off in [0x48,0x4c,0x50]:put(0x1002000+off,0x200ff00)
u.mem_write(0x43f382,struct.pack('<h',-1));rows=[]
for tick in range(270):
 put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.emu_start(0x4071e8,0x200fff0,count=4000)
 rows.append(dict(tick=tick+1,state=get(0x43e780),active=get(0x43e784),frame=get(0x43e78c),gate=struct.unpack('<h',u.mem_read(0x43f382,2))[0],shared14=get(0x43e784)))
clear=next(r['tick'] for r in rows if r['gate']==0)
assert clear==268,(clear,rows[clear-2:clear+2])
report=dict(scope='Actual405f98 start and4071e8 scheduler, actual410b00 clears382; DMD bitmap/font services stubbed. Noqueuedinterruptions',callback='0x410b00',gate_writer='0x410c0e',callback_clear_frame=267,display_clear_tick=clear,states=rows)
(ROOT/'analysis/traces/mean-mode6-display-fixture.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
print(json.dumps(dict(clear_tick=clear,transitions=[r for i,r in enumerate(rows) if i==0 or any(r[k]!=rows[i-1][k] for k in ['state','active','gate'])])))
