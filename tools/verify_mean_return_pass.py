#!/usr/bin/env python3
"""Actual41be5d..41bf03 +419da4 and419944..4199a6; display/hold adapters."""
import hashlib,json,random,struct,subprocess,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP,UC_X86_REG_EIP
root=Path(__file__).resolve().parents[1]
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000),(0x2100000,0x2000)]:u.mem_map(a,n)
image=(root/'build/mean-prepared/pe-data.bin').read_bytes();u.mem_write(0x400000,image)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
put(0x43f068,0x1003000);put(0x43f0d0,0x1002000)
put(0x1002058,0x2101000);put(0x1002034,0x2101100)
events={}
def hook(uc,a,n,c):
 if a not in (0x2101000,0x2101100,0x40f754):return
 if a==0x2101000:events['score']=uc.reg_read(UC_X86_REG_EAX)
 if a==0x2101100:events['announcement']=True;uc.reg_write(UC_X86_REG_EAX,1)
 sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if a==0x2101100 else 8 if a==0x40f754 else 0))
u.hook_add(UC_HOOK_CODE,hook)
rng=random.Random(374);cases=[];expected=[]
def w(raw,o,v):struct.pack_into('<H',raw,o,v&65535)
for op in ('hit','tick'):
 for i in range(768):
  raw=bytearray(rng.randbytes(0x3c0));mode=rng.choice([-1,1,2,4,5,6]);w(raw,0x374,rng.choice([-32768,-1,0,1,149,150,32767]));w(raw,0x37a,rng.randrange(65536));w(raw,0x37c,rng.choice([0,1,2,32766,32767,32768,65535]));w(raw,0x384,rng.choice([0,0,1,65535]));w(raw,0x3a6,rng.choice([0,1,2]));w(raw,0x1e6,rng.randrange(5))
  for j in range(5):raw[0x1e0+j]=rng.randrange(2)
  cases.append(dict(op=op,mode=mode,fields=list(raw)));u.mem_write(0x43f000,bytes(raw));put(0x43f068,0x1003000);put(0x43f0d0,0x1002000);put(0x1003030,mode);put(0x200f000,0x2100000);u.reg_write(UC_X86_REG_ESP,0x200f000)
  events.clear();events.update(score=0,announcement=False)
  u.emu_start(0x41be5d if op=='hit' else 0x419944,0x41bf03 if op=='hit' else 0x4199a6,count=1000)
  result=bytearray(u.mem_read(0x43f000,0x3c0))
  # Service34's opaque returned handle038 is presentation-owned, outside helper.
  for off in (0x038,0x068,0x0d0):result[off:off+4]=raw[off:off+4]
  expected.append(dict(fields=list(result),**events))
probe=sys.argv[1] if len(sys.argv)>1 else str(root/'build/native/mean_return_pass_probe')
actual=json.loads(subprocess.check_output([probe],input=json.dumps(cases),text=True))
for i,(a,e) in enumerate(zip(actual,expected)):
 if a!=e:
  diff=[hex(j) for j,(x,y) in enumerate(zip(a['fields'],e['fields'])) if x!=y];raise AssertionError((i,cases[i]['op'],diff,a['score'],e['score']))
assert len(actual)==len(expected)
(root/'analysis/traces/mean-return-pass-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope=__doc__,cases=cases,expected=expected),separators=(',',':'))+'\n')
print(len(cases),'original/native return-pass hit/expiry states exact')
