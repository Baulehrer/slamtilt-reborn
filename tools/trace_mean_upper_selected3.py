#!/usr/bin/env python3
"""Selected3 callback-only cycle, excluding separate minigame/display dispatch."""
import json,struct
from pathlib import Path
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX
ROOT=Path(__file__).resolve().parents[1]
env={'__file__':str(ROOT/'tools/trace_mean_upper_capture.py')};exec((ROOT/'tools/trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0],env)
u=env['u'];put=env['put'];get=env['get'];word=env['word']
put(0x1002088,0x200ff00)
u.mem_write(0x43f1e6,struct.pack('<h',3));u.mem_write(0x43f394,struct.pack('<h',-1))
u.mem_write(0x43ec3c,b'\xa5'*480)
b=bytearray(100);struct.pack_into('<ii',b,0,14*65536,14*65536);struct.pack_into('<HH',b,0x58,3,1);u.mem_write(0x1000000,bytes(b))
result=[]
for i in range(400):
 before=len(env['scores']);put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x415330,0x200fff0,count=10000)
 if i%4==3:
  for a in [0x438b5c,0x438b68,0x438b74]:
   if get(a)>=0:put(a,get(a)-1)
 result.append(dict(timer=word(0x43f36a),gate=word(0x43f364),field394=word(0x43f394),field1f2=word(0x43f1f2),mode=get(0x1001030),shared44=get(0x1001044),slot1=[get(0x438b5c+j*4) for j in range(3)],slot20=[get(0x438b20+j*4) for j in range(3)],score=sum(env['scores'][before:]),ball=list(u.mem_read(0x1000000,100))))
 if word(0x1000058)==2:break
report={'scope':'Actual415330 selected3 secondcapture; actual423190 memset; service88/audio/score boundedret and service34handle1. Separate shared44 minigame dispatcher NOT executed. Callback-onlyrelease doesnotprove minigamecompleted.','states':result,'initialization':{'buffer43ec3c':list(u.mem_read(0x43ec3c,480)),'field3a4':word(0x43f3a4),'globals':{hex(a):get(a) for a in [0x43efe8,0x43f018,0x43eff8,0x43eff4,0x43eff0,0x43f010,0x43f00c,0x43f000,0x43f004,0x43efec,0x43f014,0x43effc,0x43efdc]},'shared':{hex(a):get(0x1001000+a) for a in [0x10,0x14,0x18,0x20,0x44]}}}
(ROOT/'analysis/traces/mean-upper-selected3-original.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
print(json.dumps({'steps':len(result),'initialization':{k:v for k,v in report['initialization'].items() if k!='buffer43ec3c'},'transitions':[{'tick':i+1,**{k:s[k] for k in ['timer','field394','field1f2','mode','shared44','slot1','slot20','score']}} for i,s in enumerate(result) if i in [0,50,51,len(result)-1]]}))
