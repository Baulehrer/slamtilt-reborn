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
    'mix_all.c': '8f0a03008f35852029d586029ac308aefd8089c5bcb2cb67d193320e33a2ef10',
    'mixer.h': 'abfa0e10446991de6eba884bcd3d23e737e43a8d93adbc3c60c6224c3f0ffeec',
    'mixer.c': '72ff837d252050bb8cc93471ff955d17d109801c4d30e70d7a896f7bdd6553ad',
    'period.c': '23cc96ef90974a6fffb213f6b5412257cca80ade143ad568157ee580a66c3f75',
    'player.c': '5844db1c5b764e6d8fb1185c73300f9a3713784b4c6260829fda0382f1e6e24e',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    source, output = a.source.resolve(), a.output.resolve()
    if source == output or source in output.parents or output in source.parents:
        raise ValueError('Source and output must be separate trees')
    for name, expected in EXPECTED.items():
        if sha(source/'src'/name) != expected:
            raise ValueError(f'Unexpected libxmp source: {name}')
    marker = output/'.slamtilt-stim-patch.json'
    manifest = {'patch_sha256': sha(PATCH), 'original_files': EXPECTED}
    if output.exists():
        if not marker.is_file() or json.loads(marker.read_text()) != manifest:
            raise ValueError(f'Refusing to overwrite unrecognized tree: {output}')
        subprocess.run(['patch','--dry-run','--reverse','--batch','-p1','-i',str(PATCH)],cwd=output,check=True,stdout=subprocess.DEVNULL)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, output, ignore=shutil.ignore_patterns('.git'))
    subprocess.run(['patch','--batch','-p1','-i',str(PATCH)],cwd=output,check=True)
    marker.write_text(json.dumps(manifest,indent=2)+'\n')


if __name__ == '__main__':
    main()
