#!/usr/bin/env python3
"""Extract proven Windows Mean collision bitplanes; outputs stay outside source control."""
import argparse, hashlib, json
from pathlib import Path
WIDTH, STRIDE, PLANE_STRIDE, OFFSET = 320, 40, 0x6040, 0x9ba36

def sample(data, x, y, plane=0):
    if not 0 <= x < WIDTH or not 0 <= y < 600 or not 0 <= plane < 4:
        raise ValueError('coordinate/plane outside validated playfield bounds')
    pos = OFFSET + plane * PLANE_STRIDE + y * STRIDE + (x >> 3)
    if pos >= len(data):
        raise ValueError('truncated collision bitmap')
    return bool(data[pos] & (0x80 >> (x & 7)))

def extract(source, output):
    data = Path(source).read_bytes()
    if len(data) < OFFSET + 4 * PLANE_STRIDE:
        raise ValueError('truncated Mean DAT')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    masks = []
    for plane in range(4):
        pixels = bytes(255 if sample(data, x, y, plane) else 0 for y in range(600) for x in range(WIDTH))
        name = f'mean-collision-plane-{plane}.pgm'
        (output / name).write_bytes(b'P5\n320 600\n255\n' + pixels)
        masks.append({'plane': plane, 'offset': hex(OFFSET + plane * PLANE_STRIDE), 'occupied_pixels': pixels.count(255), 'pgm': name})
    # Debug composite against the proven indexed playfield, red = collision plane0.
    palette, image = 0x1590c8, 0x1594c8
    if image + WIDTH * 600 <= len(data):
        rgb = bytearray()
        for y in range(600):
            for x in range(WIDTH):
                index = data[image + y * WIDTH + x]
                color = data[palette + index * 4 + 1:palette + index * 4 + 4]
                rgb.extend(((color[0] + 255) // 2, color[1] // 2, color[2] // 2) if sample(data, x, y) else color)
        (output / 'mean-collision-overlay.ppm').write_bytes(b'P6\n320 600\n255\n' + rgb)
    result = {'source_sha256': hashlib.sha256(data).hexdigest(), 'width': WIDTH, 'validated_height': 600, 'stored_plane_stride': PLANE_STRIDE, 'stored_rows': PLANE_STRIDE // STRIDE, 'bit_order': 'MSB first', 'planes': masks, 'note': 'Plane0 occupancy consumed by collision; extra planes feed event/state masks. No invented line geometry.'}
    (output / 'mean-collision.json').write_text(json.dumps(result, indent=2) + '\n')
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dat', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    print(json.dumps(extract(args.dat, args.output), indent=2))
