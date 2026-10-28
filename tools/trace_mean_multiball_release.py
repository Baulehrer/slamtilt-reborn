#!/usr/bin/env python3
"""Bounded original callback5 release; no invented free-physics trace."""
import json, struct, hashlib
from pathlib import Path
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP
ROOT=Path(__file__).resolve().parents[1]
exec((ROOT/'tools/trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
image=bytes(u.mem_read(0x400000,0x100000));runtime=bytes(u.mem_read(0x1000000,0x10000))
cases=[]
for mode,selected,bits,flag in [(5,4,0,0),(5,0,0,0),(4,4,6,0),(4,4,2,0),(4,4,6,1),(6,4,0,0),(6,4,0,1)]:
 for secondary,tertiary in [(3,0),(2,0),(1,0),(0,2),(0,1),(0,0),(-1,0)]:
  u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime)
  b=bytearray((i*11+7)%256 for i in range(100));struct.pack_into('<HH',b,0x58,3,5);u.mem_write(0x1000000,bytes(b))
  put(0x1001030,mode);u.mem_write(0x43f1e6,struct.pack('<h',selected));u.mem_write(0x43f39e,struct.pack('<h',bits));u.mem_write(0x43f3a6,struct.pack('<h',flag));u.mem_write(0x43f382,struct.pack('<h',flag));put(0x43f064,0x12345)
  for i,v in enumerate([19,secondary,tertiary]):put(0x438b8c+i*4,v)
  steps=[]
  for tick in range(8):
   put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x415330,0x200fff0,count=10000)
   steps.append(dict(tick=tick+1,ball=list(u.mem_read(0x1000000,100)),slot=[get(0x438b8c+i*4) for i in range(3)],bits=word(0x43f39e),slot50=[get(0x438b50+i*4) for i in range(3)]))
   if word(0x1000058)==2:break
  cases.append(dict(initial=dict(mode=mode,selected=selected,bits=bits,flag=flag,secondary=secondary,tertiary=tertiary,ball=list(b)),steps=steps))
report=dict(scope='Original415330 callback5 +416ad8 +416e78/416f24 release; presentation service58 bounded; no engine physics or display-slot decrement',image_sha256=hashlib.sha256((ROOT/'build/mean-prepared/pe-data.bin').read_bytes()).hexdigest(),cases=cases)
(ROOT/'analysis/traces/mean-multiball-release-original.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
print(json.dumps(dict(cases=len(cases),states=sum(len(c['steps']) for c in cases),released=sum(c['steps'][-1]['ball'][88]==2 for c in cases))))
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EDX,UC_X86_REG_EIP
put(0x43e740,0x1005000);put(0x1005004,0x1005100);put(0x1005108,0x1005200);put(0x1005230,0x200ff00)
events=[]
def observe(uc,a,n,ctx):
 events.append(dict(kind='step' if a==0x4088f0 else 'pair',i=uc.reg_read(UC_X86_REG_EAX),**({} if a==0x4088f0 else dict(j=uc.reg_read(UC_X86_REG_EDX)))))
 sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,struct.unpack('<I',uc.mem_read(sp,4))[0]);uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,observe,begin=0x4088f0,end=0x4088f0);u.hook_add(UC_HOOK_CODE,observe,begin=0x408bfc,end=0x408bfc)
put(0x43e770,3);put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.emu_start(0x408874,0x200fff0,count=10000)
loop=dict(status='VERIFIED bounded original wrapper; callback/physics/pair bodies stubbed',iteration_events=events,addresses={'wrapper':'0x408874','ball_step':'0x4088f0','pair_step':'0x408bfc','active_count':'0x43e770','pointer_array':'0x4298c8','allocator':'0x408050','drain_callback':'0x408084'},order=['table descriptor+30 callback before balls','step index i','pair i,j for j=i+1..count-1','increment i; count read again'],drain={'single':'408084 count<=1 lifecycle, no count removal here','multiple':'408084 count>1 marks ball+58=5; removal not in408874/4088f0; external sweep still needs locating'},held={'callback':'0x4166cb','poll':'0x416ad8','slot':'0x438b8c','mode5_selected4_release':'0x416e78','state':2,'x':13,'y':306,'vx':0,'vy_hex':'0x5a000','layer_word48':1},fixture='analysis/traces/mean-multiball-release-original.json')
(ROOT/'analysis/mean-multiball-loop.json').write_text(json.dumps(loop,indent=2)+'\n')
print(events)
removals=[]
for states in [(2,5,2),(5,2,2),(5,5,2),(5,5,5),(2,2,5),(5,)]:
 for i,s in enumerate(states):
  ptr=0x1006000+i*128;put(0x4298c8+i*4,ptr);b=bytearray([i+1]*100);struct.pack_into('<H',b,0x58,s);u.mem_write(ptr,bytes(b))
 put(0x43e770,len(states));put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000)
 u.emu_start(0x4079dc,0x407a3d,count=1000)
 n=get(0x43e770);removals.append(dict(initial=list(states),final_count=n,objects=[list(u.mem_read(0x1006000+i*128,100)) for i in range(len(states))]))
loop['drain'].update(sweep='0x4079dc..0x407a3d',algorithm='Ascending i; if state5 andcount>1 copy100bytes fromlastobject intoi; decrementcount; markoldlast state5. Incrementi without rechecking swappedobject; consecutive drainedlast may survive to nextsweep.',cases=removals)
(ROOT/'analysis/mean-multiball-loop.json').write_text(json.dumps(loop,indent=2)+'\n')
print('Removal counts:',[r['final_count'] for r in removals])
