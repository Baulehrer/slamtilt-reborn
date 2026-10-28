#!/usr/bin/env python3
"""Replay only real keyboard pairs against the cached original minigame island."""
import json,hashlib,struct,subprocess,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
R=Path(__file__).resolve().parents[1];fixture=json.loads((R/'analysis/traces/mean-minigame1-winning-input.json').read_text())
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000),(0x1100000,0x200000)]:u.mem_map(a,n)
image=(R/'build/mean-minigame-prepared/image.bin').read_bytes();runtime=(R/'build/mean-minigame-prepared/runtime.bin').read_bytes();dat=next((R/'build/corpus/win95/demo-1997').rglob('MEAN.DAT')).read_bytes()
assert hashlib.sha256(image).hexdigest()==fixture['image_sha256']
u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime);u.mem_write(0x1100000,dat)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
services={0x405f98,0x406574,0x406680,0x406280,0x40617c,0x4060f8,0x4060a4,0x405c60,0x40560c,0x4058c8,0x4058a0,0x40587c,0x405814,0x40f91c,0x419f6c,0x416fe0}
points=[0];requested=[0]
def adapter(uc,a,n,c):
 if a==0x40560c:points[0]=(points[0]+uc.reg_read(UC_X86_REG_EAX))&0xffffffff
 if a==0x405814:put(0x43942c+uc.reg_read(UC_X86_REG_EAX)*0xac,uc.reg_read(UC_X86_REG_EDX))
 sp=uc.reg_read(UC_X86_REG_ESP);ret=get(sp)
 if a==0x405f98:requested[0]=get(sp+12);uc.reg_write(UC_X86_REG_EAX,1)
 uc.reg_write(UC_X86_REG_EIP,ret);uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if a==0x405f98 else 4 if a==0x406280 else 8 if a==0x40617c else 0))
for a in services:u.hook_add(UC_HOOK_CODE,adapter,begin=a,end=a)
rows=[]
for tick,(key,expected) in enumerate(zip(fixture['keys'],fixture['states'])):
 put(0x1001054,-1 if key==1 else 0);put(0x1001058,-1 if key==2 else 0)
 put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.emu_start(0x4180d0,0x200fff0,count=100000)
 actual=[tick,key]+[get(a) for a in [0x43efdc,0x43efe0,0x43efe4,0x43effc,0x43f00c,0x43f010]]
 h=14695981039346656037
 for b in u.mem_read(0x43ec3c,480):h=((h^b)*1099511628211)&0xffffffffffffffff
 rows.append(dict(fields=list(struct.unpack('<24I',u.mem_read(0x43efd8,96))),active=get(0x1001044),mode=get(0x1001030),field_1fa=struct.unpack('<H',u.mem_read(0x43f1fa,2))[0],points=points[0],callback=requested[0],packed_frame_fnv=str(h)))
 assert actual==expected,(tick,actual,expected)
 assert bool(get(0x1001044))==(tick+1<len(fixture['keys']))
assert points[0]==120000000 and requested[0]==0x40fb78 and get(0x43efdc)==7
native=json.loads(subprocess.check_output([sys.argv[1] if len(sys.argv)>1 else str(R/'build/native/mean_minigame1_winning_lift'),str(R/'build/mean-minigame-prepared/image.bin'),str(R/'build/mean-minigame-prepared/runtime.bin'),str(next((R/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))),str(R/'analysis/traces/mean-minigame1-winning-input.json')]))
assert len(native)==len(rows)
for tick,(a,b) in enumerate(zip(native,rows)):assert a==b,(tick,a,b)
(R/'analysis/traces/mean-minigame1-winning-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),runtime_sha256=hashlib.sha256(runtime).hexdigest(),dat_sha256=hashlib.sha256(dat).hexdigest(),native_state_sha256=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest(),fields_range='0x43efd8..0x43f034',input_sha256=hashlib.sha256(bytes(fixture['keys'])).hexdigest(),ticks=len(fixture['keys']),points=points[0],callback=requested[0],raw_43efdc=get(0x43efdc),scope='Actual4180d0 original math/control/collision/progress from cached selected3 capture initialization; only shared presentation/audio/score-admission/lamp side effects adapt. Real keyboard inputs only;24DWORD rawstatefields,field1fa,active/mode/points/callback and480bytepacked-frame hash match native lift everytick.'),indent=2)+'\n')
print(len(fixture['keys']),'original gameplay ticks match winning input:120M,6completed laps,40fb78')
