#!/usr/bin/env python3
"""Inventory originals and extracted corpus; exact and block-alignment comparisons."""
import pathlib,hashlib,json,re,subprocess,collections,difflib,datetime,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
def describe(p):
 b=p.read_bytes(); s=re.findall(rb'[ -~]{6,}',b)
 r={'path':str(p.relative_to(ROOT)),'size':len(b),'sha256':hashlib.sha256(b).hexdigest(),'sha1':hashlib.sha1(b).hexdigest(),'platform': 'windows' if 'win95' in p.parts else 'amiga','type':subprocess.run(['file','-b',str(p)],capture_output=True,text=True).stdout.strip(),'strings':[x.decode('ascii') for x in s[:40]],'build_date':None,'compiler':None,'version':None,'provenance':'QUELLEN.md; containing archive path retained','compression':'container' if p.suffix.lower() in ['.lha','.lzh','.zip','.7z','.rar','.lzx','.dms'] else 'undetermined'}
 if b'PRO-PACK' in r['type'].encode(): r['compression']='PRO-PACK (RNC), method 1'
 if b'$VER:' in b:
  r['version']=b.split(b'$VER:',1)[1].split(b'\0',1)[0][:120].decode('latin1')
 if b'InstallShield v3.0' in b: r['role']='InstallShield 3 setup wrapper; not game executable'
 if b[:2]==b'MZ':
  try:
   import pefile
   pe=pefile.PE(data=b);r['build_date']=datetime.datetime.fromtimestamp(pe.FILE_HEADER.TimeDateStamp,datetime.timezone.utc).isoformat();r['sections']=[{'name':q.Name.rstrip(b'\0').decode(errors='replace'),'file_offset':q.PointerToRawData,'size':q.SizeOfRawData,'rva':q.VirtualAddress,'executable':bool(q.Characteristics&0x20000000)} for q in pe.sections];r['image_base']=pe.OPTIONAL_HEADER.ImageBase;r['linker_version']=f'{pe.OPTIONAL_HEADER.MajorLinkerVersion}.{pe.OPTIONAL_HEADER.MinorLinkerVersion}';r['imports']=[q.dll.decode(errors='replace') for q in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[])];r['compression']='normal PE sections; packing not excluded'
  except Exception: pass
 return r
originals=[p for d in ['amiga','win95','cd32'] for p in (ROOT/d).rglob('*') if p.is_file()]
extracted=[p for p in (ROOT/'build/corpus').rglob('*') if p.is_file() and 'test-adf' not in p.parts and p.suffix.lower() not in ['.iso','.img']]
records=[describe(p) for p in originals+extracted]
(ROOT/'analysis/corpus.json').write_text(json.dumps({'schema':1,'files':records},indent=2))
executables=[r for r in records if pathlib.Path(r['path']).name.lower() in ['game.exe','demo.exe','slamtilt.exe','main.bin'] or r['path'].lower().endswith('.slave')]
groups=collections.defaultdict(list)
for r in executables:groups[r['sha256']].append(r)
canonical=[v[0] for v in groups.values()]
pairs=[]
for i,a in enumerate(canonical):
 for c in canonical[i+1:]:
  family=lambda x:'amiga-core' if pathlib.Path(x['path']).name.lower() in ['game.exe','demo.exe'] else pathlib.Path(x['path']).name.lower()
  if family(a)!=family(c):continue
  ab=(ROOT/a['path']).read_bytes();cb=(ROOT/c['path']).read_bytes();n=min(len(ab),len(cb));runs=[];start=None
  for k in range(n):
   if ab[k]!=cb[k] and start is None:start=k
   if ab[k]==cb[k] and start is not None:runs.append([start,k]);start=None
  if start is not None:runs.append([start,n])
  blocks=lambda b:[b[j:j+32] for j in range(0,len(b),32)]
  matched=difflib.SequenceMatcher(None,blocks(ab),blocks(cb),autojunk=True).get_matching_blocks()
  pairs.append({'a':a['path'],'b':c['path'],'size_a':len(ab),'size_b':len(cb),'same_offset_equal_bytes':sum(x==y for x,y in zip(ab,cb)),'changed_runs':runs,'block_matches':[{'offset_a':m.a*32,'offset_b':m.b*32,'size':m.size*32,'classification':'identical' if m.a==m.b else 'shifted'} for m in matched if m.size>=2],'method':'32-byte aligned exact blocks, sequence matching with popular blocks ignored; unmatched is changed/added/removed candidate, not proven function boundary'})
(ROOT/'analysis/binary-diffs.json').write_text(json.dumps({'groups':[[r['path'] for r in v] for v in groups.values()],'comparisons':pairs},indent=2))
lines=['# Corpus','', 'Generated with `build/venv/bin/python tools/corpus_scan.py`. Full per-file metadata, SHA-1/SHA-256, selected strings, PE sections/imports and dates: `analysis/corpus.json`. Source attribution: `QUELLEN.md`. Dates inside media are not release proof. Unknown compiler/version values are intentional.','',f'{len(originals)} original files; {len(extracted)} extracted files. Archive payloads stay under ignored `build/corpus/`.','', '| Original file | Bytes | SHA-256 | Type |','|---|---:|---|---|']
for r in records[:len(originals)]:lines.append(f"| `{r['path']}` | {r['size']} | `{r['sha256']}` | {r['type'].replace('|','/')} |")
lines+=['','## Extraction limits','','IPF and LZX/DMS not decoded in this pass. Amiga Action #83 disk 1 is not readable by xdftool. `nts_slamtiltcd.lzh` returns 7z exit 2: files must not be trusted until independently decoded. EU MODE1/2352 BIN and ROM IMG were converted by taking bytes 16..2063 of each 2352-byte sector; ISO extraction succeeds. Audio tracks were not interpreted. 1999 STR Demon is a separate Resurrection product and must not be treated as original Slam Tilt revision.']
previous=(ROOT/'docs/corpus.md').read_text() if (ROOT/'docs/corpus.md').exists() else ''
if '## Immediate reference choices' in previous: lines+=['', '## Immediate reference choices'+previous.split('## Immediate reference choices',1)[1]]
(ROOT/'docs/corpus.md').write_text('\n'.join(lines)+'\n')
lines=['# Binary map','','Exact identities are SHA-256 confirmed. `analysis/binary-diffs.json` includes changed byte runs and displaced 32-byte block matches. This is structural block evidence, not semantic equivalence. Byte offsets are file offsets, not loaded addresses.','', '## Identical build groups','']
for v in groups.values():
 lines += [f"### {pathlib.Path(v[0]['path']).name}: {v[0]['size']} bytes, `{v[0]['sha256']}`",'']+[f"- `{r['path']}`" for r in v]+['']
lines+=['## Comparisons','','| A | B | Same-offset equal | Changed runs | Displaced matching bytes |','|---|---|---:|---:|---:|']
for p in pairs:lines.append(f"| `{p['a']}` | `{p['b']}` | {p['same_offset_equal_bytes']}/{min(p['size_a'],p['size_b'])} | {len(p['changed_runs'])} | {sum(m['size'] for m in p['block_matches'] if m['classification']=='shifted')} |")
previous=(ROOT/'docs/binary-map.md').read_text() if (ROOT/'docs/binary-map.md').exists() else ''
if '## Highest-value findings' in previous: lines+=['', '## Highest-value findings'+previous.split('## Highest-value findings',1)[1]]
(ROOT/'docs/binary-map.md').write_text('\n'.join(lines)+'\n')
print(len(records),'records',len(groups),'binary groups',len(pairs),'comparisons')
