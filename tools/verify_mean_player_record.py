#!/usr/bin/env python3
import json,struct,subprocess,sys,hashlib,random
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EIP
r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
rng=random.Random(8000);cases=[];expected=[]
for n in range(32):
 raw=bytes([n]*416) if n<8 else rng.randbytes(416)
 u.mem_write(0x43ee24,raw);u.mem_write(0x100f000,struct.pack('<I',0x100fff0));u.reg_write(UC_X86_REG_ESP,0x100f000);u.emu_start(0x419e68,0x100fff0,count=10000)
 assert u.reg_read(UC_X86_REG_EIP)==0x100fff0
 for player in range(8):
  cases.append(list(raw[player*52:player*52+52]));expected.append(list(u.mem_read(0x43ee24+player*52,52)))
actual=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases),text=True));assert actual==expected
(r/'analysis/traces/mean-player-record-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Actual419e68 eight-player records,32 sentinel/random contexts; bytes17/23/29 preserved, record04/12hex=4,22hex=8000; native frontend singleplayer',cases=cases,expected=expected),separators=(',',':'))+'\n')
print('256 original/native player initializer records exact')
