#!/usr/bin/env python3
"""Original408a18/417148 vs isolated native, synthetic records/original LUT."""
import json,struct,subprocess,sys
from pathlib import Path
exec((Path(__file__).parent/'trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
lut=(ROOT/'build/mean-prepared/lookup.bin').read_bytes();u.mem_write(0x1006000,lut)
for a,v in [(0x43e764,0x1006000),(0x4298c8,0x1000000),(0x43e740,0x1005000),(0x1005000,0x1005100),(0x1005104,0x1005200),(0x1005200,0x1005300)]:put(a,v)
cases=[];expected=[]
actual_record=list(struct.unpack_from("<6h",(ROOT/"build/mean-prepared/pe-data.bin").read_bytes(),0x38a48))
def call(a,eax):
 put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,eax);u.emu_start(a,0x200fff0,count=1000)
for boundary in [False,True]:
 for phase in [-1,0x30b1d5,0x30b1d6,0x30b1d7,0x6163ab,0x6163ac,0x6163ad,10000000]:
  for speed in [-0x30000,0,0x20000,0x30000]:
   for rec in [[160,300,50,0,100,20],[20,100,30,1024,-100,40],[160,300,100,2048,20,-10],actual_record]:
    b=bytearray(100);struct.pack_into('<ii',b,0,100<<16,200<<16);struct.pack_into('<iiH',b,0x2c,phase,speed,0);struct.pack_into('<H',b,0x58,7)
    u.mem_write(0x1000000,bytes(b));u.mem_write(0x1005300,struct.pack('<6h',*rec));call(0x417148 if boundary else 0x408a18,0x1000000 if boundary else 0)
    cases.append(dict(ball=list(b),boundary=boundary,record=rec));expected.append(dict(ball=list(u.mem_read(0x1000000,100)),transitioned=boundary and phase>0x6163ac))
exe=sys.argv[1] if len(sys.argv)>1 else str(ROOT/'build/native/mean_state7_probe')
actual=json.loads(subprocess.check_output([exe,str(ROOT/'build/mean-prepared/lookup.bin')],input=json.dumps(cases).encode()))
for i,(a,e) in enumerate(zip(actual,expected)):
 if a!=e:print('FAIL',i,cases[i],a,e);raise SystemExit(1)
# Original417148 precedes408a18; trace actual directory record to held-ball boundary.
b=bytearray(100);struct.pack_into('<iiH',b,0x2c,0x30b1d6,0x30000,0);struct.pack_into('<H',b,0x58,7)
u.mem_write(0x1000000,bytes(b));u.mem_write(0x1005300,struct.pack('<6h',*actual_record));cycle=[]
for tick in range(1000):
 before=list(u.mem_read(0x1000000,100));call(0x417148,0x1000000);after=list(u.mem_read(0x1000000,100));transition=word(0x1000058)==3
 cases.append(dict(ball=before,boundary=True,record=actual_record));expected.append(dict(ball=after,transitioned=transition))
 if not transition:
  call(0x408a18,0);cases.append(dict(ball=after,boundary=False,record=actual_record));expected.append(dict(ball=list(u.mem_read(0x1000000,100)),transitioned=False))
 cycle.append(dict(tick=tick+1,ball=list(u.mem_read(0x1000000,100))))
 if transition:break
actual=json.loads(subprocess.check_output([exe,str(ROOT/'build/mean-prepared/lookup.bin')],input=json.dumps(cases).encode()))
assert actual==expected
report=dict(actual_record_address='0x438a48',actual_record=actual_record,cycle=cycle,scope='Original408a18 and417148; synthetic directory records, actual original LUT; no full gameplay equivalence',cases=len(cases),differences=0,records=[dict(input=c,output=e) for c,e in zip(cases,expected)])
(ROOT/'analysis/traces/mean-state7-original.json').write_text(json.dumps(report,separators=(',',':'))+'\n');print('PASS',len(cases))
