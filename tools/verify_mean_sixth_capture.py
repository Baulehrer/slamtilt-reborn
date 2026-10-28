#!/usr/bin/env python3
"""Original sixth-award capture through transfer and release, bounded DMD/audio."""
from pathlib import Path
import json, subprocess
exec((Path(__file__).parent/'trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
probe=ROOT/'build/oracle/mean_capture_tick_probe'
subprocess.run(['c++','-std=c++17','-Isrc','-Ibuild/native/_deps/json-src/include','tests/mean_capture_tick_probe.cpp','src/physics/mean_capture_tick.cpp','src/physics/mean_step.cpp','src/physics/mean_material_bundle.cpp','-o',str(probe)],cwd=ROOT,check=True)
awards=[]
def score_hook(uc,a,n,c):
 awards.append(uc.reg_read(UC_X86_REG_EAX));sp=uc.reg_read(UC_X86_REG_ESP)
 uc.reg_write(UC_X86_REG_EIP,get(sp)&0xffffffff);uc.reg_write(UC_X86_REG_ESP,sp+4)
put(0x1002058,0x200ff20)
u.hook_add(UC_HOOK_CODE,score_hook,begin=0x200ff20,end=0x200ff20)
fixtures=[]
for selection in [0,1,2,32767,-32768]:
 for address,value in [(0x43f204,5),(0x43f1fe,selection),(0x43f200,7),(0x43f202,9),(0x43f1fa,32767),(0x43f380,50),(0x43f364,0),(0x43f392,0)]:u.mem_write(address,struct.pack('<H',value&65535))
 for address,values in [(0x438b68,[-1,100,0]),(0x438b74,[-1,0,0]),(0x438b50,[0,0,0])]:
  for i,v in enumerate(values):put(address+i*4,v)
 put(0x1001030,2)
 b=bytearray(100);struct.pack_into('<ii',b,0,26*65536,279*65536);struct.pack_into('<HH',b,0x58,3,2);u.mem_write(0x1000000,bytes(b));expected=[]
 for tick in range(1200):
  awards.clear();put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000)
  u.emu_start(0x415330,0x200fff0,count=20000)
  if tick%4==3:
   for address in [0x438b68,0x438b74]:
    if get(address)>=0:put(address,get(address)-1)
  expected.append(dict(ball=list(u.mem_read(0x1000000,100)),slot2=[get(0x438b68+i*4) for i in range(3)],slot3=[get(0x438b74+i*4) for i in range(3)],slot50=[get(0x438b50+i*4) for i in range(3)],timer=word(0x43f380),gate=word(0x43f364),field204=word(0x43f204),score=sum(awards),field1fe=word(0x43f1fe),field200=word(0x43f200),field202=word(0x43f202),field1fa=word(0x43f1fa)))
  if word(0x1000058)==2:break
 initial=dict(ball=list(b),field204=5,field1fe=selection,field200=7,field202=9,field1fa=32767,steps=1200,sixth=True)
 actual=json.loads(subprocess.check_output([str(probe)],input=json.dumps(initial),text=True))
 diff=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
 if diff:
  i=diff[0];print(selection,i,{k:(actual[i][k],expected[i][k]) for k in expected[i] if actual[i][k]!=expected[i][k]})
 assert not diff and len(actual)==len(expected) and expected[-1]['ball'][88]==2
 fixtures.append(dict(initial=initial,expected=expected))
report=dict(cycles=len(fixtures),states=sum(len(f['expected']) for f in fixtures),steps=[len(f['expected']) for f in fixtures],differences=0)
(ROOT/'analysis/traces/mean-sixth-capture-fixture.json').write_text(json.dumps(dict(scope='Original415330, actual40f754 delay740, presentation services bounded, full ball and local state',cases=fixtures),separators=(',',':'))+'\n')
(ROOT/'analysis/traces/mean-sixth-capture-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
