#!/usr/bin/env python3
"""Actual415330 mode6 side Tilt: actual first helpers, continued side logic."""
import itertools,json,struct,subprocess,sys
from pathlib import Path
exec((Path(__file__).parent/'trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
from unicorn.x86_const import UC_X86_REG_EDX,UC_X86_REG_EBX
calls=[]; samples=[]; transfer_count=0; current_cb=0
put(0x1004004,0x1000080)
def service(uc,a,n,ctx):
 global transfer_count
 if a==0x417068:
  transfer_count+=1
  return
 if a==0x200ff00 and uc.reg_read(UC_X86_REG_EAX)==0x437dec:
  assert uc.reg_read(UC_X86_REG_EDX)==6 and uc.reg_read(UC_X86_REG_EBX)==5
  samples.append(a)
 if a in [0x417068,0x416fe0]:
  calls.append(hex(a));stub(uc,a,n,ctx)
for a in [0x417068,0x416fe0,0x200ff00]:u.hook_add(UC_HOOK_CODE,service,begin=a,end=a)
image=bytes(u.mem_read(0x400000,0x100000));runtime=bytes(u.mem_read(0x1000000,0x10000));cases=[];expected=[]
for cb,timer,gate,count,bits,blocked,slotclock,busy,occupied in itertools.product([2,4],[-4,-2,-1,0,1],[-1,0],[1,3],[0,7],[0,1],[0,2],[False,True],[False,True]):
 u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime)
 b=bytearray(100);struct.pack_into('<ii',b,0,280<<16,285<<16);struct.pack_into('<HH',b,88,3,cb);u.mem_write(0x1000000,bytes(b))
 put(0x1001030,6);put(0x1001000,count+(1 if occupied else 0));put(0x100201c,1)
 # Occupancy list includes ball itself and zero inactive entries; only actual callback3 blocker.
 for j in range(1,5):
  addr=0x1000080+j*128;put(0x1004000+j*4,addr);other=bytearray(100)
  if j==1 and occupied:struct.pack_into('<HH',other,88,3,3)
  u.mem_write(addr,bytes(other))
 initial=dict(callback=cb,timer=timer,gate=gate,count=count+(1 if occupied else 0),captures=[0 if bits&(1<<i) else -1 for i in range(3)],blocked=blocked,slot=[-1,slotclock,1],field38=2,tilt=True,ball=list(b),slot3=[0 if busy else -1,100,0],callback3_occupied=occupied)
 for a,v in [(0x43f380,timer),(0x43f370,timer),(0x43f364,gate)]+list(zip([0x43f38e,0x43f368,0x43f36c],initial['captures'])):u.mem_write(a,struct.pack('<h',v))
 for a,v in [(0x438b40,blocked),(0x438b38,2)]:put(a,v)
 for addr,values in [(0x438b68 if cb==2 else 0x438b80,initial['slot']),(0x438b74,initial['slot3']),(0x438b50,[0,0,0])]:
  for off,v in enumerate(values):put(addr+off*4,v)
 calls.clear();scores.clear();samples.clear();transfer_count=0;current_cb=cb
 put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x415330,0x200fff0,count=10000)
 output=dict(state=word(0x1000058),timer=word(0x43f380 if cb==2 else 0x43f370),gate=word(0x43f364),captures=[word(a) for a in [0x43f38e,0x43f368,0x43f36c]],slot=[get((0x438b68 if cb==2 else 0x438b80)+i*4) for i in range(3)],field38=get(0x438b38),score=sum(scores),player08=get(0x1003008),transfer=False,lamp='0x416fe0' in calls,ball=list(u.mem_read(0x1000000,100)),slot3=[get(0x438b74+i*4) for i in range(3)],slot50=[get(0x438b50+i*4) for i in range(3)],samples=len(samples),early_transfer_count=int(cb==4))
 cases.append(initial);expected.append(output)
actual=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases),text=True))
assert len(actual)==len(expected)
for i,(a,b) in enumerate(zip(actual,expected)):
 if a!=b:print('FAIL',i,{k:(a[k],b[k]) for k in a if a[k]!=b[k]},cases[i]);raise SystemExit(1)
(ROOT/'analysis/traces/mean-tilt-mode6-side-original.json').write_text(json.dumps(dict(scope=__doc__+' First416d08/417068 actual; all417068 actual;416fe0 recorded/stubbed; score/SFX boundary recorded; full100bytes, timers, gates,slots,bonus exact. Seeded context, no whole table.',cases=len(cases),differences=0,records=[dict(input=c,output=e) for c,e in zip(cases,expected)]),separators=(',',':'))+'\n')
print('PASS',len(cases),'cases')
