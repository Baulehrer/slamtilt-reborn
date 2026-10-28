#!/usr/bin/env python3
"""Actual phase1 ramp and callback4 phase2/normal capture effects."""
import json,struct,subprocess,sys
from pathlib import Path
exec((Path(__file__).parent/'verify_mean_capture_tick.py').read_text().split('b=bytearray(100)')[0])
from unicorn.x86_const import UC_X86_REG_EDX,UC_X86_REG_EBX,UC_X86_REG_ECX
# Original services34,84,88 and40f754 presentation boundaries; actual416fe0.
events={}
def extra(uc,a,n,c):
 if a in [0x1000600,0x1000700,0x1000800,0x40f754]:
  sp=uc.reg_read(UC_X86_REG_ESP)
  if a==0x1000600:events['callback']=get(sp+12);uc.reg_write(UC_X86_REG_EAX,0)
  if a==0x1000700:events['audio84']=True
  if a==0x1000800:events['audio88']=True
  uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if a==0x1000600 else 8 if a==0x40f754 else 0))
 if a==0x416fe0:events['reset']=True
 if a==0x200ff00 and uc.reg_read(UC_X86_REG_EAX)==0x437dc8:
  assert uc.reg_read(UC_X86_REG_EDX)==6 and uc.reg_read(UC_X86_REG_EBX)==5
u.hook_add(UC_HOOK_CODE,extra)
put(0x1002034,0x1000600);put(0x1002084,0x1000700);put(0x1002088,0x1000800)
base=bytes(u.mem_read(0x43f000,0x3c0));cases=[];expected=[]
def run(c,entry):
 global events
 raw=bytes(c['raw']);u.mem_write(0x43f000,raw);u.mem_write(0x1000000,bytes(c['ball']));put(0x1001030,c['mode']);put(0x1001000,2 if c['blocked'] else 1);put(0x1004004,0x1000080)
 blocker=bytearray(100);struct.pack_into('<HH',blocker,0x58,3,c['blocked']);u.mem_write(0x1000080,bytes(blocker));u.mem_write(0x438a40,struct.pack('<h',17))
 for a,arr in [(0x438b80,c['slot80']),(0x438b74,c['slot3']),(0x438b50,[0,0,0])]:u.mem_write(a,struct.pack('<3i',*arr))
 put(0x438b38,c['b38']);put(0x438b40,c['b40']);put(0x438b2c,99);put(0x438b34,99);put(0x1003008,0)
 for o,v in [(0x10,77),(0x14,77),(0x18,77),(0x20,77),(0x44,0)]:put(0x1001000+o,v)
 put(0x43efd4,77);put(0x43efcc,77)
 events=dict(callback=0,reset=False,audio88=False,audio84=False);scores.clear()
 put(0x200f018,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1001000);u.reg_write(UC_X86_REG_EDX,0x1000000)
 if c['kind']=='entry':
  u.reg_write(UC_X86_REG_EAX,0x1002000);u.reg_write(UC_X86_REG_EBX,0x1000000);u.reg_write(UC_X86_REG_ECX,get(0x1000000))
 u.emu_start(entry,0x200fff0,count=6000)
 if get(0x1001044)==1:
  assert [get(0x1001000+o) for o in [0x10,0x14,0x18,0x20,0x44]]==[0,0,-1,0,1]
  assert get(0x43efd4)==get(0x43efcc)==0
 if events['reset']:
  assert get(0x438b2c)==0 and get(0x438b34)==-1
 entered=c['kind']=='entry' and word(0x1000058)==3
 if entered:events['reset']=True

 cases.append(c);expected.append(dict(raw=list(u.mem_read(0x43f000,0x3c0)),mode=get(0x1001030),a40=word(0x438a40),ball=list(u.mem_read(0x1000000,100)),slot80=[get(0x438b80+i*4) for i in range(3)],slot3=[get(0x438b74+i*4) for i in range(3)],slot50=[get(0x438b50+i*4) for i in range(3)],b38=get(0x438b38),score=sum(scores),bonus=get(0x1003008),start44=get(0x1001044)==1,sample=entered,**events))
