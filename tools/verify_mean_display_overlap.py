#!/usr/bin/env python3
"""Compose actual admission4071e8 scheduling and original pixels across interruptions."""
# Reuse the existing mapped image, DAT, graphics/font/mask adapters, CLI and hashes.
from pathlib import Path
prefix=(Path(__file__).with_name('verify_mean_material5_display.py')).read_text().split('specs=')[0]
exec(compile(prefix,'verify_mean_material5_display.py','exec'))
put(0x43f068,0x43e770);put(0x43e740,0x1006000);put(0x1006004,0x1006100);put(0x1006108,0x1006200);put(0x1006234,0x1004000)
cases=[]
# Admission request parameters proved independently in display-request-args.json.
for first,second,at in [(0x412d24,0x4107c8,12),(0x4107c8,0x412d24,12),(0x411fdc,0x410e4c,12),(0x412d24,0x412c58,12),(0x413a2c,0x4107c8,12),(0x412d24,0x4107c8,149),(0x412d24,0x4107c8,150)]:
 mapping={0x412d24:(8,7),0x412c58:(8,7),0x4107c8:(6,5),0x411fdc:(7,6),0x410e4c:(7,6),0x413a2c:(5,2)}
 def request(cb):return dict(request=[*mapping[cb],cb])
 cases.append([request(first)]+[dict(tick=1) for _ in range(at)]+[request(second)]+[dict(tick=1) for _ in range(200)])
owner_only=os.environ.get('SLAM_REWARD_OWNER_ONLY')
if owner_only:
 cases=[]
 mapping={0x410a34:(8,7),0x410910:(8,7),0x410d34:(8,7),0x410b00:(10,9)}
 for cb in mapping: cases.append([dict(request=[*mapping[cb],cb])]+[dict(tick=1) for _ in range(305)])
 for first,second,at,second_args in [(0x410a34,0x410b00,12,(10,9)),(0x410b00,0x410a34,12,(8,7)),(0x410b00,0x412d24,12,(11,10)),(0x410d34,0x410b00,74,(10,9)),(0x410d34,0x410b00,76,(10,9))]:
  cases.append([dict(request=[*mapping[first],first])]+[dict(tick=1) for _ in range(at)]+[dict(request=[*second_args,second])]+[dict(tick=1) for _ in range(305)])
 put(0x100301c,0);put(0x1006234,0x413b04)
 def owner_hook(uc,address,n,data):
  if address==0x413b6b:uc.reg_write(UC_X86_REG_EIP,0x413bfa)
 u.hook_add(UC_HOOK_CODE,owner_hook)
expected=[]
for ops in cases:
 for ad,value in [(0x43e780,0),(0x43e784,0),(0x43e788,-1),(0x43e78c,0),(0x43e790,0),(0x43e7a0,2),(0x43e7b0,0),(0x43e7b4,0),(0x43e81c,0)]:put(ad,value)
 u.mem_write(0x43f364,struct.pack("<h",-1));u.mem_write(0x43f382,struct.pack("<h",-1));put(0x438afc,0)
 u.mem_write(0x1000000,bytes(i%4 for i in range(1920)));put(0x43efd0,0x1005000)
 packed=bytearray(480)
 for i in range(1920):
  packed[i//8]|=(i%4&1)<<(7-i%8);packed[240+i//8]|=((i%4>>1)&1)<<(7-i%8)
 u.mem_write(0x1005000,bytes(packed));rows=[]
 for op in ops:
  accepted=0
  if 'request' in op:
   eax,edx,callback=op['request']
   for reg,value in [(UC_X86_REG_EAX,eax),(UC_X86_REG_EDX,edx),(UC_X86_REG_ECX,2),(UC_X86_REG_EBX,0)]:u.reg_write(reg,value)
   for i,v in enumerate([-1,-1,callback]):put(0x10ff004+i*4,v)
   call(0x405f98);accepted= -1 if u.reg_read(UC_X86_REG_EAX)==0xffffffff else 0
  else:call(0x4071e8)
  state=[get(ad) for ad in [0x43e780,0x43e784,0x43e788,0x43e78c,0x43e790]];state[2]=state[2]-0x100000000 if state[2]&0x80000000 else state[2]
  rows.append(dict(accepted=accepted,state=state,fnv=fnv(bytes(u.mem_read(0x1000000,1920)))))
  if owner_only:rows[-1]["gates"]=[struct.unpack("<h",u.mem_read(ad,2))[0] for ad in [0x43f364,0x43f382]]+[get(0x438afc)]
 expected.append(rows)
actual=json.loads(subprocess.run([a.native,str(directory/'MEAN.DAT'),str(directory/'MAIN.DAT')]+(['--gates'] if owner_only else []),input=json.dumps(cases),capture_output=True,text=True,check=True).stdout)
assert len(actual)==len(expected)
for series,(x,y) in enumerate(zip(expected,actual)):
 assert len(x)==len(y)
 for frame,(original,native) in enumerate(zip(x,y)):assert original==native,(series,frame,original,native)
(root/('analysis/traces/mean-reward-owner-original.json' if owner_only else 'analysis/traces/mean-display-overlap-original.json')).write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),mean_dat_sha256=hashlib.sha256(mean).hexdigest(),scope='Actual405f98/4071e8 and actual pixel callbacks; idle graphics adapted; reward idle gate executed with service1c==0; lamps/audio adapted; synthetic11/10 interruption included, saved page configured; no whole-table live cadence or bonus/minigame proof',cases=cases,expected=expected),separators=(',',':'))+'\n')
print(f'{sum(map(len,cases))} original/native overlapping request/pixel/state steps exact')
