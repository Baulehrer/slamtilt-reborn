#!/usr/bin/env python3
"""Prepare the supported Windows Mean Demo for native play (Python stdlib only)."""
import argparse
import hashlib
import json
import struct
import tempfile
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def metadata():
    root = Path(__file__).resolve().parent
    if (root / 'share/slamtilt/mean-demo-startup.json').is_file():
        return root / 'share/slamtilt/mean-demo-startup.json', root / 'share/slamtilt/mean-data.sha256'
    return root.parent / 'analysis/import/mean-demo-startup.json', root.parent / 'packaging/mean-data.sha256'


def mapped_image(exe, size):
    """Map PE32 sections; Watcom .bss has raw size but raw pointer zero."""
    def u16(offset):
        return struct.unpack_from('<H', exe, offset)[0]

    def u32(offset):
        return struct.unpack_from('<I', exe, offset)[0]

    if exe[:2] != b'MZ':
        raise ValueError('Missing DOS header')
    pe = u32(0x3c)
    if exe[pe:pe + 4] != b'PE\0\0' or u16(pe + 4) != 0x14c:
        raise ValueError('Expected x86 PE executable')
    optional = pe + 24
    if u16(optional) != 0x10b or u32(optional + 28) != 0x400000:
        raise ValueError('Unsupported PE32 image base')
    image = bytearray(size)
    headers = u32(optional + 60)
    if headers > min(size, len(exe)):
        raise ValueError('Invalid PE headers')
    image[:headers] = exe[:headers]
    sections = optional + u16(pe + 20)
    for index in range(u16(pe + 6)):
        section = sections + index * 40
        va, length, source = u32(section + 12), u32(section + 16), u32(section + 20)
        # Uninitialized data occupies memory but has no on-disk bytes.
        if not source:
            continue
        if va + length > size or source + length > len(exe):
            raise ValueError('Invalid PE section range')
        image[va:va + length] = exe[source:source + length]
    return image


def apply_words(data, words):
    for offset, value in words:
        struct.pack_into('<I', data, offset, value)
    return data


def prepare(exe_path, dat_dir, destination):
    recipe_path, hashes_path = metadata()
    recipe = json.loads(recipe_path.read_text())
    hashes = dict(line.split(None, 1)[::-1]
                  for line in hashes_path.read_text().splitlines())
    exe = exe_path.read_bytes()
    if sha(exe) != recipe['build_sha256']:
        raise ValueError('Unsupported SLAMTILT.EXE revision; supported Windows Mean Demo required')
    # Check both user assets before creating any output.
    files = {name: (dat_dir / name).read_bytes() for name in ('MEAN.DAT', 'MAIN.DAT')}
    for name, data in files.items():
        if sha(data) != hashes[name]:
            raise ValueError('Unsupported or corrupt ' + name)
    image = mapped_image(exe, recipe['image_size'])
    start, length = recipe['bss']
    if image[start:start + length] != bytes(length):
        raise ValueError('Uninitialized PE section was not cleared')
    start, length = recipe['lookup']
    lookup = image[start:start + length]
    mini = image + bytes(0x100000 - len(image))
    runtime = apply_words(bytearray(0x10000), recipe['minigame_runtime'])
    runtime[0x6000:0x6000 + len(lookup)] = lookup
    files.update({
        'mean-prepared/pe-data.bin': image,
        'mean-prepared/lookup.bin': lookup,
        'mean-prepared/engine-globals.bin': apply_words(bytearray(160), recipe['engine_globals']),
        'mean-prepared/flipper-state.bin': apply_words(bytearray(108), recipe['flipper_state']),
        'mean-minigame-prepared/image.bin': apply_words(mini, recipe['minigame_image']),
        'mean-minigame-prepared/runtime.bin': runtime,
    })
    for name, data in files.items():
        if sha(data) != hashes[name]:
            raise ValueError('Prepared profile mismatch: ' + name)
    destination = destination.absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError('Destination already exists: ' + str(destination))
    destination.parent.mkdir(parents=True, exist_ok=True)
    report = {'format': 1, 'table': 'Mean Machines', 'build_sha256': sha(exe),
              'files': hashes, 'method': 'PE section extraction + verified startup scalar recipe',
              'requires_wine_or_emulator': False}
    with tempfile.TemporaryDirectory(prefix='.mean-import-', dir=destination.parent) as tmp:
        stage = Path(tmp) / 'data'
        stage.mkdir()
        for name, data in files.items():
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        (stage / 'data.sha256').write_text(hashes_path.read_text())
        (stage / 'data.json').write_text(json.dumps(report, indent=2) + '\n')
        # Reserve exclusively: preserve existing directories, including empty ones.
        destination.mkdir()
        try:
            stage.replace(destination)
        except BaseException:
            destination.rmdir()
            raise
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('exe', type=Path, help='Supported original SLAMTILT.EXE')
    parser.add_argument('dat_dir', type=Path, help='Directory containing MEAN.DAT and MAIN.DAT')
    parser.add_argument('output', type=Path, help='New private data directory (must not exist)')
    args = parser.parse_args()
    try:
        report = prepare(args.exe, args.dat_dir, args.output)
    except (OSError, ValueError, KeyError, struct.error) as error:
        parser.exit(2, 'slamimport: ' + str(error) + '\n')
    print('Mean data ready: ' + str(args.output) + ' (' + str(len(report['files'])) + ' verified files)')


if __name__ == '__main__':
    main()
