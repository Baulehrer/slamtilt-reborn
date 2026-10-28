#!/usr/bin/env python3
"""Original layer0 switch dispatcher:41c966 calls right/left capture only for mask3."""
import json,hashlib,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EDX
r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image)
seen=[]
def hook(uc,a,n,c):
 if a in [0x41c951,0x41c958,0x41c95f,0x41c966,0x41c96d,0x41c972]:seen.append(a);uc.emu_stop()
u.hook_add(UC_HOOK_CODE,hook);rows=[]
for mask in range(6):
 seen.clear();u.reg_write(UC_X86_REG_EDX,mask);u.emu_start(0x41c93d,0,count=50)
 rows.append(dict(mask=mask,target=hex(seen[0]),capture=seen[0]==0x41c966))
assert [a['mask'] for a in rows if a['capture']]==[3]
(r/'analysis/traces/mean-right-capture-dispatch-original.json').write_text(json.dumps(dict(prepared_sha256=hashlib.sha256(image).hexdigest(),scope='Actual41c93d switch-mask jump-table dispatch,41c966 directcall41d94c; excludes callbackeffects',cases=rows),indent=2)+'\n')
print('PASS original capture dispatch onlyswitchmask3')
