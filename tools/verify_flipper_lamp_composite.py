#!/usr/bin/env python3
"""All Pirate flipper frames plus whole lamp canvases against original blits.

Reuses the persisted lamp initializer harness. Original data stays below build/.
The comparison uses pristine-source alpha and current-runtime DAT RGB/masks.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import struct
import subprocess

import pefile

from validate_table_lamps_original import (
    ROOT, SHA, DAT_BASE, CANVAS, PALETTES, prepare, machine, bind_renderer,
    run, put, get,
)


def word(u, address, value):
    u.mem_write(address, struct.pack('<H', value & 0xffff))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, default=ROOT / (
        'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/'
        'Game Files/SLAMTILT/SLAMTILT.EXE'))
    parser.add_argument('--work', type=Path,
                        default=ROOT / 'build/oracle/pirate-flipper-lamps')
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'analysis/pirate-flipper-lamps.json')
    parser.add_argument('--native', type=Path,
                        help='Optional compiled table_flipper_composite_probe')
    args = parser.parse_args()
    work = args.work.resolve()
    if not work.is_relative_to(ROOT / 'build'):
        parser.error('--work must be under build/: original data')
    work.mkdir(parents=True, exist_ok=True)
    raw = args.exe.read_bytes()
    assert digest(raw) == SHA
    image = bytearray(pefile.PE(data=raw).get_memory_mapped_image())
    image.extend(bytes(0x100000 - len(image)))
    dat = (args.exe.parent / 'DAT/PIRATE.DAT').read_bytes()
    profile = json.loads((ROOT / 'analysis/table-profiles.json').read_text())['tables']['pirate']
    assert digest(dat) == profile['dat_sha256']
    initial, manifest = prepare(bytes(image), dat, profile)
    palette = PALETTES['pirate']
    foreground = profile['layers'][0]['render_offset']
    descriptors = (0x4658cc, 0x4658f0, 0x465914)
    cases, problems = [], []
    native_rgb_differences = native_alpha_differences = native_pixels = 0
    rng = random.Random(0x40b518)
    patterns = [([2] * 53), ([1] * 53),
                [rng.choice((1, 2)) for _ in range(53)],
                [rng.choice((1, 2)) for _ in range(53)]]
    for pattern_id, commands in enumerate(patterns):
        u = machine(initial, dat)  # No hooks or callee replacements.
        bind_renderer(u, dat, palette)
        run(u, 0x404f09, stop=0x404f62)
        run(u, 0x405057, stop=0x405079)
        # Original startup405153..40517d preprocesses each flipper through40b71c.
        # It replaces transparent/foreground pixels with table background bytes.
        put(u, 0x46c490, DAT_BASE + palette + 1024)
        for descriptor in descriptors:
            run(u, 0x40b71c, descriptor)
        for address in (0x46c6cc, 0x46c63c, 0x454d88):
            put(u, address, 0)
        u.mem_write(int(manifest['status_commands'], 16),
                    bytes(value for kind in commands for value in (kind, 0, 0, 0)))
        run(u, 0x408da8)
        background = bytes(u.mem_read(CANVAS, 320 * 600))
        (work / f'pattern-{pattern_id}-image.bin').write_bytes(
            bytes(u.mem_read(0x400000, 0x100000)))
        (work / f'pattern-{pattern_id}-dat.bin').write_bytes(
            bytes(u.mem_read(DAT_BASE, len(dat))))
        native_directory = work / f'pattern-{pattern_id}-native'
        if args.native:
            native_directory.mkdir(parents=True, exist_ok=True)
            subprocess.run([
                str(args.native.resolve()),
                str((args.exe.parent / 'DAT/PIRATE.DAT').resolve()),
                str(work / f'pattern-{pattern_id}-image.bin'),
                str(work / f'pattern-{pattern_id}-dat.bin'),
                str(native_directory),
            ], cwd=ROOT, check=True)
        if args.native:
            native_canvas=(native_directory/'lamp-canvas.rgba').read_bytes()
            original_rgb=bytes(v for index in background for v in dat[palette+index*4+1:palette+index*4+4])
            canvas_rgb=bytes(v for i in range(320*600)for v in native_canvas[i*4:i*4+3])
            differences=sum(original_rgb[i:i+3]!=canvas_rgb[i:i+3]for i in range(0,len(original_rgb),3))
            print('Lamp canvas pattern',pattern_id,'RGB pixel differences',differences,flush=True)
            if differences:
                points=[(i//3%320,i//3//320)for i in range(0,len(original_rgb),3)if original_rgb[i:i+3]!=canvas_rgb[i:i+3]]
                print('First canvas differences:',points[:12],flush=True)
            assert not differences,('whole lamp canvas',pattern_id,differences)
        for side, descriptor in enumerate(descriptors):
            width, height, x, y, count = struct.unpack(
                '<5H', u.mem_read(descriptor + 0xc, 10))
            source, mask_pointer = get(u, descriptor + 0x1c), get(u, descriptor + 0x20)
            size = width * height
            mask = bytes(u.mem_read(mask_pointer, size))
            offset = source - DAT_BASE
            alpha = []
            for frame in range(count):
                source_before = bytes(u.mem_read(source + frame * size, size))
                pristine = dat[offset + frame * size:offset + (frame + 1) * size]
                alpha = [index > 1 and not (
                    dat[foreground + (y + i // width) * 40 + (x + i % width) // 8] &
                    (128 >> ((x + i % width) & 7)))
                    for i, index in enumerate(pristine)]
                native_rgba = None
                if args.native:
                    native_rgba = (native_directory /
                                   f'frame{side}-{frame}.rgba').read_bytes()
                    assert len(native_rgba) == size * 4
                u.mem_write(CANVAS, background)
                word(u, descriptor + 0x16, 0xffff)  # Cache WORD, not count WORD+14.
                run(u, 0x40b518, descriptor, frame * 1024)
                actual = bytes(u.mem_read(CANVAS, 320 * 600))
                opaque_differences = transparent_differences = rule_differences = 0
                opaque_source_changes = index_differences = 0
                native_case_rgb = native_case_alpha = 0
                composite = bytearray(background)
                for i in range(size):
                    position = (y + i // width) * 320 + x + i % width
                    expected_index = source_before[i] & ~mask[i]
                    rule_differences += actual[position] != expected_index
                    if alpha[i]:
                        opaque_source_changes += source_before[i] != pristine[i]
                        composite[position] = expected_index
                    index_differences += actual[position] != composite[position]
                    original_rgb = dat[palette + actual[position] * 4 + 1:
                                       palette + actual[position] * 4 + 4]
                    native_rgb = dat[palette + composite[position] * 4 + 1:
                                     palette + composite[position] * 4 + 4]
                    if original_rgb != native_rgb:
                        if alpha[i]:
                            opaque_differences += 1
                        else:
                            transparent_differences += 1
                    if native_rgba is not None:
                        native_case_alpha += native_rgba[i * 4 + 3] != (
                            255 if alpha[i] else 0)
                        actual_native_rgb = (
                            native_rgba[i * 4:i * 4 + 3] if alpha[i] else
                            dat[palette + background[position] * 4 + 1:
                                palette + background[position] * 4 + 4])
                        native_case_rgb += actual_native_rgb != original_rgb
                assert rule_differences == 0
                assert opaque_source_changes == 0
                unchanged = bytes(u.mem_read(mask_pointer, size)) == mask
                assert unchanged
                row = dict(pattern=pattern_id, side=side,
                           descriptor=hex(descriptor), frame=frame,
                           anchor=[x, y], dimensions=[width, height],
                           source=hex(source + frame * size), mask=hex(mask_pointer),
                           mask_frame_offset=0, mask_sha256=digest(mask),
                           mask_nonzero_bytes=sum(v != 0 for v in mask),
                           source_and_not_mask_differences=rule_differences,
                           opaque_source_preprocessing_changes=opaque_source_changes,
                           opaque_rgb_differences=opaque_differences,
                           transparent_rgb_differences=transparent_differences,
                           composite_index_differences=index_differences,
                           original_canvas_sha256=digest(actual),
                           native_composite_sha256=digest(composite))
                if native_rgba is not None:
                    row.update(native_rgba_sha256=digest(native_rgba),
                               native_rgb_differences=native_case_rgb,
                               native_alpha_differences=native_case_alpha)
                    native_rgb_differences += native_case_rgb
                    native_alpha_differences += native_case_alpha
                    native_pixels += size
                cases.append(row)
                if opaque_differences or transparent_differences:
                    problems.append(row)
    report = dict(schema=1, build_sha256=SHA,
                  rule='currentDAT[descriptor+1c + frame*width*height+i] & ~image[descriptor+20+i]',
                  original='40b518..40b61b; EDI initialized40b526, source offset40b5a8..40b5c7, pixelAND40b5e1..40b5f3',
                  mask_frame_indexed=False, frame_source_indexed=True,
                  frame_cache='WORD descriptor+16; WORD+14 is frame count, not cache',
                  startup_preprocessing='Original40b71c for three flippers, as405153..40517d; replaces transparent/foreground pixels with background',
                  alpha='Pristine DAT index>1 and no original foreground bit; unchanged by lamp mask palette-bit changes',
                  lamp_patterns='all off, all on, two seeded random1/2 command patterns; original408da8 with parent links retained',
                  frames=len(cases), compared_pixels=sum(r['dimensions'][0] * r['dimensions'][1] for r in cases),
                  service_stubs=[], cases=cases, alpha_problems=problems,
                  prepared_context_directory=str(work.relative_to(ROOT)),
                  native_implementation_executed=bool(args.native),
                  scope='Actual original blits vs independent formula/alpha reference and optional compiled native compose probe. RGB comparison is authoritative; transparent equal-color palette aliases may differ in index.')
    if args.native:
        report['lamp_canvas_result'] = dict(frames=len(patterns),compared_pixels=len(patterns)*320*600,rgb_differences=0,status='PASS')
        report['native_result'] = dict(
            probe=str(args.native.resolve()), compared_pixels=native_pixels,
            rgb_differences=native_rgb_differences,
            alpha_differences=native_alpha_differences,
            status='PASS' if not (native_rgb_differences or
                                  native_alpha_differences) else 'FAIL')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('Original mask offset PASS:', len(cases), 'frames; alpha problems:', len(problems))
    if problems:
        print('First alpha problem:', json.dumps(problems[0]))
    if args.native:
        print('Native compose:', native_pixels, 'pixels;',
              native_rgb_differences, 'RGB differences;',
              native_alpha_differences, 'alpha differences')
        assert not (native_rgb_differences or native_alpha_differences)


if __name__ == '__main__':
    main()
