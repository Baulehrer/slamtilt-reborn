#!/usr/bin/env python3
"""Compare native flipper composites with actual supported Retail instructions.

Original assets and native RGBA dumps stay below build/. Requires the existing
analysis venv (pefile/Unicorn) and the compiled table_sprite_tests executable.
"""
import argparse
import hashlib
import json
import math
import struct
import subprocess
from pathlib import Path

import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import (
    UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ESP, UC_X86_REG_EIP,
)

ROOT = Path(__file__).resolve().parents[1]
RETAIL_SHA = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
SPRITES = {
    'mean': [(0x464b0c, 0x6eabe), (0x464b30, 0x75b3e), (0x464b54, 0x7cbbe)],
    'pirate': [(0x4658cc, 0x64484), (0x4658f0, 0x6b504), (0x465914, 0x72584)],
    'space': [(0x4665c0, 0x6fd15), (0x4665e4, 0x76d95), (0x466608, 0x7de15)],
    'demon': [(0x463aec, 0x84bf6), (0x463b10, 0x8bc76)],
}
PALETTES = {'mean': 0x1590c8, 'pirate': 0x14605c,
            'space': 0x14c035, 'demon': 0x146830}


def machine(image):
    u = Uc(UC_ARCH_X86, UC_MODE_32)
    for address, size in [(0x400000, 0x100000), (0x1000000, 0x200000),
                          (0x2000000, 0x10000), (0x2100000, 0x1000)]:
        u.mem_map(address, size)
    u.mem_write(0x400000, image)
    return u


