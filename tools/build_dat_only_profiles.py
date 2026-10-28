#!/usr/bin/env python3
"""Hash native-created engine states plus user DATs; never reads an EXE."""
import argparse
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def put_words(data, entries):
    for offset, value in entries:
        struct.pack_into('<I', data, offset, value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native', type=Path, default=ROOT / 'build/native/slamnative-data')
    args = parser.parse_args()
    work = ROOT / 'build/dat-only-profiles'
    work.mkdir(exist_ok=True)
    dump = work / 'native-engine-data.bin'
    subprocess.run([args.native, dump], check=True)
    engine = dump.read_bytes()
    assert len(engine) == 0x100000
    dat = ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT'
    for table in ['pirate', 'space', 'demon']:
        recipe = json.loads((ROOT / f'analysis/import/{table}-retail-startup.json').read_text())
        image = bytearray(engine)
        files = {n: (dat / n).read_bytes() for n in [table.upper() + '.DAT', 'MAIN.DAT']}
        assert all(sha(data) == recipe['input_sha256'][name] for name, data in files.items())
        dest, start, size = recipe['canvas']
        image[dest:dest + size] = files[table.upper() + '.DAT'][start:start + size]
        start = recipe['main_offset']
        image[start:start + len(files['MAIN.DAT'])] = files['MAIN.DAT']
        put_words(image, recipe['image_words'])
        runtime = bytearray(0x10000)
        for i in range(600):
            struct.pack_into('<I', runtime, 0xc000 + i * 4, 320)
        put_words(runtime, recipe['runtime_words'])
        prefix = table + '-prepared/'
        files[prefix + 'human-image.bin'] = image
        files[prefix + 'human-runtime.bin'] = runtime
        if 'summary' in recipe:
            recipe['summary']['context_hashes']['human-image.bin'] = sha(image)
            recipe['summary']['context_hashes']['human-runtime.bin'] = sha(runtime)
            files[prefix + 'summary.json'] = (json.dumps(recipe['summary'], sort_keys=True, separators=(',', ':')) + '\n').encode()
        recipe['files_sha256'] = {name: sha(data) for name, data in files.items()}
        recipe['method'] = 'Native engine/math/table initialization with user DAT files; no executable input'
        (ROOT / f'analysis/import/{table}-dat-startup.json').write_text(json.dumps(recipe, indent=2) + '\n')
        if table == 'pirate':
            text = '#pragma once\nnamespace slam {\ninline constexpr const char* native_pirate_image_sha256 = "' + sha(image) + '";\n}\n'
            (ROOT / 'src/assets/native_data_profiles.h').write_text(text)
    print('Three DAT-only profiles generated from native constructors and user DATs; no EXE read')


if __name__ == '__main__':
    main()
