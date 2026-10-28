#!/usr/bin/env python3
"""Wrap the tested relocatable asset-free runtime as an AppImage."""
import argparse,hashlib,json,os,shutil,subprocess,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,default=ROOT/'build/compat/releases/slamtilt-reborn-linux-x86_64-rc6');p.add_argument('--output',type=Path,required=True);a=p.parse_args();work=ROOT/'build/appimage-release';work.mkdir(exist_ok=True);tool=work/'appimagetool.AppImage'
if not tool.exists():
 r=json.load(urllib.request.urlopen('https://api.github.com/repos/AppImage/appimagetool/releases/latest'));asset=next(x for x in r['assets']if x['name']=='appimagetool-x86_64.AppImage');urllib.request.urlretrieve(asset['browser_download_url'],tool)
 if asset.get('digest'):assert 'sha256:'+hashlib.sha256(tool.read_bytes()).hexdigest()==asset['digest']
 (work/'tool-source.json').write_text(json.dumps({'url':asset['browser_download_url'],'sha256':hashlib.sha256(tool.read_bytes()).hexdigest()},indent=2)+'\n')
tool.chmod(0o755);app=work/'Slamtilt-Reborn.AppDir'
if app.exists():shutil.rmtree(app)
app.mkdir();shutil.copytree(a.runtime,app/'usr',symlinks=True);
for notice in ('nlohmann-json-MIT.txt','ancient-BSD-2-Clause.txt'):shutil.copyfile(ROOT/'LICENSES'/notice,app/'usr/LICENSES'/notice)
shutil.copyfile(ROOT/'packaging/linux/reborn.svg',app/'slamtilt-reborn.svg');(app/'.DirIcon').symlink_to('slamtilt-reborn.svg')
(app/'AppRun').write_text('#!/bin/sh\nset -eu\nAPPDIR=${APPDIR:-$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)}\nexport LD_LIBRARY_PATH="$APPDIR/usr/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"\nexec "$APPDIR/usr/bin/slamtilt" "$@"\n');(app/'AppRun').chmod(0o755)
(app/'slamtilt-reborn.desktop').write_text('[Desktop Entry]\nType=Application\nName=Slamtilt - Reborn\nComment=Four classic pinball tables, reborn\nExec=AppRun\nIcon=slamtilt-reborn\nCategories=Game;ArcadeGame;\nTerminal=false\n')
a.output.parent.mkdir(parents=True,exist_ok=True);env=dict(os.environ,ARCH='x86_64',APPIMAGE_EXTRACT_AND_RUN='1')
subprocess.run([tool,'--no-appstream','--mksquashfs-opt','-processors','--mksquashfs-opt','2',app,a.output.resolve()],env=env,check=True)
print(a.output)
