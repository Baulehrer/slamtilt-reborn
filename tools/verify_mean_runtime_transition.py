#!/usr/bin/env python3
"""Actual frame budget +bonus dispatcher +finish/reset; tick bodies adapted."""
import json,struct,hashlib
from pathlib import Path
from unicorn import UC_HOOK_CODE
R=Path(__file__).resolve().parents[1]
text=(R/'tools/verify_mean_drain_chain.py').read_text()
prefix=text.split('source=json.loads')[0].replace('if a in [0x100fff0,0x4078a6] or (a==0x407794 and not finish_call):','if a==0x100fff0:')
exec(prefix,globals())
source=json.loads((R/'analysis/traces/mean-capture-flight-original.json').read_text())
setup=text.split('for i in range(72):')[1].split(' cases.append')[0]
events=[]
runtime_services={0x406840:'rng',0x4084bc:'flippers',0x408874:'physics',0x40671c:'service40671c',0x4086b8:'camera_boundary',0x1003030:'table_display',0x1003040:'table_idle'}
def runtime(uc,a,n,c):
 if a==0x404b87:uc.emu_stop();return
 if a==0x4072cc:events.append('bonus');return
 if a in runtime_services:
  events.append(runtime_services[a]);sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,runtime);cases=[]
for i in [0,12,48,60]:
 for budget in [20,21,39,40,41,60,100]:
  exec('if True:'+setup,globals());call(0x408084,0x43e568)
  for a,v in [(0x43e828,0x1004000),(0x43e81c,0),(0x43e7b4,0),(0x43e780,6),(0x43e848,budget),(0x43e844,budget),(0x43e830,0),(0x43e73c,5),(0x43e7e4,112),(0x100123c,0x1003030),(0x1001234,0x1003040)]:put(a,v)
  events.clear();u.reg_write(UC_X86_REG_ESP,0x100f000);u.emu_start(0x4049e0,0,count=100000);assert u.reg_read(UC_X86_REG_EIP)==0x404b87
  step=['rng','flippers','service40671c','camera_boundary'];expected=step*(budget//5)+['bonus']
  for t in range(1,budget//20):expected+=['table_display']+(['table_idle'] if t>=2 else [])
  assert events==expected,(i,budget,events,expected)
  assert get(0x43e7a0)==1 and w(0x43e5c0)==65535
  assert w(0x43d6ee)==(1 if extra else 2) and w(0x43d6f0)==0
  assert get(0x43e848)==budget%5 and get(0x43e844)==budget%20
  cases.append(dict(context=i,budget_ms=budget,events=events.copy(),final=snapshot(),remaining_physics_ms=get(0x43e848),remaining_display_ms=get(0x43e844)))
(R/'analysis/traces/mean-runtime-transition-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='28 controlled frame batches actual4049e0/4071e8/4072cc/407794/419ad8/419b00; supplied terminal bonus state. RNG/flipper/physics/camera/table display/idle and presentation services adapted. All simulation budget consumed while bonus frozen; mode1 only resumes next frame. Not live wall-clock or native batching equivalence.',cases=cases),separators=(',',':'))+'\n');print('PASS',len(cases),'original bonus-end frame batches')
