#!/usr/bin/env python3
"""4072cc dispatcher oracle. DMD drawing stubbed; table+38 returns explicit inputs."""
import argparse,hashlib,json,struct,subprocess,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--replay',action='store_true');a=p.parse_args();f=ROOT/'analysis/traces/mean-bonus-display-original.json'
if a.replay:d=json.loads(f.read_text())
else:
 from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
 from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESP,UC_X86_REG_EIP
 image=(ROOT/'build/mean-prepared/pe-data.bin').read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 events={};c={}
 def hook(uc,addr,size,ctx):
  if addr in (0x407794,0x4077e4):events['finish' if addr==0x407794 else 'rotate_only']=True;uc.emu_stop();return
  if addr==0x100fff0:uc.emu_stop();return
  if addr in (0x4060a4,0x4060f8,0x406280,0x40617c,0x406680,0x1000100,0x1000200):
   if addr==0x1000100:events['award']=True;events['score_argument']=uc.reg_read(UC_X86_REG_EAX)
   if addr==0x1000200:
    stage=uc.reg_read(UC_X86_REG_EAX)
    if stage==0:events['initialize']=True
    else:events['callback_stage']=stage
    uc.reg_write(UC_X86_REG_EAX,c['callback_result'] if stage else 0)
   sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+({0x406280:4,0x40617c:8}.get(addr,0)))
 u.hook_add(UC_HOOK_CODE,hook)
 for addr,val in [(0x43e740,0x1001000),(0x1001004,0x1001100),(0x1001108,0x1001200),(0x1001238,0x1000200),(0x43d858,0x1002000),(0x43d8a0,0x1000100)]:put(addr,val)
 cases=[];expected=[];rng=random.Random(4072)
 for n in range(1200):
  c=dict(phase=n%10,timer=rng.choice([0,1,49,50,61,62,63,111,112,113,123,124,125,0xffffffff]),step=rng.choice([1,4]),field_43e734=rng.choice([0,3]),bonus_total=123456,field_43e718=99,bonus=rng.choice([0,500000,0xffffffff]),suppressed=n%2,multiplier=rng.choice([0,1,2,32768,65535]),callback_result=rng.choice([0,1,2]))
  for key,addr in [('phase',0x43e73c),('timer',0x43e7e4),('step',0x43e738),('field_43e734',0x43e734),('bonus_total',0x43e714),('field_43e718',0x43e718),('suppressed',0x43d864)]:put(addr,c[key])
  put(0x1002008,c['bonus']);put(0x1002010,c['multiplier']<<16);put(0x43e708,0);put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000)
  events=dict(award=False,score_argument=0,finish=False,rotate_only=False,initialize=False,callback_stage=-1);
  try:u.emu_start(0x4072cc,0x100fff0,count=2000)
  except Exception as ex:raise RuntimeError((n,c,hex(u.reg_read(UC_X86_REG_EIP)),hex(u.reg_read(UC_X86_REG_ESP)))) from ex
  out={k:get(addr) for k,addr in [('phase',0x43e73c),('timer',0x43e7e4),('step',0x43e738),('bonus_total',0x43e714),('field_43e718',0x43e718)]};out.update(events);cases.append(c);expected.append(out)
 d=dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='4072cc..407794/4077e4; drawing stubs and explicit table+38 return. Does not prove callback durations or invocation frequency.',cases=cases,expected=expected);f.write_text(json.dumps(d,separators=(',',':'))+'\n')
actual=json.loads(subprocess.check_output([str(a.native)],input=json.dumps(dict(cases=d['cases'])),text=True))
assert actual==d['expected'],next((n,d['cases'][n],x,y) for n,(x,y) in enumerate(zip(actual,d['expected'])) if x!=y)
print(json.dumps(dict(cases=len(actual),differences=0)))
