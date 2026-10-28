#!/usr/bin/env python3
"""Original mini-game execution from a naturally reached native entry context."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
R=Path(__file__).resolve().parents[1];prepared=R/'build/mean-natural-mini-oracle';dat=next((R/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
native=json.loads(subprocess.check_output([sys.argv[1],str(dat),str(R/'build/mean-prepared'),str(R/'analysis/traces/mean-flight-100.json'),str(prepared)],text=True))
image=(prepared/'image.bin').read_bytes();runtime=(prepared/'runtime.bin').read_bytes();reference=(R/'build/mean-prepared/pe-data.bin').read_bytes()
for lo,hi in [(0x180d0,0x194e4),(0x17374,0x176cc),(0x16fe0,0x1701a),(0x17b5b,0x17baf)]:assert image[lo:hi]==reference[lo:hi], 'Original code changed'
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000),(0x1100000,0x200000)]:u.mem_map(a,n)
u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime);u.mem_write(0x1100000,dat.read_bytes())
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
points=[0];requested=[0];reset_calls=[];audio=[];all_audio=[]
def adapter(uc,a,n,c):
 sp=uc.reg_read(UC_X86_REG_ESP)
 if a==0x405c60:audio.append({'service':0x5c,'descriptor':uc.reg_read(UC_X86_REG_EAX),'edx':uc.reg_read(UC_X86_REG_EDX),'ebx':uc.reg_read(UC_X86_REG_EBX)})
 if a in [0x40587c,0x4058a0,0x4058c8]:audio.append({'service':{0x40587c:0x88,0x4058a0:0x84,0x4058c8:0x80}[a],'descriptor':0,'edx':uc.reg_read(UC_X86_REG_EDX) if a!=0x4058c8 else 0,'ebx':uc.reg_read(UC_X86_REG_EAX) if a!=0x4058c8 else 0})
 if a==0x40560c:points[0]+=uc.reg_read(UC_X86_REG_EAX)
 if a==0x405814:put(0x43942c+uc.reg_read(UC_X86_REG_EAX)*0xac,uc.reg_read(UC_X86_REG_EDX))
 if a==0x405f98:
  requested[0]=get(sp+12);uc.reg_write(UC_X86_REG_EAX,1)
  # This accepted-admission adapter must include the actual405f98 voice write.
  # Its full admission/directfield behavior is independently checked960cases.
  if get(sp+4)<0x80000000:
   audio.append({'service':0x88,'descriptor':0,'edx':get(sp+8),'ebx':get(sp+4)})
 uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if a==0x405f98 else 4 if a==0x406280 else 8 if a==0x40617c else 0))
services={0x405f98,0x406574,0x406680,0x406280,0x40617c,0x4060f8,0x4060a4,0x405c60,0x40560c,0x4058c8,0x4058a0,0x40587c,0x405814,0x40f91c,0x419f6c}
for a in services:u.hook_add(UC_HOOK_CODE,adapter,begin=a,end=a)
def observe(uc,a,n,c):reset_calls.append({'mode':get(get(0x43f068)+0x30),'field_3a2':struct.unpack('<H',uc.mem_read(0x43f3a2,2))[0]})
u.hook_add(UC_HOOK_CODE,observe,begin=0x416fe0,end=0x416fe0)
def call(a):
 put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.emu_start(a,0x200fff0,count=100000)
 assert u.reg_read(UC_X86_REG_EIP)==0x200fff0,hex(a)
ticks=0
for step,row in enumerate(native['rows']):
 audio.clear()
 for side,edge in enumerate(row['edges']):
  if edge:u.reg_write(UC_X86_REG_EAX,1);call(0x41766c if side else 0x417374)
 if row['tick']:call(0x4180d0);ticks+=1
 assert audio==row['audio'],(step,'audio',audio,row['audio'])
 all_audio.extend(dict(step=step,**a) for a in audio)
 if not row['tick']:continue
 h=14695981039346656037
 for b in u.mem_read(0x43ec3c,480):h=((h^b)*1099511628211)&0xffffffffffffffff
 actual={'fields':list(struct.unpack('<24I',u.mem_read(0x43efd8,96))),'raw':list(u.mem_read(0x43f000,0x3c0)),'active':get(0x1001044),'mode':get(0x1001030),'points':points[0],'callback':requested[0],'packed_fnv':str(h)}
 assert actual==row['state'],(step,ticks,{k:(actual[k],row['state'][k]) for k in actual if actual[k]!=row['state'][k]})
assert points[0]==30000000 and requested[0]==0x4122cc and not get(0x1001044)
report={'scope':'Original4180d0 and registered417374/41766c inputs plus actual416fe0; initial context exported from unforced native finite entry, not original full-table startup/trajectory. Presentation/audio/score/lamp services bounded. Every mini tick compares24DWORD,960rawbytes,flags/points/callback/packed480bytehash. Existing production fixture independently proves result/release/finiteGameOver.','entry_step':native['entry_step'],'entry_ball':native['entry_ball'],'ticks':ticks,'input_steps':len(native['rows']),'points':points[0],'callback':hex(requested[0]),'reset_calls':reset_calls,'audio_requests':all_audio,'display_audio_adapter':'Accepted405f98 stack0/order,stack1/bank voice side effect included; actual405f98 admission/directwrites independently verified960cases','image_sha256':hashlib.sha256(image).hexdigest(),'runtime_sha256':hashlib.sha256(runtime).hexdigest(),'dat_sha256':hashlib.sha256(dat.read_bytes()).hexdigest()}
(R/'analysis/traces/mean-natural-minigame-original.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS natural entry context:',ticks,'original ticks;actual416fe0;30M/4122cc')
