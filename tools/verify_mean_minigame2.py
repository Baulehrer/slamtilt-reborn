#!/usr/bin/env python3
"""Bounded phase2 original math/control; intro text/numeric presentation excluded."""
import json,struct,subprocess,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
ROOT=Path(__file__).resolve().parents[1];u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000),(0x1100000,0x200000)]:u.mem_map(a,n)
source=ROOT/'build/mean-minigame-prepared';u.mem_write(0x400000,(source/'image.bin').read_bytes());u.mem_write(0x1000000,(source/'runtime.bin').read_bytes());dat=next((ROOT/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'));u.mem_write(0x1100000,dat.read_bytes())
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
services={0x34:0x405f98,0x38:0x406574,0x3c:0x406680,0x40:0x406280,0x44:0x40617c,0x48:0x4060f8,0x4c:0x4060a4,0x5c:0x405c60,0x58:0x40560c,0x80:0x4058c8,0x84:0x4058a0,0x88:0x40587c,0x94:0x405814}
for off,target in services.items():put(0x1002000+off,target)
points=[0];visited=set();sounds=[];sound_only="--sounds" in sys.argv;current_tick=[0]
def adapter(uc,a,n,c):
 if a==0x405c60:sounds.append(dict(tick=current_tick[0],service=0x5c,descriptor=uc.reg_read(UC_X86_REG_EAX),edx=uc.reg_read(UC_X86_REG_EDX),ebx=uc.reg_read(UC_X86_REG_EBX)))
 if a in [0x40587c,0x4058a0,0x4058c8]:
  service={0x40587c:0x88,0x4058a0:0x84,0x4058c8:0x80}[a]
  sounds.append(dict(tick=current_tick[0],service=service,descriptor=0,edx=uc.reg_read(UC_X86_REG_EDX) if service!=0x80 else 0,ebx=uc.reg_read(UC_X86_REG_EAX) if service!=0x80 else 0))
 if a==0x40560c:points[0]=(points[0]+uc.reg_read(UC_X86_REG_EAX))&0xffffffff
 if a==0x405f98:uc.reg_write(UC_X86_REG_EAX,1)
 if a==0x405814:put(0x43942c+uc.reg_read(UC_X86_REG_EAX)*0xac,uc.reg_read(UC_X86_REG_EDX))
 if a==0x416fe0:
  assert get(0x1001030)==2 and (get(0x43f3a2)&65535)==0
  put(0x438b2c,0);put(0x438b34,-1);u.mem_write(0x43f3b8,b'\0\0')
 sp=uc.reg_read(UC_X86_REG_ESP);ret=get(sp)
 uc.reg_write(UC_X86_REG_EIP,ret);uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if a==0x405f98 else 4 if a==0x406280 else 8 if a==0x40617c else 0))
