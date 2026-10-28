#!/usr/bin/env python3
"""Original mode5 leftcapture throughcallback3 transfer; bounded firstaward."""
exec(open(__file__.replace('verify_mean_mode5_left.py','trace_mean_upper_capture.py')).read().split('b=bytearray(100)')[0])
put(0x1001030,5);put(0x43f05c,10000000);put(0x43f058,0);put(0x43f050,0)
u.mem_write(0x43f380,struct.pack('<h',50));u.mem_write(0x43f3b4,b'\0\0')
# Observe only score service, keeping sound separate.
put(0x1002058,0x200ff20)
def score_stub(uc,a,n,c):
 scores.append(uc.reg_read(UC_X86_REG_EAX));sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp)&0xffffffff);uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,score_stub,begin=0x200ff20,end=0x200ff20)
b=bytearray(100);struct.pack_into('<ii',b,0,26*65536,279*65536);struct.pack_into('<HH',b,0x58,3,2);u.mem_write(0x1000000,bytes(b));expected=[]
for tick in range(400):
 before=len(scores);put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x415330,0x200fff0,count=4000)
 if tick%4==3:
  for a in [0x438b68,0x438b74,0x438b50]:
   if get(a)>=0:put(a,get(a)-1)
 expected.append(dict(ball=list(u.mem_read(0x1000000,100)),slot2=[get(0x438b68+i*4) for i in range(3)],slot3=[get(0x438b74+i*4) for i in range(3)],slot50=[get(0x438b50+i*4) for i in range(3)],timer=word(0x43f380),score=sum(scores[before:]),field050=get(0x43f050),field058=get(0x43f058),field3b4=word(0x43f3b4),ok=True))
 if word(0x100005a)==3:break
probe=ROOT/'build/oracle/mean_mode5_left_probe'
subprocess.run(['c++','-std=c++17','-Isrc','-Ibuild/native/_deps/json-src/include','tests/mean_mode5_left_probe.cpp','src/physics/mean_mode5_left.cpp','src/physics/mean_mode_reset.cpp','src/physics/mean_upper_release.cpp','src/physics/mean_step.cpp','src/physics/mean_material_bundle.cpp','-o',str(probe)],cwd=ROOT,check=True)
actual=json.loads(subprocess.check_output([str(probe)],input=json.dumps(dict(ball=list(b),field05c=10000000)),text=True));diff=[i for i,(a,b) in enumerate(zip(expected,actual)) if a!=b]
report=dict(steps=len(expected),native_steps=len(actual),differences=diff,scope='Original415330 mode5callback2, 05c=10000000 verifiedmodeinit; service34stub actual40f754;41b8d0 externalrulesstub; all100ballbytes+timer+slots+score+localmodefields',events=[dict(step=i+1,score=e['score'],timer=e['timer']) for i,e in enumerate(expected) if e['score'] or i==len(expected)-1])
(ROOT/'analysis/traces/mean-mode5-left-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if diff:print('first',diff[0],{k:(expected[diff[0]][k],actual[diff[0]][k]) for k in expected[diff[0]] if expected[diff[0]][k]!=actual[diff[0]][k]})
assert not diff and len(actual)==len(expected)
