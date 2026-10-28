#!/usr/bin/env python3
import json,struct,subprocess,sys
from pathlib import Path
exec((Path(__file__).parent/'verify_mean_capture_tick.py').read_text().split('b=bytearray(100)')[0])
base_raw=bytes(u.mem_read(0x43f000,0x3c0));cases=[];expected=[]
for mode in [1,2,3,4]:
 for timer in [-1,-2,-3]:
  for gate in [-1,0]:
   for armed in [0,-1]:
    for a6 in [0,1]:
     for blocked in [0,3,5]:
      for occupied in [False,True]:
       raw=bytearray(base_raw)
       for o,v in [(0x380,timer),(0x364,gate),(0x392,armed),(0x3a6,a6)]:struct.pack_into('<h',raw,o,v)
       b=bytearray(100);struct.pack_into('<ii',b,0,26<<16,279<<16);struct.pack_into('<HH',b,0x58,3,2)
       c=dict(ball=list(b),raw=list(raw),mode=mode,timer=timer,gate=gate,armed=armed,slot2=[-1,1,0],slot3=[0 if occupied else -1,100,0],slot5=[0 if occupied else -1,100,0],blocked=blocked)
       u.mem_write(0x43f000,bytes(raw));u.mem_write(0x1000000,bytes(b));put(0x1001030,mode);put(0x1001000,2 if blocked else 1);put(0x1004004,0x1000080)
       blocker=bytearray(100);struct.pack_into('<HH',blocker,0x58,3,blocked);u.mem_write(0x1000080,bytes(blocker))
       for a,arr in [(0x438b68,c['slot2']),(0x438b74,c['slot3']),(0x438b8c,c['slot5']),(0x438b50,[0,0,0])]:u.mem_write(a,struct.pack('<3i',*arr))
       put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x415330,0x200fff0,count=6000)
       after=bytes(u.mem_read(0x1000000,100));cases.append(c);expected.append(dict(ball=list(after),raw=list(u.mem_read(0x43f000,0x3c0)),mode=get(0x1001030),slot2=[get(0x438b68+i*4) for i in range(3)],slot3=[get(0x438b74+i*4) for i in range(3)],slot50=[get(0x438b50+i*4) for i in range(3)],sample=after[0x58]==7,ok=True))
exe=sys.argv[1] if len(sys.argv)>1 else str(ROOT/'build/native/mean_mode4_capture_probe')
a=json.loads(subprocess.check_output([exe],input=json.dumps(cases).encode()))
for i,(x,y) in enumerate(zip(a,expected)):
 if x!=y:print('FAIL',i,{k:(x[k],y[k]) for k in x if x[k]!=y[k]},cases[i]);raise SystemExit(1)
(ROOT/'analysis/traces/mean-mode4-capture-original.json').write_text(json.dumps(dict(scope='Actual415330 callback2 with actual41db1c allocation; DMD score service and41b8d0 stub; mode1..4 timer-1..-3, gates,392,3a6 and callback3/5 occupied states',cases=len(cases),differences=0,records=[dict(input=c,output=e) for c,e in zip(cases,expected)]),separators=(',',':'))+'\n');print('PASS',len(cases))