for target in set(services.values())|{0x40f91c,0x419f6c,0x416fe0}:u.hook_add(UC_HOOK_CODE,adapter,begin=target,end=target)
def observe(uc,a,n,c):visited.add(a)
for a in [0x418ca4,0x418d34,0x418e00,0x418fe6,0x4190f8,0x418eed]:u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a)
for a,v in [(0x1001030,4),(0x1001044,1),(0x1001010,0),(0x1001014,0),(0x1001018,-1),(0x1001020,0),(0x43f034,0),(0x43f01c,0),(0x43f040,0),(0x43efcc,0),(0x43efd4,0),(0x43f03c,0),(0x43f038,0)]:put(a,v)
for a,v in [(0x43f3a4,2),(0x43f3a6,2),(0x43f3a2,0),(0x43f3bc,0),(0x43f3b8,0)]:u.mem_write(a,struct.pack('<H',v))
# Source cache has zero1f6; explicit synthetic branch thresholds are seeded below.
image=bytes(u.mem_read(0x400000,0x100000));runtime=bytes(u.mem_read(0x1000000,0x10000));prepared=ROOT/('build/mean-minigame-samples-prepared' if sound_only else 'build/mean-minigame2-prepared');prepared.mkdir(exist_ok=True);(prepared/'image.bin').write_bytes(image);(prepared/'runtime.bin').write_bytes(runtime)
native_exe=sys.argv[1] if len(sys.argv)>1 else str(ROOT/'build/native/mean_minigame2_probe')
if len(sys.argv)==1:subprocess.run(['cmake','--build',str(ROOT/'build/native'),'--target','mean_minigame2_probe','-j4'],check=True)
extra_addresses=[0x43efcc,0x43efd4,0x43f040,0x43f050,0x43f1f6,0x43f3a4,0x43f3a6,0x43f3b8,0x438b2c,0x438b34]
fixtures=[]
for scenario in ([5,6,10,11,15,16,20,21] if sound_only else range(15)):
 seed=scenario%5;threshold=8000 if sound_only else [0,8000,20000][scenario//5]
 u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime);points[0]=0;visited.clear();sounds.clear();rows=[];u.mem_write(0x43f1f6,struct.pack("<H",threshold))
 if sound_only and scenario%10<5:u.mem_write(0x43f3a4,struct.pack("<HH",1,0))
 if sound_only:u.mem_write(0x43f37a,struct.pack("<H",65535 if scenario>=15 else 0))
 if sound_only:(prepared/"image.bin").write_bytes(bytes(u.mem_read(0x400000,0x100000)))
 for tick in range(2500):
  current_tick[0]=tick
  if seed==1:put(0x43f034,0x2800)
  if seed==2:put(0x43f034,0x40000)
  if seed==3:put(0x43f034,0x40000 if tick%100<50 else 0)
  if seed==4 and get(0x43f01c)==2:
   put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.emu_start(0x417570,0x200fff0,count=1000)
  put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.emu_start(0x4180d0,0x200fff0,count=100000)
  h=14695981039346656037
  for v in u.mem_read(0x43ec3c,480):h=((h^v)*1099511628211)&0xffffffffffffffff
  rows.append(dict(fields=list(struct.unpack('<24I',u.mem_read(0x43efd8,96))),extra=[get(a) for a in extra_addresses],active=get(0x1001044),mode=get(0x1001030),frame_hash=h,points=points[0]))
  if not get(0x1001044):break
 native=json.loads(subprocess.check_output([native_exe,str(prepared/'image.bin'),str(prepared/'runtime.bin'),str(dat),str(seed),'2500',str(threshold)]+(["sounds"] if sound_only else [])))
 if sound_only:
  assert native==sounds,(seed,native,sounds)
  assert [q["descriptor"] for q in sounds if q["service"]==0x5c]==[0x437fe4,0x438008,0x43802c,0x438050],sounds
  fixtures.append(dict(variant=1 if scenario%10<5 else 2,field_37a=65535 if scenario>=15 else 0,seed=seed,threshold=threshold,requests=sounds.copy()));continue
 for i,(a,b) in enumerate(zip(native,rows)):
  if a!=b:raise AssertionError((seed,i,{k:(a[k],b[k]) for k in b if a[k]!=b[k]}))
 assert len(native)==len(rows)
 fixtures.append(dict(seed=seed,threshold_1f6=threshold,states=rows,visited=[hex(a) for a in sorted(visited)]))
if sound_only:
 import hashlib
 (ROOT/'analysis/traces/mean-minigame-samples-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Actual4180d0 both minigames natural countdown service5c request sequence matches native lifted island; seeded threshold8000, no early input',cases=fixtures),indent=2)+'\n')
 print('Eight original/native minigame countdown request traces exact');sys.exit(0)
print(json.dumps(dict(cycles=len(fixtures),states=sum(len(c['states']) for c in fixtures),lengths=[len(c['states']) for c in fixtures],visited=[c['visited'] for c in fixtures],differences=0)))
(ROOT/'analysis/traces/mean-minigame2-original.json').write_text(json.dumps(dict(input_writer='0x417570..4175c5',scope='Actual4180d0 phase2math/control/framebuffer bytes exact; originalphase2initializer fields. Introtext/numericoverlay4060f8/40617c anddisplayadapters isolated; userassets cached separately; synthetic034value schedules and exact4175b2 recurrence;1f6=8000originalnewgame from419e68 plus0/20000syntheticboundaries',cases=fixtures),separators=(',',':'))+'\n')
