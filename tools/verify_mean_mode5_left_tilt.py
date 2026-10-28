#!/usr/bin/env python3
"""Bounded callback2 mode5 actual415330 incl416d08 and timer continuation."""
import sys
exec(open(__file__.replace('verify_mean_mode5_left_tilt.py','trace_mean_upper_capture.py')).read().split('b=bytearray(100)')[0])
count=[]
u.hook_add(UC_HOOK_CODE,lambda uc,a,n,c:uc.reg_write(UC_X86_REG_EAX,int(accepted)),begin=0x200ff10,end=0x200ff10)
u.hook_add(UC_HOOK_CODE,lambda uc,a,n,c:count.append(a),begin=0x416d08,end=0x416d08)
put(0x1002058,0x200ff20)
def score_stub(uc,a,n,c):
 scores.append(uc.reg_read(UC_X86_REG_EAX));sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp)&0xffffffff);uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,score_stub,begin=0x200ff20,end=0x200ff20)
cases=[];expected=[]
for accepted in [False,True]:
 for tilt in [False,True]:
  for timer in [50,1,0,-1,-2,-3,-32768]:
   for slot2 in [[-1,100,0],[-1,0,0],[-1,1,2],[-1,0,1]]:
    for occupied in [False,True]:
     b=bytearray(100);struct.pack_into('<ii',b,0,26<<16,279<<16);struct.pack_into('<HH',b,0x58,3,2)
     c=dict(accepted=accepted,tilt=tilt,ball=list(b),timer=timer,slot2=slot2,slot3=[0 if occupied else -1,100,0]);cases.append(c)
     put(0x1001030,5);put(0x100201c,int(tilt));put(0x43f05c,10000000);put(0x43f058,0);put(0x43f050,0);u.mem_write(0x43f3b4,b'\0\0');u.mem_write(0x43f1e6,b'\0\0');u.mem_write(0x43f380,struct.pack('<h',timer));u.mem_write(0x1000000,bytes(b))
     for a,arr in [(0x438b68,slot2),(0x438b74,c['slot3']),(0x438b50,[0,0,0])]:u.mem_write(a,struct.pack('<3i',*arr))
     count.clear();scores.clear();put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x415330,0x200fff0,count=10000)
     expected.append(dict(ball=list(u.mem_read(0x1000000,100)),timer=word(0x43f380),slot2=[get(0x438b68+i*4) for i in range(3)],slot3=[get(0x438b74+i*4) for i in range(3)],slot50=[get(0x438b50+i*4) for i in range(3)],field050=get(0x43f050),field058=get(0x43f058),field3b4=word(0x43f3b4),score=sum(scores),samples=len(count),ok=True))
exe=sys.argv[1];actual=json.loads(subprocess.check_output([exe],input=json.dumps(cases).encode()))
assert len(actual)==len(expected)
for i,(a,e) in enumerate(zip(actual,expected)):
 if a!=e:print('FAIL',i,{k:(a[k],e[k]) for k in a if a[k]!=e[k]},cases[i]);raise SystemExit(1)
(ROOT/'analysis/traces/mean-mode5-left-tilt-original.json').write_text(json.dumps(dict(scope='Actual415330 mode5 callback2; actual416d08, timer boundaries, occupied/delayed slots; score observed and41b8d0 rules stubbed; selection0 10M nonterminal award; accepted/rejected DMD and positive delay cases included',cases=len(cases),differences=0,records=[dict(input=c,output=e) for c,e in zip(cases,expected)]),separators=(',',':'))+'\n');print('PASS',len(cases))
