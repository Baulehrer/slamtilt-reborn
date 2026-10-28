#!/usr/bin/env python3
"""Original capture/RNG/release followed by bounded physical flights, not live play."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP,UC_X86_REG_EIP
R=Path(__file__).resolve().parents[1]
ns={'__file__':str(R/'tools/trace_mean_multiball_flight.py')}
exec((R/'tools/trace_mean_multiball_flight.py').read_text().split('u.mem_write(0x1000000,bytes(100));run')[0],ns)
u,put,run=ns['u'],ns['put'],ns['run'];prep=R/'build/mean-prepared'
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
def word(a,v):u.mem_write(a,struct.pack('<H',v&0xffff))
def w(a):return struct.unpack('<h',u.mem_read(a,2))[0]
def tls(uc,a,n,data):
 uc.reg_write(UC_X86_REG_EAX,0x1009000);sp=uc.reg_read(UC_X86_REG_ESP)
 uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,tls,begin=0x422f36,end=0x422f36)
def switches(uc,a,n,data):
 sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,switches,begin=0x408b04,end=0x408b04)
def drain(uc,a,n,data):uc.emu_stop()
u.hook_add(UC_HOOK_CODE,drain,begin=0x40898b,end=0x40898b)
base=json.loads((R/'analysis/traces/mean-flight-100.json').read_text());cases=[];capture=[];flights=[];summary=[];flightcases=[]
work=R/'build/oracle/capture-flight';work.mkdir(parents=True,exist_ok=True)
for idx,seed in enumerate([1,1996,0xffffffff]):
 b=bytearray(struct.pack('<25I',*base['initial_state']['raw_words']))
 for o,v in [(0,14<<16),(4,14<<16),(8,14<<16),(12,14<<16),(20,0),(24,0)]:struct.pack_into('<I',b,o,v)
 for o,v in [(0x58,3),(0x5a,1)]:struct.pack_into('<H',b,o,v)
 # Fully explicit supplied capture context, no original caller invariant assumed.
 put(0x1001030,4);put(0x43e834,0);put(0x43e7a8,0);put(0x1009000,seed)
 for a,v in [(0x43f36a,50),(0x43f364,0),(0x43f394,-1),(0x43f1f2,6),(0x43f200,0),(0x43f202,0),(0x43f1fa,0)]:word(a,v)
 for j,v in enumerate([-1,100,0]):put(0x438b5c+j*4,v)
 u.mem_write(0x1000000,bytes(b));run(0x406840,0)
 cases.append(dict(seed=seed,ball=list(b)));rows=[]
 for tick in range(300):
  ns['scores'].clear();run(0x406840,0);put(0x100103c,get(0x43e7ac))
  run(0x415330,0x1000000);assert u.reg_read(UC_X86_REG_EIP)==0x200fff0
  if tick%4==3 and ns['get'](0x438b5c)>=0:put(0x438b5c,ns['get'](0x438b5c)-1)
  bb=list(u.mem_read(0x1000000,100));rows.append(dict(ball=bb,timer=w(0x43f36a),slot=[ns['get'](0x438b5c+j*4) for j in range(3)],score=sum(ns['scores']),seed=get(0x1009000),accumulator=get(0x43e7a8),rng=get(0x43e7ac)))
  if bb[88]==2:break
 assert len(rows)==152 and sum(r['score'] for r in rows)==500000
 capture.append(rows)
 released=rows[-1]['ball'];trace=work/f'release-{idx}.json';trace.write_text(json.dumps({'initial_state':{'raw_words':list(struct.unpack('<25I',bytes(released)))}}))
 # Actual4088f0 physical path; switches and point forces explicitly suppressed.
 put(0x43d860,0);put(0x43d864,0);put(0x4298a4,0)
 states=[released];stop='2000ticklimit'
 for tick in range(2000):
  run(0x4088f0,0);pc=u.reg_read(UC_X86_REG_EIP)
  states.append(list(u.mem_read(0x1000000,100)))
  if pc==0x40898b:stop='actual40898bdraincallbackboundary';break
  assert pc==0x200fff0,hex(pc)
  x,y=struct.unpack_from('<ii',bytes(states[-1]))
  if not(8<=x>>16<312 and 8<=y>>16<616):stop='coordinateboundary';break
 flights.append(states);summary.append(dict(seed=seed,capture_ticks=152,flight_ticks=len(states)-1,stop=stop))
 flightcases.append(dict(trace=str(trace),poses=list(struct.unpack('<27I',(prep/'flipper-state.bin').read_bytes())),globals=list(struct.unpack('<40I',(prep/'engine-globals.bin').read_bytes())),steps=len(states)-1,include_terminal=True))
a=json.loads(subprocess.run([sys.argv[1]],input=json.dumps(cases),capture_output=True,text=True,check=True).stdout)
assert len(a)==len(capture)
for ci,(aa,bb) in enumerate(zip(a,capture)):
 assert len(aa)==len(bb)
 for t,(x,y) in enumerate(zip(aa,bb)):assert x==y,('capture',ci,t,x,y)
cf=work/'flight-cases.json';cf.write_text(json.dumps(flightcases))
a=json.loads(subprocess.check_output([sys.argv[2],str(next((R/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))),str(prep),str(R/'analysis/traces/mean-flight-100.json'),str(cf)],text=True))
assert len(a)==len(flights)
for ci,(aa,bb) in enumerate(zip(a,flights)):
 assert len(aa)==len(bb),('flight length',ci,len(aa),len(bb))
 for t,(x,y) in enumerate(zip(aa,bb)):assert x==y,('flight',ci,t,[i for i in range(100) if x[i]!=y[i]])
report=dict(build_sha256=base['build_sha256'],scope='Controlled supplied captured ball/slots/mode4/RNG seeds; actual406840/415330/416be4 with only CRT TLS pointer and score/audio adapters. Subsequent actual4088f0 physical steps with cached rest flippers, no point forces and suppressed408b04 switches; stop at actual40898b before table drain callback. Not live gameplay or whole-table/next-ball equivalence.',cases=cases,capture=capture,flights=flights,summary=summary)
(R/'analysis/traces/mean-capture-flight-original.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
print('PASS',sum(map(len,capture)),'capture/RNG/release states and',sum(map(len,flights)),'complete100-byte flight states;',summary)
