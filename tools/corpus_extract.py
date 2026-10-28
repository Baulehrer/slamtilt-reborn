#!/usr/bin/env python3
"""Extract owned original archives into ignored build/corpus; never execute payloads.
Requires 7z and amitools xdftool. LZX/DMS/IPF need separate decoders.
"""
from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[1]
logs=[]
for platform in ['amiga','win95','cd32']:
 for p in sorted((root/platform).rglob('*')):
  if not p.is_file() or 'Heftscan' in p.name:continue
  ext=p.suffix.lower();dst=root/'build/corpus'/p.relative_to(root).parent/p.stem
  if ext not in ['.lha','.lzh','.zip','.rar','.7z','.iso','.adf']:continue
  dst.mkdir(parents=True,exist_ok=True)
  if ext=='.adf' and any(dst.iterdir()):
   logs.append({'source':str(p.relative_to(root)),'destination':str(dst.relative_to(root)),'exit_code':0,'status':'existing extraction preserved; not revalidated'})
   continue
  cmd=([str(root/'build/venv/bin/xdftool'),str(p),'unpack',str(dst)] if ext=='.adf' else ['7z','x','-y',f'-o{dst}',str(p)])
  r=subprocess.run(cmd,capture_output=True,text=True)
  logs.append({'source':str(p.relative_to(root)),'destination':str(dst.relative_to(root)),'exit_code':r.returncode,'stderr':r.stderr[-3000:]})
# Raw CD images carry 2352-byte MODE1 sectors. Preserve source; create derived 2048-byte image.
raw=list((root/'win95/germany-1996').glob('*.bin'))+list((root/'build/corpus/win95/_dokumente').rglob('*.img'))
for p in raw:
 dst=root/'build/corpus/win95'/('germany-1996' if p.suffix=='.bin' else 'rom-image');dst.mkdir(parents=True,exist_ok=True);out=dst/'track01.iso'
 with p.open('rb') as f,out.open('wb') as g:
  while sector:=f.read(2352):
   if len(sector)<2352:break
   g.write(sector[16:2064])
 r=subprocess.run(['7z','x','-y',f'-o{dst}/extracted',str(out)],capture_output=True,text=True)
 logs.append({'source':str(p.relative_to(root)),'destination':str(dst.relative_to(root)),'exit_code':r.returncode,'stderr':r.stderr[-3000:]})
(root/'analysis/extraction-log.json').write_text(json.dumps(logs,indent=2))
print(f'{len(logs)} extraction attempts; {sum(x["exit_code"]!=0 for x in logs)} failed or partial')