def put(u, address, value):
    u.mem_write(address, struct.pack('<I', value & 0xffffffff))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, default=ROOT / (
        'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/'
        'Game Files/SLAMTILT/SLAMTILT.EXE'))
    parser.add_argument('--dat', type=Path, help='DAT directory; defaults beside EXE')
    parser.add_argument('--native', type=Path,
                        default=ROOT / 'build/native/table_sprite_tests')
    parser.add_argument('--work', type=Path,
                        default=ROOT / 'build/oracle/table-sprites')
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'analysis/table-sprites.json')
    args = parser.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    profiles = json.loads((ROOT / 'analysis/table-profiles.json').read_text())
    raw = args.exe.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == RETAIL_SHA
    assert profiles['build_sha256'] == RETAIL_SHA
    image = pefile.PE(data=raw).get_memory_mapped_image()
    image = image + bytes(0x100000 - len(image))
    corpus = args.dat or args.exe.parent / 'DAT'
    dumps = args.work / 'rgba'
    subprocess.run([str(args.native.resolve()), str(corpus.resolve()),
                    str(dumps.resolve())], check=True, cwd=ROOT)
    report = {
        'schema': 1, 'status': 'VERIFIED bounded original sprite preparation',
        'build_sha256': RETAIL_SHA,
        'original_function': '0x40b71c',
        'descriptor_layout': {'geometry_layer': '+0x04 WORD', 'width': '+0x0c WORD',
                              'height': '+0x0e WORD', 'x': '+0x10 WORD',
                              'y': '+0x12 WORD', 'count': '+0x14 WORD',
                              'pixel_pointer': '+0x1c DWORD'},
        'frame_selector': {'instructions': '0x40b546..0x40b568',
                           'formula': 'min((pose>>10)+((pose>>9)&1),count-1)'},
        'mask': {'instructions': '0x40b79c..0x40b7ea',
                 'formula': 'transparent if palette index<=1 OR foreground bitmap bit is set',
                 'bitmap': 'selected geometry layer render_offset + Y*40 + X/8; bit7-(X&7)'},
        'flipper_pose': {'current': 'runtime descriptor+0x0a WORD',
                         'render_cache': 'runtime descriptor+0x14 WORD',
                         'copy': '0x4055d8..0x405612 copies current to render cache',
                         'draw': '0x4090e9..0x40913c passes cached pose; no interpolation here'},
        'scope': ('Original complete sprite preprocessing executes against pristine original DAT, '
                  'actual descriptor fields and actual table foreground bitmaps. Native alpha '
                  'composite compared with original modified palette indices for every sprite '
                  'pixel/frame. Full display scheduling and dynamic foreground changes excluded.'),
        'tables': [],
    }
    base = 0x1000000
    for table, sprites in SPRITES.items():
        dat = (corpus / (table.upper() + '.DAT')).read_bytes()
        dat_sha = hashlib.sha256(dat).hexdigest()
        assert dat_sha == profiles['tables'][table]['dat_sha256']
        pal = PALETTES[table]
        u = machine(image)
        u.mem_write(base, dat)
        put(u, 0x46c490, base + pal + 1024)
        returned = int(profiles['tables'][table]['returned_descriptor'], 16)
        put(u, 0x46c644, returned)
        put(u, returned + 8, 0x11ff000)
        put(u, 0x11ff000, 0x11fe000)
        for layer in profiles['tables'][table]['layers']:
            put(u, 0x11fe000 + layer['layer'] * 20 + 16, base + layer['render_offset'])
        compared = transparent = frames = 0
        digest = hashlib.sha256()
        sprite_rows = []
        for s, (descriptor, offset) in enumerate(sprites):
            layer, width, height, x, y, count = struct.unpack_from(
                '<H6x5H', image, descriptor - 0x400000 + 4)
            pixels = width * height
            put(u, descriptor + 0x1c, base + offset)
            put(u, 0x200f000, 0x2100000)
            u.reg_write(UC_X86_REG_ESP, 0x200f000)
            u.reg_write(UC_X86_REG_EAX, descriptor)
            u.emu_start(0x40b71c, 0x2100000, count=10000000)
            assert u.reg_read(UC_X86_REG_EIP) == 0x2100000
            original = bytes(u.mem_read(base + offset, pixels * count))
            digest.update(original)
            for frame in range(count):
                rgba = (dumps / f'{table}-{s}-{frame}.rgba').read_bytes()
                assert len(rgba) == pixels * 4
                for i in range(pixels):
                    index = original[frame * pixels + i]
                    expected = dat[pal + index * 4 + 1:pal + index * 4 + 4]
                    if rgba[i * 4 + 3]:
                        native = rgba[i * 4:i * 4 + 3]
                    else:
                        transparent += 1
                        bg = dat[pal + 1024 + (y + i // width) * 320 + x + i % width]
                        native = dat[pal + bg * 4 + 1:pal + bg * 4 + 4]
                    assert native == expected, (table, s, frame, i, native, expected)
                    compared += 1
                frames += 1
            sprite_rows.append({'descriptor': hex(descriptor), 'dat_offset': hex(offset),
                                'top_left': [x, y], 'dimensions': [width, height],
                                'frame_count': count, 'geometry_layer': layer})
        report['tables'].append({'table': table, 'dat_sha256': dat_sha,
                                 'palette_offset': hex(pal), 'sprites': sprite_rows,
                                 'flippers': len(sprites), 'frames': frames,
                                 'compared_pixels': compared, 'transparent_pixels': transparent,
                                 'original_index_sha256': digest.hexdigest(), 'differences': 0})
        print(table, 'PASS', frames, 'frames', compared, 'pixels')
    assert sum(t['compared_pixels'] for t in report['tables']) == 304448
    report['ball_display'] = verify_ball_display(image, corpus)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')


def verify_ball_display(image, corpus):
    cases = []
    for x, y, px, py, rest in [
        (287, 571, 287, 571, 5), (287.75, 571.25, 286, 570, 5),
        (287.75, 571.25, 286, 570, 0), (100.75, 230.25, 99.25, 228.75, 2),
        (6.75, 6.25, 6, 6, 5), (0, 0, 0, 0, 5), (-1.25, -3.75, -1, -3, 5),
    ]:
        u = machine(image)
        put(u, 0x454b68, 0x1000000)
        u.mem_write(0x1000000, struct.pack('<4i', *[int(v * 65536) for v in (x, y, px, py)]))
        put(u, 0x46c744, rest)
        u.reg_write(UC_X86_REG_EBX, 0)
        u.reg_write(UC_X86_REG_ESP, 0x2008000)
        u.emu_start(0x40871c, 0x40879d, count=1000)
        assert u.reg_read(UC_X86_REG_EIP) == 0x40879d
        got = struct.unpack('<2h', u.mem_read(0x1000010, 4))
        expected = (math.trunc(px * (1 - rest / 5) + x * rest / 5 - 7),
                    math.trunc(py * (1 - rest / 5) + y * rest / 5 - 7))
        assert got == expected, (got, expected)
        cases.append({'current': [x, y], 'previous': [px, py], 'residual_ms': rest,
                      'original_render_xy': list(got)})
    main = (corpus / 'MAIN.DAT').read_bytes()
    assert len(main) == 0xf028
    assert set(main[0x88a4:0x88a4 + 240]) == {0, 255}
    constants = {hex(a): struct.unpack_from('<d', image, a - 0x400000)[0]
                 for a in (0x454273, 0x45427b, 0x454283)}
    assert list(constants.values()) == [0.2, 1 / 65536, -7.0]
    print('Retail ball anchor PASS', len(cases), 'original x87 cases')
    return {
        'status': 'VERIFIED original Retail x87 interpolation in seven cases',
        'routine': '0x40871c..0x40879d', 'object_table': '0x454b68',
        'residual_ms': 'int32[0x46c744]', 'constants': constants,
        'formula': 'trunc((previous*(1-residual_ms/5)+current*residual_ms/5)/65536-7)',
        'fields': {'x': '+0x00 i32', 'y': '+0x04 i32', 'previous_x': '+0x08 i32',
                   'previous_y': '+0x0c i32', 'render_x': '+0x10 i16', 'render_y': '+0x12 i16'},
        'bounds': '0<=renderX<304, 0<=renderY<600 (40b899..40b8c1)',
        'layering': {'order': 'Flippers before ball pass (40561e..40564e)',
                     'balls': 'Ascending renderY; greater Y drawn last (408889..4088da,4056a4..4056ce)',
                     'geometry': 'No geometry-layer sort; object+0x54 foreground preservation bitmap (40b88c..40b975)'},
        'main_dat_sha256': hashlib.sha256(main).hexdigest(),
        'sprite': {'dimensions': [16, 15], 'offset': '0x3da4+(renderY//8)*256',
                   'evidence': '0x40b990..0x40b9cc', 'palette': 'active table palette indices'},
        'outline': {'offset': '0x88a4', 'length': 240, 'values': [0, 255],
                    'evidence': '0x40b86f..0x40b89e',
                    'native_reuse': 'load_windows_ball_mask/load_windows_ball_pixels/windows_ball_occlusion'},
        'cases': cases, 'differences': 0,
    }


if __name__ == '__main__':
    main()
