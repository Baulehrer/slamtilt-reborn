#!/usr/bin/env python3
"""Actual419919..419944 timer/count/lamp mutations, ungated50Hz boundary."""
import hashlib,itertools,json,struct,subprocess,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
root=Path(__file__).resolve().parents[1];image=(root/'build/mean-prepared/pe-data.bin').read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image)
cases=[dict(timer=t,count=c,lamp=l) for t,c,l in itertools.product([-32768,-1,0,1,399,400,32767],[0,1,3,65535],[[4,4,1,0],[255,9,7,5]])]
# Full countdown sequence, including expired quiescence.
for t in range(400,-2,-1):cases.append(dict(timer=t,count=3 if t>=0 else 0,lamp=[4,4,1,0] if t>=0 else [2,4,1,0]))
expected=[]
for c in cases:
 u.mem_write(0x43f3b0,struct.pack('<h',c['timer']));u.mem_write(0x43f39a,struct.pack('<H',c['count']));u.mem_write(0x43f258,bytes(c['lamp']));u.emu_start(0x419919,0x419944,count=100)
 expected.append(dict(timer=struct.unpack('<h',u.mem_read(0x43f3b0,2))[0],count=struct.unpack('<H',u.mem_read(0x43f39a,2))[0],lamp=list(u.mem_read(0x43f258,4))))
actual=json.loads(subprocess.run([sys.argv[1]],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout);assert actual==expected
report=dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Actual419919..419944 ungated clock block;400->0 then401st clock expires/resetcount/onlylampbyte0; engine1c gate and full table scheduler excluded',cases=cases,expected=expected,differences=[])
(root/'analysis/traces/mean-skull-clock-original.json').write_text(json.dumps(report,separators=(',',':'))+'\n');print(len(cases),'Original/native skull clock states exact')
