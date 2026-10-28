#!/usr/bin/env python3
"""Hash only extracted Slam Tilt table assets and game EXEs; no extraction/RE."""
import argparse
import hashlib
import json
from pathlib import Path

NAMES = ('MAIN.DAT', 'MEAN.DAT', 'PIRATE.DAT', 'SPACE.DAT', 'DEMON.DAT')

def record(path):
    data = path.read_bytes()
    result = {'path': path.as_posix(), 'size': len(data),
              'sha256': hashlib.sha256(data).hexdigest()}
    if path.name.upper() == 'SLAMTILT.EXE':
        if b'BEGTEXT' in data[:1024] and b'DDRAW.dll' in data:
            result['role'] = 'game_executable'
            result['role_evidence'] = ['PE BEGTEXT section', 'DDRAW.dll import string']
        elif b'%sSETUP.LOG' in data and b'AppName=SlamTilt' in data:
            result['role'] = 'installer_container'
            result['role_evidence'] = ['%sSETUP.LOG string', 'AppName=SlamTilt string']
        else:
            result['role'] = 'unclassified'
    return result

def families(records):
    groups = {}
    for item in records:
        groups.setdefault(item['sha256'], []).append(item['path'])
    return [{'sha256': key, 'paths': value} for key, value in sorted(groups.items())]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('build/corpus/win95'))
    parser.add_argument('--output', type=Path, default=Path('analysis/corpus-table-data-families.json'))
    args = parser.parse_args()
    paths = sorted(p for p in args.root.rglob('*') if p.is_file())
    tables = {}
    for name in NAMES:
        files = [record(p) for p in paths if p.name.upper() == name]
        groups = families(files)
        tables[name] = {'files': files, 'families': groups,
                        'file_count': len(files), 'family_count': len(groups),
                        'all_available_identical': len(groups) == 1}
    exes = [record(p) for p in paths if p.name.upper() == 'SLAMTILT.EXE']
    report = {
        'schema': 1, 'scope': 'Extracted Windows original Slam Tilt assets only; byte identity, not runtime equivalence.',
        'method': 'Fresh SHA256 of all files matching five exact basenames and SLAMTILT.EXE; stable sorted paths.',
        'tables': tables, 'executables': {'files': exes, 'families': families(exes),
                        'game_families': families([e for e in exes if e['role'] == 'game_executable'])},
        'ranked_actions': [
            {'rank': 1, 'action': 'Reuse existing DAT parsers, geometry and sprite decoding across every identical regional table family.',
             'benefit': 'No per-release asset profiles or repeated format RE needed.'},
            {'rank': 2, 'action': 'Use the smallest verified full EXE family as the Pirate/Space/Demon runtime oracle; map table callback addresses once per EXE hash.',
             'benefit': 'Identical EXE copies share exact code/global addresses; different EXE hashes still require bounded matching.'},
            {'rank': 3, 'action': 'Keep demo and retail rule/physics trace provenance separate even when DAT matches.',
             'benefit': 'Known demo-versus-retail Drag Race instruction difference lies in EXE, not DAT.'}
        ],
        'limits': ['Only already extracted files are covered; missing German table DAT is not inferred.',
                   'Identical DAT does not prove identical executable rules or physics.',
                   'Different EXE hash is not itself evidence of gameplay changes; German SLAMTILT.EXE is an installer container, not a fifth game build.',
                   'Resurrection is excluded because it is a separate game.']
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    for name, info in tables.items():
        print(f"{name}: {info['file_count']} files, {info['family_count']} SHA256 families")
    print(f"SLAMTILT.EXE: {len(exes)} files, {len(report['executables']['families'])} families")

if __name__ == '__main__':
    main()
