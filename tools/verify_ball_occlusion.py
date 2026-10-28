#!/usr/bin/env python3
"""Native 240-byte mask versus actual demo 40abc8..40aceb, original user DAT."""
import hashlib, json, random, struct, subprocess, sys
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ESP
ROOT = Path(__file__).resolve().parents[1]
folder = ROOT / 'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT'
main = (folder / 'MAIN.DAT').read_bytes()
dat = (folder / 'MEAN.DAT').read_bytes()
image = (ROOT / 'build/mean-prepared/pe-data.bin').read_bytes()
u = Uc(UC_ARCH_X86, UC_MODE_32)
for address, size in [(0x400000, 0x100000), (0x1000000, 0x10000), (0x1100000, 0x200000), (0x1400000, 0x10000), (0x2000000, 0x10000)]:
    u.mem_map(address, size)
u.mem_write(0x400000, image)
u.mem_write(0x1100000, dat)
u.mem_write(0x1400000, main)
def put(address, value):
    u.mem_write(address, struct.pack('<I', value))
put(0x43e82c, 0x1400000)
put(0x4298c8, 0x1000000)
put(0x43d7e0, 0x1001000)
# Original engine initialization nibble expansion, MSB-first bytes.
for n in range(16):
    put(0x43d7a0 + n * 4, sum((255 if n & (1 << (3-j)) else 0) << (j*8) for j in range(4)))
outline = main[0x88a4:0x88a4+240]
cases = []
rng = random.Random(0x40abc8)
offsets = [0xb3b36, 0xcbb96, 0xdb406, 0xeac76, 0xcbb96-14]
for offset in offsets:
    for x in list(range(16)) + [295, 296, 297, 302, 303]:
        for y in [0, 1, 63, 89, 115, 170, 279, 337, 500, 599]:
            cases.append(dict(offset=offset, x=x, y=y, flag=1))
    for _ in range(200):
        cases.append(dict(offset=offset, x=rng.randrange(304), y=rng.randrange(600), flag=1))
for flag in [0, 1, 2, 0xffff]:
    for x, y in [(-1, 0), (304, 0), (0, -1), (0, 600), (303, 599), (0, 0)]:
        cases.append(dict(offset=0xcbb96, x=x, y=y, flag=flag))
expected = []
for c in cases:
    ball = bytearray(100)
    struct.pack_into('<hh', ball, 0x10, c['x'], c['y'])
    struct.pack_into('<H', ball, 0x20, c['flag'])
    struct.pack_into('<I', ball, 0x54, 0x1100000+c['offset'])
    u.mem_write(0x1000000, bytes(ball))
    u.mem_write(0x1001000, outline)
    put(0x200f000, 0x200fff0)
    u.reg_write(UC_X86_REG_ESP, 0x200f000)
    u.reg_write(UC_X86_REG_EAX, 0)
    u.emu_start(0x40abc8, 0x200fff0, count=2000)
    expected.append(dict(flag=struct.unpack('<H', u.mem_read(0x1000020, 2))[0], mask=list(u.mem_read(0x1001000, 240))))
exe = sys.argv[1] if len(sys.argv) > 1 else str(ROOT/'build/oracle/ball_occlusion_probe')
if len(sys.argv) == 1:
    subprocess.run(['c++', '-std=c++17', '-Isrc', '-Ibuild/native/_deps/json-src/include', 'tests/ball_occlusion_probe.cpp', 'src/assets/ball_mask.cpp', 'src/assets/ball_occlusion.cpp', '-o', exe], cwd=ROOT, check=True)
actual = json.loads(subprocess.check_output([exe, str(folder/'MAIN.DAT'), str(folder/'MEAN.DAT')], input=json.dumps(cases).encode()))
assert len(actual) == len(expected)
for i, (a, e) in enumerate(zip(actual, expected)):
    assert a == e, (i, cases[i], a['flag'], e['flag'])
report = dict(scope='Actual demo40abc8..40aceb, user MAIN/MEAN.DAT; original engine nibble LUT supplied explicitly; all 240 output bytes and refresh flag compared. Includes object+54=cbb96-14, all bit alignments and invalid clipping/refresh guards. Native helper accepts valid drawing bounds; outer guard lives in probe/renderer.',
              entry='0x40abc8', prepared_sha256=hashlib.sha256(image).hexdigest(),
              main_sha256=hashlib.sha256(main).hexdigest(), mean_sha256=hashlib.sha256(dat).hexdigest(),
              cases=len(cases), differences=0,
              records=[dict(input=c, output_sha256=hashlib.sha256(bytes(e['mask'])).hexdigest(), flag=e['flag']) for c,e in zip(cases,expected)])
(ROOT/'analysis/traces/ball-occlusion-original.json').write_text(json.dumps(report, separators=(',', ':'))+'\n')
print('PASS', len(cases), 'original occlusion masks + guard flags')
