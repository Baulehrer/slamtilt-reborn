#!/usr/bin/env python3
"""Stage the cross build without running host ldd or mislabelling its architecture."""
import hashlib,json,re,shutil,subprocess,tarfile
from pathlib import Path
root=Path('/workspace'); work=root/'build/arm64-release'; stage=work/'slamtilt-reborn-linux-aarch64'
if stage.exists(): shutil.rmtree(stage)
for component in ['Runtime','FrontendRuntime']:
 subprocess.run(['cmake','--install',str(work/'native'),'--prefix',str(stage),'--component',component,'--strip'],check=True)
share=stage/'share/slamtilt'
for table in ['pirate','space','demon']:
 shutil.copyfile(root/f'analysis/import/{table}-retail-startup.json',share/f'{table}-retail-startup.json')
for notice in ['nlohmann-json-MIT.txt','ancient-BSD-2-Clause.txt']:
 shutil.copyfile(root/'LICENSES'/notice,stage/'LICENSES'/notice)
lib=stage/'lib'; lib.mkdir(exist_ok=True)
for name in ['libSDL3.so.0','libxmp.so.4']:
 shutil.copyfile(Path('/opt/arm64/lib')/name,lib/name)
for source,target in [('SDL3-3.4.18/LICENSE.txt','SDL3.txt'),('libxmp/docs/COPYING','libxmp.txt')]:
 shutil.copyfile(work/'sources'/source,stage/'LICENSES'/target)
starter=stage/'slamtilt-reborn'
starter.write_text('''#!/bin/sh
set -eu
here=$(CDPATH= cd -P "$(dirname "$(readlink -f -- "$0")")" && pwd)
export LD_LIBRARY_PATH="$here/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec "$here/bin/slamtilt" "$@"
''');starter.chmod(0o755);shutil.copy2(starter,stage/'slamtilt')
shutil.copyfile(root/'packaging/arm64/README.md',stage/'README-ARM64.md')
shutil.copyfile(root/'packaging/arm64/README.md',stage/'README.txt')
shutil.copytree(root/'packaging/batocera',stage/'batocera')
proof=[]; versions=set()
for binary in [*(stage/'bin').iterdir(),stage/'slamimport',*lib.iterdir()]:
 header=subprocess.check_output(['readelf','-h',str(binary)],text=True)
 if 'AArch64' not in header: raise RuntimeError(f'Wrong architecture: {binary}')
 proof.append(subprocess.check_output(['readelf','-h','-d',str(binary)],text=True))
 versions.update(re.findall(r'\b(?:GLIBCXX|GLIBC|CXXABI)_[0-9.]+',subprocess.check_output(['readelf','--version-info',str(binary)],text=True)))
files={str(p.relative_to(stage)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(stage.rglob('*')) if p.is_file()}
if any(Path(n).suffix.lower() in ['.dat','.exe','.bin','.adf'] for n in files): raise RuntimeError('Original asset in stage')
(stage/'frontend-bundle.json').write_text(json.dumps(dict(format=1,architecture='aarch64',original_assets_included=False,tables=['mean','pirate','space','demon'],runtime_requirements=sorted(versions),files=files),indent=2)+'\n')
(work/'elf-proof.txt').write_text('\n'.join(proof))
with tarfile.open(str(stage)+'.tar.gz','w:gz') as archive: archive.add(stage,arcname=stage.name)
