#!/usr/bin/env python3
"""Export an original Amiga table .Raw playfield as a PPM image."""
import argparse
from pathlib import Path
import struct
from slamdecode import decode


def playfield(data):
    if data[:4] == b'SLAM':
        data = decode(data)
    if len(data) < 4:
        raise ValueError('missing section pointer')
    section = struct.unpack_from('>I', data)[0]
    if section + 24 > len(data):
        raise ValueError('section outside file')
    pixels, palette, *_ = struct.unpack_from('>6I', data, section)
    start, colors = section + pixels, section + palette
    if pixels != 24 or start + 192000 > len(data) or colors + 1024 > len(data):
        raise ValueError('unsupported/truncated playfield section')
    pal = data[colors:colors + 1024]
    if any(pal[i] for i in range(0, 1024, 4)):
        raise ValueError('invalid palette reserved bytes')
    rgb = bytearray()
    for y in range(600):
        row = start + y * 320
        for x in range(320):
            index = sum(((data[row + plane * 40 + x // 8] >> (7 - x % 8)) & 1) << plane for plane in range(8))
            rgb.extend(pal[index * 4 + 1:index * 4 + 4])
    return bytes(rgb)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(b'P6\n320 600\n255\n' + playfield(args.input.read_bytes()))
    print(f'{args.output}: 320x600 original Amiga playfield')


if __name__ == '__main__':
    main()
