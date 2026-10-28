#!/usr/bin/env python3
"""Compose actual return rule, admission, five hold timers, expiry and DMD pixels."""
from pathlib import Path
prefix=Path(__file__).with_name('verify_mean_material5_display.py').read_text().split('specs=')[0]
exec(compile(prefix,'verify_mean_material5_display.py','exec'))
put(0x43f068,0x43e770);put(0x1003034,0x405f98);put(0x1003058,0x1004030)
put(0x43e740,0x1006000);put(0x1006004,0x1006100);put(0x1006108,0x1006200);put(0x1006234,0x1004000)
score=0
def score_hook(uc,address,n,data):
 global score
 if address!=0x1004030:return
 score+=uc.reg_read(UC_X86_REG_EAX)
 sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,score_hook)
def ticks(n):return [dict(tick=1) for _ in range(n)]
hit=dict(hit=1)
cases=[
 [hit]+ticks(20)+[hit]+ticks(120)+[hit]+ticks(151)+[hit]+ticks(20)+[hit]+ticks(151),
 [hit]+ticks(150)+[hit]+ticks(151)+[hit],
 [hit]+ticks(151)+[hit]+ticks(150)+[hit],
 [dict(block=1),hit]+ticks(10)+[hit]+ticks(160)+[hit,hit]+ticks(160),
 [hit,hit,dict(block=1)]+ticks(10)+[hit]+ticks(160)+[hit,hit]+ticks(160),
 [hit,hit,hit]+ticks(151)+[hit,hit]+ticks(151)]
expected=[]
field_ranges=[(i,2 if i==0x1e6 or i>=0x374 else 4) for i in [0x024,0x038,0x050,0x1e6,0x25c,0x2bc,0x2c0,0x2c4,0x2c8,0x2cc,0x374,0x37a,0x37c]]
slot_addresses=[0x438b64,0x438b70,0x438b7c,0x438b88,0x438b94]
for ops in cases:
 score=0;u.mem_write(0x43f000,bytes(0x3c0));put(0x43f068,0x43e770);put(0x43f0d0,0x1003000);put(0x43f024,77);u.mem_write(0x43f374,b'\xff\xff')
 for ad,v in [(0x43e780,0),(0x43e784,0),(0x43e788,-1),(0x43e78c,0),(0x43e790,0),(0x43e7a0,2),(0x43e7b0,0),(0x43e7b4,0),(0x43e81c,0)]:put(ad,v)
 for ad,v in zip(slot_addresses,[11,22,33,44,55]):put(ad,v)
 u.mem_write(0x1000000,bytes(i%4 for i in range(1920)));put(0x43efd0,0x1005000)
 packed=bytearray(480)
 for i in range(1920):
  packed[i//8]|=(i%4&1)<<(7-i%8);packed[240+i//8]|=((i%4>>1)&1)<<(7-i%8)
 u.mem_write(0x1005000,bytes(packed));rows=[]
 for op in ops:
  if 'block' in op:
   for reg,v in [(UC_X86_REG_EAX,8),(UC_X86_REG_EDX,7),(UC_X86_REG_ECX,2),(UC_X86_REG_EBX,0)]:u.reg_write(reg,v)
   for i,v in enumerate([-1,-1,0x412d24]):put(0x10ff004+i*4,v)
   call(0x405f98)
  else:
   u.reg_write(UC_X86_REG_ESP,0x10ff000)
   u.emu_start(0x41be5d if 'hit' in op else 0x419944,0x41bf03 if 'hit' in op else 0x4199a6,count=10000)
   if 'hit' not in op:call(0x4071e8)
  fields=[]
  for offset,n in field_ranges:fields+=list(u.mem_read(0x43f000+offset,n))
  state=[get(ad) for ad in [0x43e780,0x43e784,0x43e788,0x43e78c,0x43e790]];state[2]=state[2]-0x100000000 if state[2]&0x80000000 else state[2]
  rows.append(dict(fields=fields,timers=[get(ad) for ad in slot_addresses],score=score,display=state,fnv=fnv(bytes(u.mem_read(0x1000000,1920)))))
 expected.append(rows)
actual=json.loads(subprocess.run([a.native,str(directory/'MEAN.DAT'),str(directory/'MAIN.DAT')],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout)
assert len(actual)==len(expected)
for i,(x,y) in enumerate(zip(expected,actual)):
 assert len(x)==len(y)
 for j,(original,native) in enumerate(zip(x,y)):assert original==native,(i,j,original,native)
(root/'analysis/traces/mean-return-pass-cycle-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),mean_dat_sha256=hashlib.sha256(mean).hexdigest(),scope=__doc__+'; actual419da4/405f98/40f754/4071e8/41163c executed; binary score accumulation and idle rendering adapted; isolated table clock/capture timers, no full ball physics or live frame batching proof',cases=cases,expected=expected),separators=(',',':'))+'\n')
print(sum(map(len,cases)),'original/native complete cycle states/pixels exact')
