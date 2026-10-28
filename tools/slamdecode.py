#!/usr/bin/env python3
"""Bounded SLAM/StoneCracker decoder, derived from retail hunk0:0x8280.

Consulted Teemu Suutari's ancient StoneCracker generation-8 implementation
(BSD-2-Clause; see LICENSES/ancient-BSD-2-Clause.txt and docs/amiga-overlays.md).
Original assets are read locally and are never bundled. Output is bounded to
64 MiB by default. This implements the backward MSB LZ format, not 68k code.
"""
import argparse
from pathlib import Path
import struct


def decode(data: bytes, max_output: int = 64 * 1024 * 1024) -> bytes:
    if len(data) < 22 or data[:4] != b'SLAM':
        raise ValueError('not a SLAM container')
    marker, size, packed = struct.unpack_from('>III', data, 4)
    if marker != 0x50 or not 0 < size <= max_output:
        raise ValueError('unsupported SLAM marker or output length')
    end = 12 + packed
    if end < 16 or end + 6 > len(data):
        raise ValueError('truncated packed payload/trailer')
    mode, reservoir, available = struct.unpack_from('>HHH', data, end)
    if not 10 <= mode <= 14 or not 0 <= available <= 16:
        raise ValueError('invalid distance mode/bit count')
    cursor = end

    def bits(n):
        nonlocal cursor, reservoir, available
        value = 0
        for _ in range(n):
            if not available:
                cursor -= 2
                if cursor < 16:
                    raise ValueError('packed bitstream exhausted')
                reservoir = int.from_bytes(data[cursor:cursor + 2], 'big')
                available = 16
            value = (value << 1) | ((reservoir >> 15) & 1)
            reservoir = (reservoir << 1) & 0xffff
            available -= 1
        return value

    out = bytearray(size)
    pos = size
    while pos:
        literal = False
        if bits(1) == 0:
            literal, count = True, 1
        elif bits(1):
            count = 2 + bits(1)
        elif bits(1):
            count = 4 + bits(2)
        elif bits(1) == 0:
            count = 23 + bits(8)
            if count == 278:
                while True:
                    extra = bits(8)
                    count += extra
                    if count > pos:
                        raise ValueError('literal run exceeds remaining output')
                    if extra != 255:
                        break
        else:
            extra = bits(4)
            if extra < 15:
                count = 8 + extra
            else:
                literal, count = True, 14 + bits(5)
        if count > pos:
            raise ValueError('run exceeds remaining output')
        if literal:
            for _ in range(count):
                pos -= 1
                out[pos] = bits(8)
        else:
            if bits(1):
                distance = 545 + bits(mode)
            elif bits(1):
                distance = 1 + bits(5)
            else:
                distance = 33 + bits(9)
            if pos + distance - 1 >= size:
                raise ValueError(f'backreference outside decoded output: pos={pos} distance={distance} count={count} cursor={cursor} available={available}')
            for _ in range(count):
                pos -= 1
                out[pos] = out[pos + distance]
    return bytes(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = decode(args.input.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(result)
    print(f'{args.input}: {len(result)} decoded bytes -> {args.output}')


if __name__ == '__main__':
    main()