for kind in ['ramp','capture']:
 for mode in ([1,2,3] if kind=='ramp' else [1,2,3,4,5]):
  for armed in [0,-1]:
   for timer in [-1,0,1]:
    for busy in [False,True]:
     for blocked in [0,3]:
      for b40 in [0,1]:
       raw=bytearray(base)
       for o,v in [(0x392,armed),(0x3a2,armed),(0x370,timer),(0x3b8,5)]:struct.pack_into('<h',raw,o,v)
       struct.pack_into('<I',raw,0x038,0)
       b=bytearray(100);struct.pack_into('<iiHH',b,0,280<<16,285<<16,0,0);struct.pack_into('<HH',b,0x58,3,4)
       c=dict(kind=kind,raw=list(raw),mode=mode,ball=list(b),slot80=[-1,1,0],slot3=[0 if busy else -1,100,0],b38=10,b40=b40,blocked=blocked)
       # Ramp requires armed; unarmedbranch skips to original epilogue41b615.
       run(c,0x41b002 if kind=='ramp' else 0x4164e1)
# Full mode5 callback4 countdown through actual417068 transfer, not just edges.
raw=bytearray(base)
for o,v in [(0x370,50),(0x3a2,0),(0x3b8,0)]:struct.pack_into('<h',raw,o,v)
b=bytearray(100);struct.pack_into('<ii',b,0,280<<16,285<<16);struct.pack_into('<HH',b,0x58,3,4)
c=dict(kind='capture',raw=list(raw),mode=5,ball=list(b),slot80=[-1,200,0],slot3=[-1,100,0],b38=10,b40=0,blocked=0)
sequence_ticks=0
while True:
 run(c,0x4164e1);sequence_ticks+=1;result=expected[-1]
 if struct.unpack_from('<H',bytes(result['ball']),0x5a)[0]!=4:break
 assert sequence_ticks<300
 c={**c,'raw':result['raw'],'ball':result['ball'],'slot80':result['slot80'],'slot3':result['slot3'],'b38':result['b38']}
assert sequence_ticks==251
for entry_mode in [1,2,3,4,5,6]:
 for x in [259,260,280]:
  for marker in [0,20]:
   for occupied in [-1,0]:
    for blocked in [0,4]:
     raw=bytearray(base);b=bytearray(100);struct.pack_into('<ii',b,0,x<<16,500<<16);struct.pack_into('<HHH',b,0x58,2,0,marker)
     c=dict(kind='entry',raw=list(raw),mode=entry_mode,ball=list(b),slot80=[occupied,17,0],slot3=[-1,100,0],b38=10,b40=0,blocked=blocked)
     run(c,0x41da51)
exe=sys.argv[1] if len(sys.argv)>1 else str(ROOT/'build/native/mean_mode4_right_entry_probe')
a=json.loads(subprocess.check_output([exe],input=json.dumps(cases).encode()))
for i,(x,y) in enumerate(zip(a,expected)):
 if x!=y:print('FAIL',i,[(hex(k),aa,bb) for k,(aa,bb) in enumerate(zip(x['raw'],y['raw'])) if aa!=bb],{k:(x[k],y[k]) for k in x if k!='raw' and x[k]!=y[k]},cases[i]['kind'],cases[i]['mode']);raise SystemExit(1)
(ROOT/'analysis/traces/mean-mode4-right-entry-original.json').write_text(json.dumps(dict(scope='Actual41b002 humanphase1, actual4164e1 callback4 modes1..5 through417068 plus251 sequential mode5 callback4 states;416fe0 actual,service34/84/88/40f754 recorded presentation boundaries; engine start writes and capture sample args verified in event assertions; actualentry41da51 modes1..6 x259/260/280 marker20 and occupancy cases',cases=len(cases),differences=0,records=[dict(input=c,output=e) for c,e in zip(cases,expected)]),separators=(',',':'))+'\n');print('PASS',len(cases))
