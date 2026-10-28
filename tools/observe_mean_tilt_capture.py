#!/usr/bin/env python3
"""Bounded actual capture/Tilt branch observation, explicit seeded services."""
from pathlib import Path
import json,struct
ROOT=Path(__file__).resolve().parents[1]
exec((ROOT/'tools/verify_mean_capture_tick.py').read_text().split('b=bytearray(100)')[0])
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.x86_const import UC_X86_REG_EDX
base=bytes(u.mem_read(0x400000,0x100000));rows=[];writes=[];calls=[]
def watch(uc,access,a,n,v,c):
 if 0x1000000<=a<0x1000064 or 0x43f000<=a<0x43f3c0 or 0x438b2c<=a<0x438b90:writes.append([hex(uc.reg_read(UC_X86_REG_EIP)),hex(a),n,hex(v&((1<<(n*8))-1))])
def observe(uc,a,n,c):
 if a in [0x416be4,0x417068,0x416fe0]:calls.append(hex(a))
 if a==0x100fff0: calls.append('unknown_service');uc.emu_stop()
u.hook_add(UC_HOOK_MEM_WRITE,watch);u.hook_add(UC_HOOK_CODE,observe)
for cb in range(1,6):
 for state in [3,6]:
  for tilt in [0,1]:
   u.mem_write(0x400000,base);put(0x100201c,tilt)
   for slot in [0x34,0x84,0x88,0x8c]:put(0x1002000+slot,0x100fff0)
   put(0x43f368,0xfffe0000);put(0x438b5c,-1);put(0x438b68,-1);put(0x438b74,-1);put(0x438b80,-1)
   b=bytearray(100);struct.pack_into('<ii',b,0,280<<16,285<<16);struct.pack_into('<HH',b,0x58,state,cb);u.mem_write(0x1000000,bytes(b))
   writes=[];calls=[];scores=[];put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000)
   try:u.emu_start(0x415330,0x200fff0,count=6000);error=None
   except Exception as e:error=str(e)
   final=bytes(u.mem_read(0x1000000,100));rows.append(dict(callback=cb,state=state,tilt=tilt,calls=calls,writes=writes,final_state=struct.unpack_from('<HH',final,0x58),final_xy=struct.unpack_from('<ii',final),error=error))
report={'scope':'Actual415330 bounded seeded capture contexts; no original whole-table startup claim', 'seed':{'ball_xy':[280*65536,285*65536],'state58':[3,6],'callback5a':[1,2,3,4,5],'table_mode':2,'raw43f368':'0xfffe0000','slots438b5c_68_74_80':-1,'timer43f380':50},'boundaries':{'prefix':'verify_mean_capture_tick.py before b=bytearray(100)','4161bb':'skip to4169db after local writes','41b8d0':'stub returns, captures score500000 only','service58_5c':'stub returns; captures score500000 only','service34_84_88_8c':'stop if reached (none reached)'},'records':rows}
(ROOT/'analysis/traces/mean-tilt-capture-observation.json').write_text(json.dumps(report,indent=2)+'\n')
for c in rows:print(c['callback'],c['state'],c['tilt'],c['calls'],c['final_state'],len(c['writes']),c['error'])
