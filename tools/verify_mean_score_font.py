#!/usr/bin/env python3
"""Original406280 digit rendering versus native MAIN.DAT parser."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
exec((Path(__file__).parent/'trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
from unicorn.x86_const import UC_X86_REG_EBX,UC_X86_REG_ECX,UC_X86_REG_EDX
main=next((ROOT/'build/corpus/win95/demo-1997').rglob('MAIN.DAT'));data=main.read_bytes();u.mem_map(0x1100000,0x10000);u.mem_write(0x1100000,data);put(0x43e82c,0x1100000);put(0x43e3e8,0x1008000)
inputs=[];expected=[]
for score in [0,1,9,10,99,100,999,1000,123456,120000000,4294967294,4294967295,123456789012,999999999999]:
 for align,x in [(0,1),(1,12),(2,23)]:
  # Coordinates guarantee all writes stay inside 96x20.
  if x*4-align*4*len(str(score))<2 or x*4-align*4*len(str(score))+8*len(str(score))>96:continue
  u.mem_write(0x1008000,bytes(1920));put(0x200f000,0x200fff0);put(0x200f004,0x1007000)
  u.mem_write(0x1007000,bytes.fromhex(f'{score:012d}'))
  for r,v in [(UC_X86_REG_ESP,0x200f000),(UC_X86_REG_EAX,align),(UC_X86_REG_EBX,score if score<4294967295 else 4294967295),(UC_X86_REG_ECX,x),(UC_X86_REG_EDX,2)]:u.reg_write(r,v)
  u.emu_start(0x406280,0x200fff0,count=20000)
  inputs.append([score,x,2,align]);expected.append(list(u.mem_read(0x1008000,1920)))
probe=sys.argv[1] if len(sys.argv)>1 else 'build/oracle/mean_score_font_probe'
actual=json.loads(subprocess.check_output([probe,str(main)],input=json.dumps(inputs).encode()))
assert actual==expected,[(i,next((j,a,b) for j,(a,b) in enumerate(zip(x,y)) if a!=b)) for i,(x,y) in enumerate(zip(actual,expected)) if x!=y][:3]
fixture=dict(entry='0x406280',font_offset='0x8994',main_dat_sha256=hashlib.sha256(data).hexdigest(),cases=[dict(input=a,pixels_sha256=hashlib.sha256(bytes(b)).hexdigest()) for a,b in zip(inputs,expected)])
(ROOT/'analysis/traces/mean-score-font-fixture.json').write_text(json.dumps(fixture,separators=(',',':'))+'\n');print(json.dumps(dict(cases=len(inputs),pixels=len(inputs)*1920,differences=0)))
