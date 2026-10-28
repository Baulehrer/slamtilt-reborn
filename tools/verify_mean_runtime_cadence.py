#!/usr/bin/env python3
"""Actual4049e0 budget consumption and4071e8 dispatch, service bodies adapted."""
import json,struct,hashlib
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EIP
R=Path(__file__).resolve().parents[1];image=(R/'build/mean-prepared/pe-data.bin').read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
events=[]
services={0x406840:'rng',0x4084bc:'flippers',0x408874:'physics',0x40671c:'service40671c',0x4086b8:'service4086b8',0x4072cc:'bonus',0x1003000:'table_display',0x1003010:'table_overlay'}
def hook(uc,a,n,c):
 if a==0x404b87:uc.emu_stop();return
 if a in services:
  events.append(services[a]);sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,hook);cases=[]
for mode,overlay in [(2,0),(3,0),(4,0),(2,1)]:
 for budget in [0,1,4,5,6,19,20,21,24,25,39,40,41,100]:
  u.mem_write(0x400000,image)
  for a,v in [(0x43e740,0x1001000),(0x1001004,0x1001100),(0x1001108,0x1001200),(0x100123c,0x1003000),(0x1001228,0x1003010),(0x43e828,0x1002000),(0x43e7a0,mode),(0x43e7b4,overlay),(0x43e81c,0),(0x43e780,6),(0x43e848,budget),(0x43e844,budget),(0x43e830,0)]:put(a,v)
  events.clear();u.reg_write(UC_X86_REG_ESP,0x100f000);u.emu_start(0x4049e0,0,count=10000);assert u.reg_read(UC_X86_REG_EIP)==0x404b87
  step=['rng','flippers']+(['physics'] if mode!=3 and not overlay else [])+['service40671c','service4086b8']
  display=['table_overlay'] if overlay else ['bonus'] if mode==3 else ['table_display']
  expected=step*(budget//5)+display*(budget//20)
  assert events==expected,(mode,overlay,budget,events,expected)
  assert get(0x43e848)==budget%5 and get(0x43e844)==budget%20 and get(0x43e830)==budget//20
  cases.append(dict(mode=mode,overlay=overlay,budget_ms=budget,remaining_physics_ms=get(0x43e848),remaining_display_ms=get(0x43e844),events=events.copy()))
(R/'analysis/traces/mean-runtime-cadence-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Actual4049e0..404b87 and4071e8 dispatch; controlled mode/overlay/budgets, service bodies adapted. Original batches physics before presentation; native fixed5ms policy interleaves50Hz display. No wall-clock jitter or live mode transition proof.',cases=cases),separators=(',',':'))+'\n');print('PASS',len(cases),'original runtime budget/dispatch cases')
