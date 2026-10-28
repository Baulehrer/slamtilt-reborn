#!/usr/bin/env python3
"""Compare native lamp frames and the bounded consumer with Retail instructions.

Original images, DAT-derived data and RGBA dumps remain below build/.
Requires the existing pefile/Unicorn venv and table_lamp_tests executable.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import struct
import subprocess

import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.x86_const import (
    UC_X86_REG_EAX, UC_X86_REG_EDX, UC_X86_REG_ESP, UC_X86_REG_EIP,
)

ROOT = Path(__file__).resolve().parents[1]
SHA = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
DAT_BASE, CANVAS, DAMAGE = 0x1100000, 0x4a0000, 0x100c000
PALETTES = {'mean': 0x1590c8, 'pirate': 0x14605c,
            'space': 0x14c035, 'demon': 0x146830}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def put(u, address, value):
    u.mem_write(address, struct.pack('<I', value & 0xffffffff))


def get(u, address):
    return struct.unpack('<I', u.mem_read(address, 4))[0]


def run(u, address, eax=0, edx=0, stop=0x2100000):
    put(u, 0x200f000, 0x2100000)
    u.reg_write(UC_X86_REG_ESP, 0x200f000)
    u.reg_write(UC_X86_REG_EAX, eax)
    u.reg_write(UC_X86_REG_EDX, edx)
    u.emu_start(address, stop, count=1000000)
    assert u.reg_read(UC_X86_REG_EIP) == stop


def machine(image, dat):
    u = Uc(UC_ARCH_X86, UC_MODE_32)
    for address, size in [(0x400000, 0x100000), (DAT_BASE, 0x200000),
                          (0x1000000, 0x10000), (0x2000000, 0x10000),
                          (0x2100000, 0x1000)]:
        u.mem_map(address, size)
    u.mem_write(0x400000, image)
    u.mem_write(DAT_BASE, dat)
    return u


def prepare(image, dat, profile):
    u = machine(image, dat)
    heap = 0x4e0000

    def initialization_service(uc, address, size, user):
        nonlocal heap
        if address == 0x40f7e0:
            value = DAT_BASE
        else:
            value = heap
            heap += (uc.reg_read(UC_X86_REG_EDX) + 15) & ~15
            assert heap < 0x500000
        uc.reg_write(UC_X86_REG_EAX, value)
        sp = uc.reg_read(UC_X86_REG_ESP)
        uc.reg_write(UC_X86_REG_EIP, get(uc, sp))
        uc.reg_write(UC_X86_REG_ESP, sp + 4)

    for address in (0x40f7e0, 0x40f740):
        u.hook_add(UC_HOOK_CODE, initialization_service,
                   begin=address, end=address)
    run(u, 0x405a3a, stop=0x405b90)
    run(u, 0x40bbac)
    run(u, int(profile['initializer'], 16), 0x46c67c, 0x46b748)
    returned = u.reg_read(UC_X86_REG_EAX)
    assert returned == int(profile['returned_descriptor'], 16)
    put(u, 0x46c644, returned)
    count = get(u, 0x46c6a4)
    metadata = get(u, returned + 8)
    descriptors = get(u, metadata + 0x10)
    rows = []
    for i in range(count):
        address = get(u, descriptors + i * 4)
        x, y, width, height, state, _, parent, mask = struct.unpack(
            '<6hII', u.mem_read(address, 20))
        rows.append(dict(id=i, descriptor=hex(address), x=x, y=y,
                         width=width * 16, height=height, state=state,
                         parent=hex(parent), mask_offset=hex(mask - DAT_BASE)))
    return bytes(u.mem_read(0x400000, 0x100000)), dict(
        count=count, metadata=hex(metadata), descriptor_table=hex(descriptors),
        status_commands=hex(get(u, metadata + 4)),
        alternate_commands=hex(get(u, metadata + 0xc)), rows=rows)


def bind_renderer(u, dat, palette):
    put(u, 0x46c724, CANVAS)
    put(u, 0x46c708, 320)
    put(u, 0x46c484, DAMAGE)
    u.mem_write(CANVAS, dat[palette + 1024:palette + 1024 + 320 * 600])
    u.mem_write(DAMAGE, struct.pack('<HH', 320, 0) * 600)


def verify_frames(image, dat, table, manifest, dumps):
    u = machine(image, dat)  # No code/service hooks in pixel execution.
    palette = PALETTES[table]
    pixels = dat[palette + 1024:palette + 1024 + 320 * 600]
    bind_renderer(u, dat, palette)
    cases, compared, visible_total = [], 0, 0
    combined = hashlib.sha256()
    for row in manifest['rows']:
        descriptor = int(row['descriptor'], 16)
        isolated = bytearray(u.mem_read(descriptor, 20))
        isolated[12:16] = bytes(4)  # Exclude dynamic parent/sprite effects.
        x, y, width, height = (row[k] for k in ('x', 'y', 'width', 'height'))
        offset = int(row['mask_offset'], 16)
        mask = dat[offset:offset + width * height // 8]
        for on, entry in [(0, 0x40b2ec), (1, 0x40b0b4)]:
            u.mem_write(CANVAS, pixels)
            u.mem_write(0x1000000, bytes(isolated))
            run(u, entry, 0x1000000)
            state = struct.unpack('<H', u.mem_read(0x1000008, 2))[0]
            assert state == (0xffff if on else 0)
            actual = bytes(u.mem_read(CANVAS, len(pixels)))
            expected = bytearray(pixels)
            native = (dumps / f"{table}-{row['id']}-{on}.rgba").read_bytes()
            assert len(native) == width * height * 4
            visible = 0
            for i in range(width * height):
                xx, yy = i % width, i // width
                pos = (y + yy) * 320 + x + xx
                covered = bool(mask[yy * (width // 8) + xx // 8] &
                               (128 >> (xx % 8)))
                if covered:
                    expected[pos] = pixels[pos] & 127 if on else pixels[pos] | 128
                    visible += 1
                assert native[i * 4 + 3] == (255 if covered else 0)
                background = dat[palette + pixels[pos] * 4 + 1:
                                 palette + pixels[pos] * 4 + 4]
                rgb = native[i * 4:i * 4 + 3] if covered else background
                original = dat[palette + actual[pos] * 4 + 1:
                               palette + actual[pos] * 4 + 4]
                assert rgb == original, (table, row['id'], on, i)
            assert actual == bytes(expected), (table, row['id'], on)
            combined.update(actual)
            compared += width * height
            visible_total += visible
            cases.append(dict(id=row['id'], on=on, descriptor=row['descriptor'],
                              anchor=[x, y], dimensions=[width, height],
                              state_word=state, visible_pixels=visible,
                              original_canvas_sha256=digest(actual),
                              native_rgba_sha256=digest(native), differences=0))
    return dict(table=table, lamps=manifest['count'], frames=len(cases),
                compared_pixels=compared, visible_mask_pixels=visible_total,
                original_canvas_sha256=combined.hexdigest(), differences=0,
                cases=cases)


def verify_consumer(image, dat, manifest):
    """Four bounded command frames, including unchanged original parent links."""
    u = machine(image, dat)
    bind_renderer(u, dat, PALETTES['pirate'])
    run(u, 0x404f09, stop=0x404f62)
    run(u, 0x405057, stop=0x405079)
    for address in (0x46c6cc, 0x46c63c, 0x454d88):
        put(u, address, 0)
    count, commands = manifest['count'], int(manifest['status_commands'], 16)
    events, writes = Counter(), Counter()

    def entered(uc, address, size, user):
        events[hex(address)] += 1

    def written(uc, access, address, size, value, user):
        if not (CANVAS <= address < CANVAS + 320 * 600):
            writes[(hex(address), size, hex(uc.reg_read(UC_X86_REG_EIP)))] += 1

    for address in (0x40b0b4, 0x40b2ec, 0x405bb4):
        u.hook_add(UC_HOOK_CODE, entered, begin=address, end=address)
    u.hook_add(UC_HOOK_MEM_WRITE, written, begin=0x400000, end=0x4fffff)
    before = bytes(u.mem_read(0x400000, 0x100000))
    rng, frames = random.Random(0x408da8), []
    for frame in range(4):
        command_bytes = bytes(v for _ in range(count)
                              for v in [rng.randrange(1, 7), rng.randrange(1, 5),
                                        rng.randrange(1, 5), rng.randrange(1, 5)])
        u.mem_write(commands, command_bytes)
        run(u, 0x4053ed, stop=0x4053f8)  # Original 50-Hz budget reset, EDX0.
        run(u, 0x408da8)
        states = [struct.unpack('<H', u.mem_read(int(r['descriptor'], 16) + 8, 2))[0]
                  for r in manifest['rows']]
        assert all(s in (0, 0xffff) for s in states)
        assert get(u, 0x46c63c) == count and get(u, 0x454d88) == 0
        frames.append(dict(frame=frame, input_commands_sha256=digest(command_bytes),
                           state_words=states, canvas_sha256=digest(
                               bytes(u.mem_read(CANVAS, 320 * 600)))))
    after = bytes(u.mem_read(0x400000, 0x100000))
    changed = [hex(0x400000 + i) for i in range(0, len(before), 2)
               if before[i:i + 2] != after[i:i + 2] and
               not CANVAS <= 0x400000 + i < CANVAS + 320 * 600]
    assert events['0x40b0b4'] and events['0x40b2ec']
    return dict(table='pirate', original_function='0x408da8',
                frames=frames, original_calls=dict(events), service_stubs=[],
                dynamic_parent_links='retained, all four Pirate links execute',
                changed_image_words=changed,
                image_write_log=[dict(address=a, size=s, pc=p, count=n)
                                 for (a, s, p), n in sorted(writes.items())])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, default=ROOT / (
        'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/'
        'Game Files/SLAMTILT/SLAMTILT.EXE'))
    parser.add_argument('--dat', type=Path)
    parser.add_argument('--native', type=Path, default=ROOT / 'build/native/table_lamp_tests')
    parser.add_argument('--work', type=Path, default=ROOT / 'build/oracle/table-lamps')
    parser.add_argument('--output', type=Path, default=ROOT / 'analysis/table-lamps-original.json')
    args = parser.parse_args()
    work = args.work.resolve()
    if not work.is_relative_to(ROOT / 'build'):
        parser.error('--work must remain below build/: original binary data')
    work.mkdir(parents=True, exist_ok=True)
    raw = args.exe.read_bytes()
    assert digest(raw) == SHA
    pe = pefile.PE(data=raw)
    image = bytearray(pe.get_memory_mapped_image())
    image.extend(bytes(0x100000 - len(image)))
    for section in pe.sections:
        if section.Name.rstrip(b'\0') == b'.bss':
            start, size = section.VirtualAddress, section.Misc_VirtualSize
            image[start:start + size] = bytes(size)
    profiles = json.loads((ROOT / 'analysis/table-profiles.json').read_text())
    assert profiles['build_sha256'] == SHA
    corpus = args.dat or args.exe.parent / 'DAT'
    manifests, prepared, data = {}, {}, {}
    for name, profile in profiles['tables'].items():
        dat = (corpus / f'{name.upper()}.DAT').read_bytes()
        assert digest(dat) == profile['dat_sha256']
        prepared[name], manifests[name] = prepare(bytes(image), dat, profile)
        data[name] = dat
        (work / f'{name}-image.bin').write_bytes(prepared[name])
    dumps = work / 'rgba'
    subprocess.run([str(args.native.resolve()), str(corpus.resolve()), str(work),
                    str(dumps)], cwd=ROOT, check=True)
    report = dict(schema=1, build_sha256=SHA, tables=[],
                  pixel_scope='Static table overlays; parent+0c cleared in descriptor copy',
                  renderer_bindings={'0x46c724': hex(CANVAS), '0x46c708': 320,
                                     '0x46c484': hex(DAMAGE)},
                  preparation_adapters=['0x40f7e0', '0x40f740'])
    for name in manifests:
        result = verify_frames(prepared[name], data[name], name, manifests[name], dumps)
        report['tables'].append(result)
        print(name, 'PASS', result['frames'], 'frames', result['compared_pixels'], 'pixels')
    report['consumer'] = verify_consumer(prepared['pirate'], data['pirate'], manifests['pirate'])
    (work / 'profiles.json').write_text(json.dumps(manifests, indent=2) + '\n')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('Pirate complete consumer PASS: four command frames, original blits, no service stubs')


if __name__ == '__main__':
    main()
