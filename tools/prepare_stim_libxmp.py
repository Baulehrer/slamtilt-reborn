#!/usr/bin/env python3
"""Create a verified private libxmp source tree with Slam Tilt STIM fixes."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'patches/libxmp-stim-rate.patch'
EXPECTED = {
    'common.h': '35bacd82022233610a08a1f5e27e71aa609d2d2b10fdd2030e74ceb19a29d57a',
    'control.c': '20463b6707b070f2c82e434b34051ad2c5afca247d5e0ebb9806d0a0f860458f',
    'effects.c': '232b96cca9f830ba73cfeb64709c1738ec7ca69e6d21dffd558d419126abdb06',
    'loaders/stim_load.c': '4590c5a0875e0ead568a61cb801d1fa08dc0682ffbe45dab29276f5bdfb1aba3',
    'mix_all.c': '8f0a03008f35852029d586029ac308aefd8089c5bcb2cb67d193320e33a2ef10',
    'mixer.h': 'abfa0e10446991de6eba884bcd3d23e737e43a8d93adbc3c60c6224c3f0ffeec',
    'mixer.c': '72ff837d252050bb8cc93471ff955d17d109801c4d30e70d7a896f7bdd6553ad',
    'period.c': '23cc96ef90974a6fffb213f6b5412257cca80ade143ad568157ee580a66c3f75',
    'player.c': '5844db1c5b764e6d8fb1185c73300f9a3713784b4c6260829fda0382f1e6e24e',
    'player.h': '043997a0e9efb46c11eabc9f3abf1a136e565132280ba856f337a43f3bb772b7',
    'read_event.c': 'f0ea35e492a33fc415a737ee7e6a0bea28735e0efc1f4fc68f94fe6c240c184c',
}
EXPECTED_ROOT = {
    'include/xmp.h': 'd88634f540674b85cb2f985a706fcfe25cff7318b1403fe4e6c81622ae91fdaa',
    'libxmp.map': '26a5c91fe90c4978dd893f55ad77588a66a322adb341625879dafce82a2045c2',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--patch', type=Path, default=PATCH, help='Pinned patch to apply')
    a = p.parse_args()
    source, output = a.source.resolve(), a.output.resolve()
    if source == output or source in output.parents or output in source.parents:
        raise ValueError('Source and output must be separate trees')
    for name, expected in EXPECTED.items():
        if sha(source/'src'/name) != expected:
            raise ValueError(f'Unexpected libxmp source: {name}')
    for name, expected in EXPECTED_ROOT.items():
        if sha(source/name) != expected:
            raise ValueError(f'Unexpected libxmp source: {name}')
    marker = output/'.slamtilt-stim-patch.json'
    patch = a.patch.resolve()
    manifest = {'patch_sha256': sha(patch), 'original_files': EXPECTED, 'original_root_files': EXPECTED_ROOT}
    if output.exists():
        if not marker.is_file() or json.loads(marker.read_text()) != manifest:
            raise ValueError(f'Refusing to overwrite unrecognized tree: {output}')
        subprocess.run(['patch','--dry-run','--reverse','--batch','-p1','-i',str(patch)],cwd=output,check=True,stdout=subprocess.DEVNULL)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, output, ignore=shutil.ignore_patterns('.git'))
    subprocess.run(['patch','--batch','-p1','-i',str(patch)],cwd=output,check=True)
    marker.write_text(json.dumps(manifest,indent=2)+'\n')


if __name__ == '__main__':
    main()
