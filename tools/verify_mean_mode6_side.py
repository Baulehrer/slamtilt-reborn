#!/usr/bin/env python3
import itertools,json,struct,subprocess
from pathlib import Path
exec((Path(__file__).parent/'trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
calls=[]
def service(uc,a,n,ctx):calls.append(hex(a));stub(uc,a,n,ctx)
for a in [0x417068,0x416fe0]:u.hook_add(UC_HOOK_CODE,service,begin=a,end=a)
image=bytes(u.mem_read(0x400000,0x100000));runtime=bytes(u.mem_read(0x1000000,0x10000));cases=[];expected=[]
for cb,timer,gate,count,bits,blocked,slotclock in itertools.product([2,4],[-4,-3,-2,-1,0,1,32767,-32768],[-1,0],[1,2,3,4],range(8),[0,1],[0,2]):
 u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime);b=bytearray(100);struct.pack_into('<HH',b,88,3,cb);u.mem_write(0x1000000,bytes(b));put(0x1001030,6);put(0x1001000,count);put(0x100201c,0)
 initial=dict(callback=cb,timer=timer,gate=gate,count=count,captures=[0 if bits&(1<<i) else -1 for i in range(3)],blocked=blocked,slot=[-1,slotclock,1],field38=2)
 for a,v in [(0x43f380,timer),(0x43f370,timer),(0x43f364,gate)]+list(zip([0x43f38e,0x43f368,0x43f36c],initial['captures'])):u.mem_write(a,struct.pack('<h',v))
 for a,v in [(0x438b40,blocked),(0x438b38,2)]:put(a,v)
 for off,v in enumerate(initial['slot']):put((0x438b68 if cb==2 else 0x438b80)+off*4,v)
 calls.clear();scores.clear();put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x415330,0x200fff0,count=10000)
 output=dict(state=word(0x1000058),timer=word(0x43f380 if cb==2 else 0x43f370),gate=word(0x43f364),captures=[word(a) for a in [0x43f38e,0x43f368,0x43f36c]],slot=[get((0x438b68 if cb==2 else 0x438b80)+i*4) for i in range(3)],field38=get(0x438b38),score=sum(scores),player08=get(0x1003008),transfer='0x417068' in calls,lamp='0x416fe0' in calls)
 cases.append(initial);expected.append(output)
subprocess.run(['c++','-std=c++17','-Isrc','-Ibuild/native/_deps/json-src/include','tests/mean_mode6_side_probe.cpp','src/physics/mean_mode6_side.cpp','src/physics/mean_step.cpp','src/physics/mean_material_bundle.cpp','-o','build/oracle/mean_mode6_side_probe'],check=True)
actual=json.loads(subprocess.check_output(['build/oracle/mean_mode6_side_probe'],input=json.dumps(cases),text=True))
assert actual==expected,next(((i,a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b),None)
(ROOT/'analysis/traces/mean-mode6-side-fixture.json').write_text(json.dumps(dict(scope='Actual415330 mode6 state3 callback2/4, shared+1c0; transfer417068/lamp416fe0 observed then stubbed; score service observed; all timers/gates/slots exact',cases=cases,expected=expected),separators=(',',':'))+'\n')
print(json.dumps(dict(cases=len(cases),differences=0)))
