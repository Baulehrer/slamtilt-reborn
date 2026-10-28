#!/usr/bin/env python3
import json,struct,subprocess,random
from pathlib import Path
exec((Path(__file__).parent/'trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
rng=random.Random(4);cases=[];expected=[]
for stage in [0,1,2,4]:
 for i in range(32):
  b=bytearray(rng.randrange(256) for _ in range(100));struct.pack_into('<HH',b,0x58,3,1)
  cases.append(dict(stage=stage,ball=list(b)))
  u.mem_write(0x1000000,bytes(b));put(0x1001030,5)
  for a,v in [(0x43f1e6,4),(0x43f37e,stage),(0x43f36a,-2),(0x43f3ae,123)]:u.mem_write(a,struct.pack('<H',v&65535))
  u.mem_write(0x43f260,bytes([9,8,7,6]));put(0x438b60,0);put(0x438b64,0)
  put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x415330,0x200fff0,count=10000)
  expected.append(dict(ball=list(u.mem_read(0x1000000,100)),stage=word(0x43f37e),field3ae=word(0x43f3ae),data=list(u.mem_read(0x43f260,4)),slot=[get(0x438b50+i*4) for i in range(3)],delay=get(0x438b90)))
subprocess.run(['c++','-std=c++17','-Isrc','-Ibuild/native/_deps/json-src/include','tests/mean_mode4_transfer_probe.cpp','src/physics/mean_mode5_left.cpp','src/physics/mean_mode_reset.cpp','src/physics/mean_upper_release.cpp','src/physics/mean_step.cpp','src/physics/mean_material_bundle.cpp','-o','build/oracle/mean_mode4_transfer_probe'],check=True)
actual=json.loads(subprocess.check_output(['build/oracle/mean_mode4_transfer_probe'],input=json.dumps(cases),text=True))
assert actual==expected,[(i,{k:(a[k],b[k]) for k in b if a[k]!=b[k]}) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b][:1]
(ROOT/'analysis/traces/mean-mode4-transfer-fixture.json').write_text(json.dumps(dict(cases=cases,expected=expected,scope='Actual415330 selected4 ready upper slot and416b28 transfer; stage1->2 andall100ballbytes; multiball spawn excluded'),separators=(',',':'))+'\n')
print(json.dumps(dict(cases=len(cases),differences=0)))
