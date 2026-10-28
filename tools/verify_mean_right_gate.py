#!/usr/bin/env python3
import json,struct,subprocess,sys
from pathlib import Path
exec((Path(__file__).parent/'verify_mean_capture_tick.py').read_text().split('b=bytearray(100)')[0])
from unicorn.x86_const import UC_X86_REG_EBX,UC_X86_REG_ECX
base=bytes(u.mem_read(0x43f000,0x3c0));cases=[];expected=[]
for kind in ['gate','a','b']:
 for mode in [1,2,3,4]:
  for armed in [0,1,-1]:
   for marker in [0,11,20,31]:
    for x in [0,339,340]:
     raw=bytearray(base);struct.pack_into('<h',raw,0x3a2,armed);struct.pack_into('<h',raw,0x3b8,armed)
     struct.pack_into('<I',raw,0x90,0x110be00e)
     b=bytearray(range(100));struct.pack_into('<i',b,0,271<<16);struct.pack_into('<i',b,4,x<<16);struct.pack_into('<H',b,0x5c,marker)
     c=dict(kind=kind,mode=mode,raw=list(raw),ball=list(b));cases.append(c)
     u.mem_write(0x43f000,bytes(raw));u.mem_write(0x1000000,bytes(b));put(0x1001030,mode);put(0x438b2c,17);put(0x438b34,19)
     n=0 if kind=='gate' else 5 if kind=='a' else 2
     for i in range(n):put(0x200f000+i*4,0)
     put(0x200f000+n*4,0x200fff0)
     u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.reg_write(UC_X86_REG_ECX,0x1000000);u.reg_write(UC_X86_REG_EBX,x<<16)
     if kind=='a' and x>=340:continue # Originalalternatebranch outside bounded writer.
     u.emu_start({'gate':0x416fe0,'a':0x41cd50,'b':0x41de71}[kind],0x200fff0,count=1000)
     expected.append(dict(raw=list(u.mem_read(0x43f000,0x3c0)),ball=list(u.mem_read(0x1000000,100)),b2c=get(0x438b2c),b34=get(0x438b34)))
cases=[c for c in cases if not(c['kind']=='a' and struct.unpack_from('<i',bytes(c['ball']),4)[0]>=340<<16)]
probe=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build/native/mean_right_gate_probe'
if not probe.is_file():raise FileNotFoundError('Build native mean_right_gate_probe before running oracle')
actual=json.loads(subprocess.check_output([str(probe)],input=json.dumps(cases).encode()))
assert len(actual)==len(expected)
for i,(a,b) in enumerate(zip(actual,expected)):
 if a!=b:print('FAIL',i,cases[i]['kind'],{k:(a[k],b[k]) for k in a if a[k]!=b[k]});raise SystemExit(1)
report=dict(scope='Actual416fe0 humanmodes1..4;41cd50 gated marker20 y<340;41de71 gated marker20 and fallback11. Caller owns preceding switch branches.',cases=len(cases),differences=0,records=[dict(input=c,output=e) for c,e in zip(cases,expected)])
(ROOT/'analysis/traces/mean-right-gate-original.json').write_text(json.dumps(report,separators=(',',':'))+'\n');print('PASS',len(cases))
