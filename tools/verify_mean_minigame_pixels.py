#!/usr/bin/env python3
"""Composed actual minigame rendering, using existing cached math/control harness."""
import sys,json,hashlib,subprocess,struct
from pathlib import Path
# Initialize only; do not run or rewrite existing gameplay fixtures.
prefix=Path(__file__).with_name('verify_mean_minigame2.py').read_text().split('points=[0];visited=set()')[0]
exec(compile(prefix,'verify_mean_minigame2.py','exec'))
main_path=dat.with_name('MAIN.DAT');main=main_path.read_bytes()
u.mem_map(0x1400000,0x10000);u.mem_write(0x1400000,main)
put(0x43e82c,0x1400000);u.mem_map(0x1500000,0x10000);put(0x43e3e8,0x1500000)
put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.emu_start(0x40af14,0x200fff0,count=20000)
# Renderers run original code, including nested calls; only external gameplay side effects adapt.
renderers={0x406574,0x406680,0x406280,0x40617c,0x4060f8,0x4060a4,0x40f91c}
def adapter(uc,a,n,c):
 if a==0x405f98:uc.reg_write(UC_X86_REG_EAX,1)
 if a==0x405814:put(0x43942c+uc.reg_read(UC_X86_REG_EAX)*0xac,uc.reg_read(UC_X86_REG_EDX))
 if a==0x416fe0:
  put(0x438b2c,0);put(0x438b34,-1);u.mem_write(0x43f3b8,b'\0\0')
 sp=uc.reg_read(UC_X86_REG_ESP);ret=get(sp)
 uc.reg_write(UC_X86_REG_EIP,ret);uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if a==0x405f98 else 0))
for target in (set(services.values())|{0x419f6c,0x416fe0})-renderers:u.hook_add(UC_HOOK_CODE,adapter,begin=target,end=target)
for a,v in [(0x1001030,4),(0x1001044,1),(0x1001010,0),(0x1001014,0),(0x1001018,-1),(0x1001020,0),(0x43f034,0),(0x43f01c,0),(0x43f040,0),(0x43efcc,0),(0x43efd4,0),(0x43f03c,0),(0x43f038,0)]:put(a,v)
image=bytes(u.mem_read(0x400000,0x100000));runtime=bytes(u.mem_read(0x1000000,0x10000))
cache=ROOT/'build/mean-minigame-pixels-prepared';cache.mkdir(exist_ok=True)
(cache/'runtime.bin').write_bytes(runtime)
fixtures=[]
for variant,seed in [(1,0),(1,3),(2,0),(2,4)]:
 u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime);u.mem_write(0x1500000,bytes(1920))
 u.mem_write(0x43f3a4,struct.pack('<HH',variant,0 if variant==1 else 2));u.mem_write(0x43f1f6,struct.pack('<H',8000))
 (cache/'image.bin').write_bytes(bytes(u.mem_read(0x400000,0x100000)));rows=[]
 for tick in range(2500):
  if seed==3:put(0x43f034,0x40000 if tick%100<50 else 0)
  if seed==4 and get(0x43f01c)==2:
   put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.emu_start(0x417570,0x200fff0,count=1000)
  put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.emu_start(0x4180d0,0x200fff0,count=100000)
  h=14695981039346656037
  for b in u.mem_read(0x1500000,1920):h=((h^b)*1099511628211)&0xffffffffffffffff
  rows.append(dict(tick=tick,pixels=str(h)))
  if not get(0x1001044):break
 native=json.loads(subprocess.check_output([sys.argv[1],str(cache/'image.bin'),str(cache/'runtime.bin'),str(dat),str(seed),'2500','8000','pixels',str(main_path)]))
 assert len(native)==len(rows),(variant,seed,len(native),len(rows))
 for n,(a,b) in enumerate(zip(native,rows)):assert a==b,(variant,seed,n,a,b)
 fixtures.append(dict(variant=variant,seed=seed,states=rows))
(ROOT/'analysis/traces/mean-minigame-pixels-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),main_sha256=hashlib.sha256(main).hexdigest(),scope='Actual4180d0 with original render/text/mask services; bounded side-effect adapters, seeded variant contexts; full DMD canvas after each tick',cases=fixtures),separators=(',',':'))+'\n')
print(sum(len(x['states']) for x in fixtures),'composed original/native minigame DMD frames exact')
