#!/usr/bin/env python3
"""Verify sequential original flipper edge-input/pose updates against native lift."""
import json
import struct
import subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_ESP

ROOT = Path(__file__).resolve().parents[1]
base = ROOT / 'build/mean-prepared'
image = bytearray((base / 'pe-data.bin').read_bytes())
image.extend(bytes(0x100000 - len(image)))
image[0x3e700:0x3e7a0] = (base / 'engine-globals.bin').read_bytes()
poses = (base / 'flipper-state.bin').read_bytes()
image[0x3e850:0x3e850 + len(poses)] = poses
u = Uc(UC_ARCH_X86, UC_MODE_32)
u.mem_map(0x400000, 0x100000)
u.mem_write(0x400000, bytes(image))
u.mem_map(0x2000000, 0x10000)
u.mem_map(0x2100000, 0x1000)
inputs = []
expected = []
for tick in range(240):
    left = 1 if tick in (5, 70, 180) else 0xffffffff if tick in (30, 150, 220) else 0
    right = 1 if tick in (10, 100, 170) else 0xffffffff if tick in (60, 140, 230) else 0
    inputs.append([left, right])
    for address, value in ((0x4298b8, left), (0x4298bc, right), (0x4298c0, right)):
        u.mem_write(address, struct.pack('<I', value))
    u.mem_write(0x200f000, struct.pack('<I', 0x2100000))
    u.reg_write(UC_X86_REG_ESP, 0x200f000)
    u.emu_start(0x4084bc, 0x2100000, count=10000)
    expected.append(list(u.mem_read(0x43e850, 78)))
path = ROOT / 'build/oracle/flipper-input-cases.json'
path.write_text(json.dumps([dict(operation='pose', inputs=inputs)]))
native = json.loads(subprocess.check_output([str(ROOT / 'build/native/flipper_probe'), str(base), str(path)], text=True))[0]
differences = [i for i, (a, b) in enumerate(zip(expected, native)) if a != b]
report = dict(steps=len(inputs), differences=differences,
              distinct_poses=len({bytes(x) for x in expected}),
              writer='0x4084bc', edge_inputs=['0x4298b8', '0x4298bc', '0x4298c0'])
(ROOT / 'analysis/traces/mean-flipper-input-validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
assert len(native) == len(expected) and not differences
assert report['distinct_poses'] > 10
