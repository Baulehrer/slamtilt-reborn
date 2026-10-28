#!/usr/bin/env python3
import json,struct,hashlib,sys
from pathlib import Path
exec((Path(__file__).parent/'trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
DAT=ROOT/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT';dat=DAT.read_bytes();u.mem_map(0x3000000,0x40000);u.mem_map(0x1100000,0x200000);u.mem_write(0x1100000,dat)
u.hook_add(UC_HOOK_CODE,stub,begin=0x4052b0,end=0x4052b0)
put(0x43e820,0x3000000);put(0x43e83c,320)
for n in range(16):put(0x43d7a0+n*4,sum((255 if n&(1<<(3-j)) else 0)<<(j*8) for j in range(4)))
profiles=json.loads((ROOT/'analysis/mean-lamp-descriptors.json').read_text());pixels=dat[0x1590c8+1024:0x1590c8+1024+320*600];fixture=[];off="--off" in sys.argv
for p in profiles:
 u.mem_write(0x3000000,pixels);u.mem_write(0x1000000,struct.pack('<hhhhhhII',p['x'],p['y'],p['width']//16,p['height'],0,0,0,0x1100000+p['offset']))
 put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x40a654 if off else 0x40a41c,0x200fff0,count=30000)
 expected=bytearray(pixels);w=p['width'];h=p['height'];mask=dat[p['offset']:p['offset']+w*h//8]
 for y in range(h):
  for x in range(w):
   if mask[y*(w//8)+x//8]&(128>>(x%8)):expected[(p['y']+y)*320+p['x']+x]=(expected[(p['y']+y)*320+p['x']+x]|128) if off else (expected[(p['y']+y)*320+p['x']+x]&127)
 actual=bytes(u.mem_read(0x3000000,len(pixels)));assert actual==expected,p
 fixture.append(dict(id=p['id'],on_canvas_sha256=hashlib.sha256(actual).hexdigest(),mask_sha256=hashlib.sha256(mask).hexdigest()))
(ROOT/('analysis/traces/mean-lamp-off-pixels-fixture.json' if off else 'analysis/traces/mean-lamp-pixels-fixture.json')).write_text(json.dumps(dict(scope=('Actual40a654 off' if off else 'Actual40a41c on')+' originalmasksource andpalettebitpatch; nibbleLUTexplicit, clip4052b0stub, parentptr0 excludesdynamicobjectocclusion. NativeMSBfirstonebitmask independentlymatchesall63pixelpatches.',cases=fixture),indent=2)+'\n');print('63 masks byte-exact')
