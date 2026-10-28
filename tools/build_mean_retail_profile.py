#!/usr/bin/env python3
"""Reproduce data-only Retail Mean import metadata; original bytes stay in build/."""
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    spec = importlib.util.spec_from_file_location('mean_reference', ROOT / 'tools/slamimport_reference.py')
    reference = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reference)
    mapping = json.loads((ROOT / 'analysis/mean-retail-readset.json').read_text())
    recipe = json.loads((ROOT / 'analysis/import/mean-demo-startup.json').read_text())
    recipe.update(build_sha256=mapping['source_build_sha256'],
                  source_image_size=mapping['source_image_size'],
                  data_copies=mapping['copies'], pointer_fixups=mapping['pointer_fixups'])
    recipe['provenance']['retail'] = ('Byte-verified Retail data ranges including the complete math lookup island, explicit pointer normalization '
                                     'to native Mean data ABI; no original code or headers copied. '
                                     'Existing verified native startup scalar recipe; not Retail startup emulation.')
    game = ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    exe = (game / 'SLAMTILT.EXE').read_bytes()
    assert hashlib.sha256(exe).hexdigest() == recipe['build_sha256']
    source = reference.mapped_image(exe, recipe['source_image_size'])
    image = bytearray(recipe['image_size'])
    for start, dest, size in recipe['data_copies']:
        image[dest:dest + size] = source[start:start + size]
    for offset, old, new in recipe['pointer_fixups']:
        assert struct.unpack_from('<I', image, offset)[0] == old
        struct.pack_into('<I', image, offset, new)
    assert hashlib.sha256(image).hexdigest() == mapping['sparse_image_sha256']
    begin, size = recipe['lookup']
    lookup = image[begin:begin + size]
    mini = reference.apply_words(image + bytearray(0x100000 - len(image)), recipe['minigame_image'])
    runtime = reference.apply_words(bytearray(0x10000), recipe['minigame_runtime'])
    runtime[0x6000:0x6000 + len(lookup)] = lookup
    files = {'MEAN.DAT': (game / 'DAT/MEAN.DAT').read_bytes(),
             'MAIN.DAT': (game / 'DAT/MAIN.DAT').read_bytes(),
             'mean-prepared/pe-data.bin': image,
             'mean-prepared/engine-globals.bin': reference.apply_words(bytearray(160), recipe['engine_globals']),
             'mean-prepared/flipper-state.bin': reference.apply_words(bytearray(108), recipe['flipper_state']),
             'mean-prepared/lookup.bin': lookup,
             'mean-minigame-prepared/image.bin': mini,
             'mean-minigame-prepared/runtime.bin': runtime}
    (ROOT / 'analysis/import/mean-retail-startup.json').write_text(json.dumps(recipe, indent=2) + '\n')
    (ROOT / 'packaging/mean-retail-data.sha256').write_text(''.join(
        hashlib.sha256(data).hexdigest() + '  ' + name + '\n' for name, data in files.items()))
    print(f"Retail Mean recipe/profile: {len(recipe['data_copies'])} data ranges,124 pointer fixups,8 files; no embedded original assets")


if __name__ == '__main__':
    main()
