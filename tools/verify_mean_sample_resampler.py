#!/usr/bin/env python3
"""Original LUT and bounded420120 mono voice PCM; excludes final stereo mixer."""
import json,struct,hashlib
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import *
root=Path(__file__).resolve().parents[1];image=(root/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x50000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
def run(start,eax=0,ebx=0,esi=0,edi=0):
 put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000)
 for r,v in [(UC_X86_REG_EAX,eax),(UC_X86_REG_EBX,ebx),(UC_X86_REG_ESI,esi),(UC_X86_REG_EDI,edi)]:u.reg_write(r,v)
 u.emu_start(start,0x100fff0,count=2000000)
put(0x43f418,0x1010000);run(0x41eb60,0x20000//6)
u.mem_write(0x1020000,bytes(range(256))*32)
put(0x1002000,0x1020000);put(0x1002004,8192)
put(0x1003000,0x1010000);put(0x1003004,44100);put(0x1003008,65536)
def fnv(data):
 h=14695981039346656037
 for v in data:h=((h^v)*1099511628211)&0xffffffffffffffff
 return str(h)
cases=[]
for descriptor,period,length in [(0x437cf0,160,6465),(0x437d14,226,4078),(0x437da4,226,3026),(0x437d38,226,4490),(0x437d5c,226,4012),(0x437dec,226,5808),(0x437dc8,226,7576),(0x437fe4,428,2747),(0x438008,428,2882),(0x43802c,428,3395),(0x438050,428,4536)]:
 for frames in [1,100,1000,2048,30000]:
  put(0x1002004,length)
  frequency=0x361f0f//period;put(0x1001000,0x1002000);put(0x1001004,0);put(0x1001008,0);put(0x100100c,65536);put(0x1001010,frequency);put(0x1001014,0)
  u.mem_write(0x1030000,bytes(frames*2));run(0x420120,frames,0x1030000,0x1001000,0x1003000)
  actual=bytes(u.mem_read(0x1030000,frames*2));step=((frequency<<32)//44100)&~15
  expected=bytearray()
  for f in range(frames):
   index=(f*step)>>32
   byte=index%256;signed=(byte if byte<128 else byte-256) if index<length else 0
   expected.extend(struct.pack('<h',(signed*(0x20000//6)*127)>>16))
  assert actual==expected,(period,frames,actual[:16],expected[:16])
  assert (get(0x1001004)<<32| get(0x1001008))==min(frames,((length<<32)+step-1)//step)*step
  if frames==30000:assert get(0x1001010)==0
  cases.append(dict(descriptor=descriptor,period=period,frames=frames,pcm_fnv64=fnv(actual),final_phase=str(min(frames,((length<<32)+step-1)//step)*step),first_samples=list(struct.unpack('<'+str(min(frames,8))+'h',actual[:min(frames,8)*2]))))
(root/'analysis/traces/mean-sample-resampler-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Original LUT41eb60 andmono420120; factory6voices/master65536; excludes final stereo mix',cases=cases),indent=2)+'\n')
print(f'{len(cases)} original mono resampler/LUT PCM cases exact')
