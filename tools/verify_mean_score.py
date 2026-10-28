#!/usr/bin/env python3
"""Native numeric score and lower switch4 base award vs actual original x86."""
import json, random, struct, subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ESP
ROOT=Path(__file__).resolve().parents[1]
u=Uc(UC_ARCH_X86,UC_MODE_32)
for address,size in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000),(0x2100000,0x1000)]:u.mem_map(address,size)
u.mem_write(0x400000,(ROOT/'build/mean-prepared/pe-data.bin').read_bytes())
def put(a,v):u.mem_write(a,struct.pack('<I',v))
put(0x43d858,0x1004000);put(0x43f0d0,0x1002000);put(0x1002058,0x40560c)
put(0x43f068,0x1001000);put(0x1001030,1)
rng=random.Random(1996);cases=[];expected=[]
for operation in ['score','lower_score']:
 for i in range(320):
  initial=rng.choice([0,999999999999,9999999999,999999999,999999, rng.randrange(10**12)])
  points=rng.choice([0,25000,2**32-1,rng.randrange(2**32)])
  ball=bytearray(100);x=i; y=rng.randrange(450,608)
  struct.pack_into('<ii',ball,0,x*65536+rng.randrange(65536),y*65536+rng.randrange(65536))
  cases.append(dict(operation=operation,bytes=list(ball),initial_score=initial,points=points))
  u.mem_write(0x1000000,bytes(ball));u.mem_write(0x1004000,bytes.fromhex(f'{initial:012d}'))
  # Keep mode-specific additional awards/lamp paths outside this bounded slice.
  u.mem_write(0x43f1fc,b'\0\0');u.mem_write(0x43f37a,b'\0\0')
  put(0x200f000,0x2100000);u.reg_write(UC_X86_REG_ESP,0x200f000)
  u.reg_write(UC_X86_REG_EAX,points if operation=='score' else 0x1000000)
  u.emu_start(0x40560c if operation=='score' else 0x41c974,0x2100000,count=20000)
  assert u.reg_read(UC_X86_REG_ESP)==0x200f004
  expected.append(int(bytes(u.mem_read(0x1004000,6)).hex()))
p=ROOT/'build/oracle/score-cases.json';p.write_text(json.dumps(cases))
actual=json.loads(subprocess.check_output([str(ROOT/'build/native/mean_probe'),str(p),str(ROOT/'build/mean-prepared/lookup.bin')],text=True))
differences=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
report=dict(cases=len(cases),differences=differences,scope='40560c six-byte packed-BCD addition, wrap/carry; lower switch4 y450..607 acrossall320X; mode-specific additional awards disabled')
(ROOT/'analysis/traces/mean-score-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert actual==expected
# Native event dispatch must award once per observed lower switch entry.
command=[str(ROOT/'build/native/mean_sim_probe'),str(ROOT/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT'),str(ROOT/'build/mean-prepared'),str(ROOT/'analysis/traces/mean-flight-100.json'),'2500','cycle']
a=json.loads(subprocess.check_output(command,text=True));b=json.loads(subprocess.check_output(command,text=True))
assert a==b and a['score_events']>0 and a['score']==a['score_events']*25000
first=next(i for i,s in enumerate(a['samples']) if s['score']>0)
assert a['samples'][first]['score']==25000
# A held switch must not award every tick; score survives next-ball preparation.
held=[(x,y) for x,y in zip(a['samples'],a['samples'][1:])
      if x['layer']==y['layer']==0 and x['switch_mask']==y['switch_mask']==4]
assert held and all(x['score']==y['score'] for x,y in held)
next_ball=next(i for i,s in enumerate(a['samples'][first+1:],first+1) if s['state']==0)
assert a['samples'][next_ball]['score']==a['samples'][next_ball-1]['score']
report.update(native_score=a['score'],native_score_events=a['score_events'],native_deterministic=a==b)
(ROOT/'analysis/traces/mean-score-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
