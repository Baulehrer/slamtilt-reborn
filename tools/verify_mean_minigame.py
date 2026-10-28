#!/usr/bin/env python3
"""Originalselected3 bounded static-lift comparisons, reusable userasset caches."""
exec(open('tools/mean_minigame_oracle.py').read())
from unicorn import UC_HOOK_CODE
# Real service identities; observational adapters preserve registers.
services={0x34:0x405f98,0x38:0x406574,0x3c:0x406680,0x40:0x406280,0x5c:0x405c60,0x58:0x40560c,0x80:0x4058c8,0x84:0x4058a0,0x88:0x40587c,0x94:0x405814}
for off,target in services.items():put(0x1002000+off,target)
points=[0]
def adapter(uc,a,n,c):
 if a==0x40560c:points[0]+=uc.reg_read(UC_X86_REG_EAX)
 if a==0x405f98:uc.reg_write(UC_X86_REG_EAX,1)
 sp=uc.reg_read(UC_X86_REG_ESP);ret=get(sp)&0xffffffff
 uc.reg_write(UC_X86_REG_EIP,ret);uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if a==0x405f98 else 4 if a==0x406280 else 0))
for target in services.values():u.hook_add(UC_HOOK_CODE,adapter,begin=target,end=target)
put(0x43efd0,0x1008000)
image=bytes(u.mem_read(0x400000,0x100000));runtime=bytes(u.mem_read(0x1000000,0x10000))
prepared=ROOT/'build/mean-minigame-prepared';prepared.mkdir(exist_ok=True)
(prepared/'image.bin').write_bytes(image);(prepared/'runtime.bin').write_bytes(runtime)
subprocess=__import__('subprocess')
subprocess.run(['c++','-std=c++17','-Isrc','-Ibuild/native/_deps/json-src/include','tests/mean_minigame_probe.cpp','src/physics/mean_minigame_lift.cpp','build/generated/mean_minigame.cpp','-o','build/mean_minigame_probe'],check=True)
fixtures=[]
for seed in range(4):
 u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime);points[0]=0;rows=[]
 for tick in range(2000):
  put(0x1001054,-1 if seed==1 or seed==3 and tick%100<50 else 0);put(0x1001058,-1 if seed==2 or seed==3 and tick%100>=50 else 0)
  run(0x4180d0)
  rows.append(dict(fields=list(struct.unpack('<24I',u.mem_read(0x43efd8,96))),active=get(0x1001044)&0xffffffff,mode=get(0x1001030),selected=e['word'](0x43f1e6),frame=list(u.mem_read(0x43ec3c,480)),points=points[0]))
  if not get(0x1001044):break
 native=json.loads(subprocess.check_output(['build/mean_minigame_probe',str(prepared/'image.bin'),str(prepared/'runtime.bin'),str(next((ROOT/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))),str(seed),'2000']))
 diff=[i for i,(a,b) in enumerate(zip(native,rows)) if a!=b]
 if diff:
  i=diff[0];print('DIFF',seed,i,{k:(native[i][k],rows[i][k]) for k in rows[i] if native[i][k]!=rows[i][k] and k!='frame'});print('frame differences',sum(a!=b for a,b in zip(native[i]['frame'],rows[i]['frame'])))
 assert not diff and len(native)==len(rows),(seed,len(native),len(rows))
 fixtures.append(dict(seed=seed,states=rows))
print(json.dumps({'cycles':len(fixtures),'states':sum(len(c['states']) for c in fixtures),'lengths':[len(c['states']) for c in fixtures],'differences':0}))
(ROOT/'analysis/traces/mean-minigame-fixture.json').write_text(json.dumps(dict(scope='Original4180d0 selected3 noinput/left/right/alternating, runtime math/control/framebuffer exact; display/audio adapters;416fe0/lamps bounded; startup-derived context cached locally',cases=fixtures),separators=(',',':'))+'\n')
