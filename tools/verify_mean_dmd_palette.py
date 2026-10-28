#!/usr/bin/env python3
"""Actual Windows descriptor installation and DMD indexed transfer -> user RGB."""
import argparse, hashlib, json, struct, subprocess
from pathlib import Path
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EDX, UC_X86_REG_ESP
p = argparse.ArgumentParser(); p.add_argument('--native', required=True); args = p.parse_args()
r = Path(__file__).resolve().parents[1]
base = r/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT'
raw = (base/'SLAMTILT.EXE').read_bytes(); dat = (base/'DAT/MEAN.DAT').read_bytes()
image = pefile.PE(data=raw).get_memory_mapped_image()
u = Uc(UC_ARCH_X86, UC_MODE_32); u.mem_map(0x400000, 0x100000); u.mem_write(0x400000, image)
u.mem_map(0x1000000, 0x200000); u.mem_write(0x1000000, dat)
u.mem_map(0x1300000, 0x10000)
def put(a, v): u.mem_write(a, struct.pack('<I', v))
def get(a): return struct.unpack('<I', u.mem_read(a, 4))[0]
put(0x43e740, 0x438ae4)
u.emu_start(0x404598, 0x4045aa, count=20)
assert get(0x43e3f4) == 0x438a38
u.reg_write(UC_X86_REG_EAX, 0x1000000)
u.emu_start(0x40f148, 0x40f159, count=20)
assert get(0x438a30) == 0x1000000 + 0x1590c8
indices = list(u.mem_read(get(0x43e3f4), 4))
levels = bytes((x + 3*y) % 4 for y in range(20) for x in range(96))
u.mem_write(0x1300000, levels); put(0x43e3e8, 0x1300000)
put(0x130f000, 0x130fff0); u.reg_write(UC_X86_REG_ESP, 0x130f000)
u.reg_write(UC_X86_REG_EAX, 0x1302000); u.reg_write(UC_X86_REG_EDX, 160)
u.emu_start(0x40576c, 0x130fff0, count=100000)
assert u.reg_read(UC_X86_REG_ESP) == 0x130f004
out = bytes(u.mem_read(0x1302000 + 0x540, 20*320))
actual = bytes(out[y*320+x*2] for y in range(20) for x in range(96))
assert actual == bytes(indices[v] for v in levels)
rgba = [list(dat[0x1590c8 + i*4 + 1:0x1590c8 + i*4 + 4]) + [255] for i in indices]
native = [list(map(int, line.split())) for line in subprocess.check_output([args.native, str(base/'DAT/MEAN.DAT')], text=True).splitlines()]
assert native == rgba, (native, rgba)
fixture = dict(build_sha256=hashlib.sha256(raw).hexdigest(), dat_sha256=hashlib.sha256(dat).hexdigest(),
    status='VERIFIED', descriptor='0x438a18', lookup='0x438a38', installer='0x404598..0x4045aa',
    transfer='0x40576c..0x405813', palette_initializer='0x40f148..0x40f159', palette_offset='0x1590c8',
    indices=indices, rgba=rgba, pixel_count=len(levels), indexed_output_sha256=hashlib.sha256(actual).hexdigest(),
    scope='Actual original descriptor installation and indexed DMD transfer, then original DAT RGB lookup. No simulated DirectDraw mode or live screenshot comparison.')
(r/'analysis/traces/mean-dmd-palette-original.json').write_text(json.dumps(fixture, indent=2)+'\n')
print('1920 actual original DMD indices and four native RGB colors match:', rgba)
