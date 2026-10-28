#!/usr/bin/env python3
"""Bounded original ordinary lap request and capture timing oracle (12 contexts)."""
import json, struct, hashlib
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ESP, UC_X86_REG_EIP
ROOT=Path(__file__).resolve().parents[1]
results=[]
for request in [False,True]:
 for accepted in [False,True]:
  for delay in [0,20,200]:
   u=Uc(UC_ARCH_X86,UC_MODE_32)
   for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000)]:u.mem_map(a,n)
   u.mem_write(0x400000,(ROOT/'build/mean-prepared/pe-data.bin').read_bytes())
   def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
   def get(a):return struct.unpack('<i',u.mem_read(a,4))[0]
   def word(a):return struct.unpack('<h',u.mem_read(a,2))[0]
   for layer,values in enumerate([(3,0x6040,0x959f6,0x9ba36,0xb3b36),(1,0x60e0,0xb98f6,0xbf9d6,0xcbb96)]):
    for i,v in enumerate(values):put(0x43f06c+layer*20+i*4,v+(0x1100000 if i>=2 else 0))
   put(0x43f068,0x1001000);put(0x1001000,1);put(0x1001030,2)
   put(0x43f0d0,0x1002000);put(0x1002010,0x1003000);put(0x1002014,0x1004000);put(0x1004000,0x1000000)
   put(0x1002058,0x200ff00);put(0x100205c,0x200ff00)
   put(0x438b68,-1);put(0x438b6c,100);put(0x438b70,0)
   put(0x438b74,-1);put(0x438b78,0);put(0x438b7c,0)
   u.mem_write(0x43f380,struct.pack('<h',50))
   scores=[]
   def stub(uc,a,n,ctx):
    if uc.reg_read(UC_X86_REG_EAX)==500000:scores.append(500000)
    sp=uc.reg_read(UC_X86_REG_ESP);target=struct.unpack('<I',uc.mem_read(sp,4))[0]
    uc.reg_write(UC_X86_REG_ESP,sp+4);uc.reg_write(UC_X86_REG_EIP,target)
   u.hook_add(UC_HOOK_CODE,stub,begin=0x200ff00,end=0x200ff00)
   def skip_rules(uc,a,n,ctx):uc.reg_write(UC_X86_REG_EIP,0x4169db)

   u.hook_add(UC_HOOK_CODE,stub,begin=0x41b8d0,end=0x41b8d0)
   put(0x1002034,0x405f98);put(0x43e7a0,2 if accepted else 0);put(0x43e780,4);put(0x43e788,0);put(0x438b70,delay)
   # Request-free control preserves the existing native rule boundary.
   if not request:u.hook_add(UC_HOOK_CODE,skip_rules,begin=0x4161bb,end=0x4161bb)
   b=bytearray(100);struct.pack_into('<ii',b,0,26*65536,279*65536);struct.pack_into('<HH',b,0x58,3,2);u.mem_write(0x1000000,bytes(b));u.mem_write(0x43f380,struct.pack('<h',0))
   rows=[]
   for tick in range(400):
    put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x415330,0x200fff0,count=5000)
    assert u.reg_read(UC_X86_REG_EIP)==0x200fff0
    if tick%4==3:
     for ad in [0x438b68,0x438b74]:
      if get(ad)>=0:put(ad,get(ad)-1)
    state=dict(tick=tick+1,timer=word(0x43f380),gate=word(0x43f364),callback=word(0x100005a),state=word(0x1000058),slot2=[get(0x438b68+i*4) for i in range(3)],slot3=[get(0x438b74+i*4) for i in range(3)],handle=get(0x43f038),display_callback=hex(get(0x43e790)&0xffffffff))
    if tick<3 or not rows or any(state[k]!=rows[-1][k] for k in ['callback','state']):rows.append(state)
    if state['state']==2:break
   admitted=request and accepted
   assert rows[0]['handle']==(-1 if admitted else 0)
   assert rows[0]['display_callback']==('0x4119e0' if admitted else '0x0')
   assert rows[0]['slot2']==[-1,100,0 if admitted else delay]
   assert [(s['timer'],s['gate']) for s in rows[:3]]==[(-1,-1),(-2,0),(-3,0)]
   assert scores==[500000]
   assert rows[-2]['callback']==3 and rows[-1]['state']==2
   assert rows[-2]['tick']==(103 if delay<=20 or admitted else 203)
   results.append(dict(actual_request=request,admission_enabled=accepted,initial_slot2_delay=delay,release_tick=tick+1,states=rows))
report=dict(image_sha256=hashlib.sha256((ROOT/'build/mean-prepared/pe-data.bin').read_bytes()).hexdigest(),scope='Actual415330 callback2 normalmode timer0 through callback3 release; actual405f98 and40f754;41b8d0 and score adapters; display-slot0 decrement each4 ball ticks; scheduler/callback pixels excluded; request-free control skips4161bb..416224 only',cases=results,conclusion='Accepted ordinary lap request clears delay438b70 via40f754; rejected request leaves it. Both keep timer-1/gate-1 then timer-2/gate0 and release timing identical when delay initially0. Nonzero delay changes release timing.')
assert all(c['states'][0]['timer']==-1 and c['states'][0]['gate']==-1 and c['states'][1]['timer']==-2 and c['states'][1]['gate']==0 for c in results)
assert all(c['release_tick']==203 for c in results if c['initial_slot2_delay']<=20 or (c['actual_request'] and c['admission_enabled']))
assert all(c['release_tick']==303 for c in results if c['initial_slot2_delay']==200 and not(c['actual_request'] and c['admission_enabled']))
report['generator']='tools/verify_mean_lap_hold.py'
report['limitations']=['No scheduler4071e8 or4119e0 pixel lifecycle execution; no whole-engine or wall-clock timing claim.', 'Lap-completion goal413608 branch excluded.']
(ROOT/'analysis/traces/mean-lap-hold-original.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS 12 original lap request/capture contexts: admission, slot delay, timer/gate, and release203/303')
