#!/usr/bin/env python3
"""Actual405f98/4071e8 admission and retirement; callback bodies are explicit adapters."""
import argparse, hashlib, itertools, json, struct, subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,UC_X86_REG_EDX,UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_ESI
p=argparse.ArgumentParser();p.add_argument('--native',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];image=(root/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32)
u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
addresses=[0x43e780,0x43e784,0x43e788,0x43e78c,0x43e790,0x43e7a0,0x43e7b0,0x43e7b4,0x43e81c,0x4297a8,0x4297ac,0x4297b8,0x4297bc,0x4297cc]
def put(ad,v):u.mem_write(ad,struct.pack('<I',v&0xffffffff))
def get(ad):return struct.unpack('<i',u.mem_read(ad,4))[0]
put(0x43e740,0x1001000);put(0x1001004,0x1001100);put(0x1001108,0x1001200)
put(0x1001228,0x1004010);put(0x1001234,0x1004020)
current_action=0
def hook(uc,ad,n,data):
 global current_action
 if ad not in (0x1004000,0x1004010,0x1004020,0x4069a0,0x4072cc):return
 if ad==0x1004000:
  current_action=3;put(0x43e78c,get(0x43e78c)+1)
  if get(0x43e78c)>=3:put(0x43e784,0)
 elif ad==0x1004010:current_action=2
 elif ad==0x1004020:current_action=4
 elif ad==0x4069a0:current_action=1
 else:current_action+=8
 sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp)&0xffffffff);uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,hook)
def call(ad,args=()):
 put(0x100f000,0x100fff0)
 for i,v in enumerate(args):put(0x100f004+i*4,v)
 u.reg_write(UC_X86_REG_ESP,0x100f000);u.emu_start(ad,0x100fff0,count=2000)
 assert u.reg_read(UC_X86_REG_EIP)==0x100fff0
cases=[]
for mode,state,limit,priority,stack0,mask in itertools.product([-1,0,1,2,3,4],[0,3,4],[-1,0,7],[0,7,8,9],[-1,0,5],[0,2]):
 initial=[state,2,7,13,0x1004000,mode,limit,0,0,17,18,19,20,mask]
 cases.append(dict(initial=initial,request=[priority,7,2,0,stack0,1,0x1004000]))
for mode,state,active,callback,engine28,screen in itertools.product([0,2,3],[0,3,4],[0,2],[0,0x1004000],[0,1],[0,1,2]):
 cases.append(dict(initial=[state,active,7,0,callback,mode,0,engine28,screen,17,18,19,20,2],ticks=6))
# Accepted replacement before running ticks; same EAX8/EDX7 request is accepted twice.
for initial_state,limit in itertools.product([0,4],[0,8]):
 cases.append(dict(initial=[initial_state,2,7,2,0x1004000,2,limit,0,0,17,18,19,20,2],request=[8,7,2,0,-1,-1,0x1004000],ticks=7))
owner_only=__import__('os').environ.get('SLAM_DISPLAY_OWNERS_ONLY')
if owner_only:
 cases=[]
 for owner,state,active,priority,counter,flag in itertools.product(['minigame','bonus','return'],[0,4,6],[0,2],[-1,7,9],[0,75,267],[0,3]):
  cases.append(dict(initial=[state,active,priority,counter,0x410b00,2,0,0,0,17,18,19,20,2],owner=owner,flag=flag,ticks=0))
expected=[]
for c in cases:
 for ad,v in zip(addresses,c['initial']):put(ad,v)
 result=0
 if 'owner' in c:
  owner=c['owner']
  if owner=='minigame':
   u.reg_write(UC_X86_REG_EAX,0x43e770);u.reg_write(UC_X86_REG_ECX,0)
   u.emu_start(0x415bf7,0x415c32,count=1000)
  elif owner=='bonus':
   put(0x43e770,1);put(0x43e774,1)
   # Table save adapter preserves registers; use same return stub as alternate.
   put(0x1001218,0x1004010);call(0x408084)
  else:
   put(0x1001308,0);put(0x100130c,c['flag']);u.reg_write(UC_X86_REG_EAX,0x1001300)
   u.reg_write(UC_X86_REG_EBX,3);u.reg_write(UC_X86_REG_ESI,0)
   u.emu_start(0x407870,0x4078a6,count=1000)
 if 'request'  in c:
  r=c['request']
  for reg,v in zip([UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ECX,UC_X86_REG_EBX],r[:4]):u.reg_write(reg,v)
  call(0x405f98,r[4:]);result=u.reg_read(UC_X86_REG_EAX);result=result-0x100000000 if result&0x80000000 else result
 actions=[]
 for tick in range(c.get('ticks',0)):
  current_action=0;call(0x4071e8);actions.append(current_action)
 state=[get(ad) for ad in addresses];state[-1]&=255
 expected.append(dict(result=result,actions=actions,state=state))
actual=json.loads(subprocess.run([a.native],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout)
assert len(actual)==len(expected)
for i,(x,y) in enumerate(zip(expected,actual)):assert x==y,(i,cases[i],x,y)
report=dict(image_sha256=hashlib.sha256(image).hexdigest(),scope=('Actual415bf7..415c32 minigame takeover,408084 bonus entry with table-save adapter and407870..4078a6 return raw writes; counter/priority/callback retention, graphic inputs varied; no full minigame2 entry or table reset/bonus composition equivalence' if owner_only else 'Actual405f98 register/stack admission and4071e8 scheduler fields; callback increment/clear, idle, engine28, alternate4069a0 andrestart4072cc explicitly adapted; no bitmap or live whole-table equivalence'),cases=cases,expected=expected)
(root/('analysis/traces/mean-display-owner-boundaries-original.json' if owner_only else 'analysis/traces/mean-display-scheduler-original.json')).write_text(json.dumps(report,separators=(',',':'))+'\n')
print(f'{len(cases)} original/native request/scheduler contexts exact')
