#!/usr/bin/env python3
"""Bounded original41ada4 vs native116<=Y<270 ball-object comparison."""
import json
import random
import struct
import subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ESP, UC_X86_REG_EIP

ROOT = Path(__file__).resolve().parents[1]
u = Uc(UC_ARCH_X86, UC_MODE_32)
u.mem_map(0x400000, 0x100000)
u.mem_map(0x1000000, 0x10000)
u.mem_map(0x2000000, 0x10000)
image = (ROOT / 'build/mean-prepared/pe-data.bin').read_bytes()
u.mem_write(0x400000, image)
def put(address, value):
    u.mem_write(address, struct.pack('<I', value))
for layer, offsets in enumerate([
    (3, 0x6040, 0x959f6, 0x9ba36, 0xb3b36),
    (1, 0x60e0, 0xb98f6, 0xbf9d6, 0xcbb96),
    (1, 0x3390, 0xd1956, 0xd4ce6, 0xdb406),
    (1, 0x41a0, 0xde796, 0xe2936, 0xeac76),
    (1, 0x3390, 0xd20d6, 0xd5466, 0xdb406)]):
    for index, value in enumerate(offsets):
        put(0x43f06c + layer * 20 + index * 4,
            value + (0x1100000 if index >= 2 else 0))
# Rule-only140<=Y<160 path: skip after the branch is selected.
# There are no ball writes anywhere in41b2d5..41b491.
def external(uc, address, size, context):
    uc.reg_write(UC_X86_REG_EIP, 0x41b615)
u.hook_add(UC_HOOK_CODE, external, begin=0x41b2d5, end=0x41b2d5)
put(0x43f0d0, 0x1001000)
put(0x1001010, 0x1002000)
def skip_rules(uc, address, size, context):
    uc.reg_write(UC_X86_REG_EIP, 0x41c8af)
u.hook_add(UC_HOOK_CODE, skip_rules, begin=0x41c7c1, end=0x41c7c1)
rng = random.Random(14133)
cases = []
expected = []
for i in range(1600):
    ball = bytearray(rng.randbytes(100))
    x = rng.choice([100 * 65536 - 1, 100 * 65536,
                    100 * 65536 + 1, 175 * 65536 - 1,
                    175 * 65536, rng.randrange(320 * 65536)])
    y = rng.choice([116 * 65536, 140 * 65536 - 1,
                    140 * 65536, 160 * 65536 - 1,
                    160 * 65536, 230 * 65536 - 1,
                    230 * 65536, 270 * 65536 - 1,
                    rng.randrange(116 * 65536, 270 * 65536)])
    struct.pack_into('<ii', ball, 0, x, y)
    struct.pack_into('<H', ball, 0x48, 3)
    struct.pack_into('<H', ball, 0x38, 1)
    start = 0x41ada4
    if i >= 1200:
        struct.pack_into('<ii', ball, 0, rng.choice([230*65536,268*65536,rng.randrange(230*65536,320*65536)]), rng.choice([160*65536,240*65536-1,240*65536,280*65536-1,rng.randrange(160*65536,280*65536)]))
        struct.pack_into('<H', ball, 0x48, 1)
        put(0x100101c, 0)
        start = 0x41c464
    elif i >= 800:
        if i < 1000:
            struct.pack_into('<ii', ball, 0, rng.randrange(160*65536, 212*65536), rng.randrange(150*65536,608*65536))
            struct.pack_into('<H', ball, 0x48, 2)
            start = 0x41bdd0
        else:
            struct.pack_into('<i', ball, 0, rng.choice([204*65536-1,204*65536,204*65536+1,rng.randrange(320*65536)]))
            struct.pack_into('<H', ball, 0x48, 4)
            struct.pack_into('<H', ball, 0x38, i%4)
            start = 0x41ac7c
    cases.append(list(ball))
    u.mem_write(0x1000000, bytes(ball))
    put(0x200f000, 0x200fff0)
    u.reg_write(UC_X86_REG_ESP, 0x200f000)
    u.reg_write(UC_X86_REG_EAX, 0x1000000)
    u.emu_start(start, 0x200fff0, count=1000)
    expected.append(list(u.mem_read(0x1000000, 100)))
probe = ROOT / 'build/oracle/mean_ramp_probe'
subprocess.run(['c++', '-std=c++17', '-Isrc', '-Ibuild/native/_deps/json-src/include',
                'tests/mean_ramp_probe.cpp', 'src/physics/mean_ramp_bundle.cpp',
                'src/physics/mean_step.cpp', 'src/physics/mean_material_bundle.cpp', '-o', str(probe)], cwd=ROOT, check=True)
actual = json.loads(subprocess.check_output([str(probe)], input=json.dumps(cases), text=True))
differences = [i for i, (a, b) in enumerate(zip(expected, actual)) if a != b]
report = {'original': '41ada4 bounded41b273..41b615; layer2entry41c300; layer4switch41ac7c; layer1right41c78c..41c84d', 'cases': len(cases),
          'differences': differences,
          'scope': 'All100 ball bytes; rule-only140<=Y<160 branch skipped after selection; original contains no ball writes there',
          'branches': {'116<=Y<140': 'layer2,+5c9,+1c10,+60=0x601',
                       'layer1,mask1,X>=230,160<=Y<240': 'human services+1c0:+5c13,+1c20,+600x3000; field_player_08+=500000, not score',
                       'layer1,mask1,X>=230,240<=Y<280': 'layer0,+220,+2a0xaa,+5c11,+1c10,+600x1801,+28120',
                       'layer2,mask1,Y>=150,160<=X<212': 'layer4 only,41c300..41c341',
                       'layer4,mask0': '+2840,+220,+2a0,+5c8,+1c40,+600x180',
                       'layer4,mask1': 'layer2 if fixedX<204 else layer3',
                       'layer4,mask>1': 'ball unchanged',
                       '140<=Y<160': 'ball unchanged; field_player_08+=500000 at41b2e8 (not score service); external rules/lamps',
                       '160<=Y<270,100<X<175': 'layer2',
                       '160<=Y<230,X<=100': 'layer0,+220,+2a0xf8e,+5c7,+1c10,+600x181,+28120',
                       '230<=Y<270,X<=100': 'layer1,+5c6,+1c20,+600x60',
                       '160<=Y<270,X>=175': 'layer2,+220,+2a0,+5c3,+1c0,+600x1c,+2840'}}
(ROOT / 'analysis/mean-ramp-bundle.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
if differences:
    i = differences[0]
    print(i, [(n,a,b) for n,(a,b) in enumerate(zip(expected[i], actual[i])) if a != b])
    raise SystemExit(1)
