#!/usr/bin/env python3
"""Inventory already-built local release artifacts; never publishes anything."""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('release', type=Path)
args = parser.parse_args()
assets = args.release / 'assets'
required = ['Slamtilt-Reborn-windows-x86_64-setup.exe',
            'Slamtilt-Reborn-windows-x86_64-portable.zip',
            'Slamtilt-Reborn-linux-x86_64.AppImage',
            'Slamtilt-Reborn-linux-arm64-preview.tar.gz',
            'Slamtilt-Reborn.html']
files = []
for name in required:
    path = assets / name
    if not path.is_file() or not path.stat().st_size:
        raise SystemExit('Missing artifact: ' + str(path))
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    files.append({'name': name, 'bytes': path.stat().st_size, 'sha256': digest})
manifest = {
    'project': 'Slamtilt - Reborn', 'version': args.release.name,
    'publication': 'LOCAL_ONLY', 'original_game_data_in_runtime': False,
    'windows_signed': False, 'arm64_physical_hardware_verified': False,
    'assets': files,
}
proofs = [json.loads((args.release / 'verification' / name).read_text())
          for name in ('browser-pc.json', 'browser-adf.json')]
html_sha = next(f['sha256'] for f in files if f['name'].endswith('.html'))
for proof in proofs:
    if (not proof.get('passed') or proof.get('html_sha256') != html_sha or
            set(proof.get('selected_tables', [])) != {'mean', 'pirate', 'space', 'demon'}):
        raise SystemExit('Browser proof is missing, failed, or belongs to another artifact')
manifest.update({'browser_preview': True, 'browser_requires': 'WebAssembly JSPI + native Wasm exceptions',
                 'browser_verified': 'Chromium' + proofs[0]['browser']['version'],
                 'browser_acceptance': {proof['asset_source']: len(proof['checks']) for proof in proofs},
                 'windows_advanced_gpu_filters': False})
digests = {f['name']: f['sha256'] for f in files}
notice_proof = json.loads((args.release / 'verification/packaging-notices.json').read_text())
if notice_proof['exact_repacked_installer_smoke_exit_code'] != 0:
    raise SystemExit('Windows installer acceptance failed')
for name, digest in notice_proof['assets'].items():
    if digests.get(name) != digest:
        raise SystemExit('Native package differs from acceptance proof: ' + name)
appimage_proof = json.loads((args.release / 'verification/appimage.json').read_text())
if (appimage_proof['status'] != 'PASS' or appimage_proof['appimage_sha256'] !=
        digests['Slamtilt-Reborn-linux-x86_64.AppImage']):
    raise SystemExit('AppImage differs from acceptance proof')
(assets / 'SHA256SUMS').write_text(''.join(f"{f['sha256']}  {f['name']}\n" for f in files))
(args.release / 'release.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('Sealed', len(files), 'local artifacts:', args.release)
