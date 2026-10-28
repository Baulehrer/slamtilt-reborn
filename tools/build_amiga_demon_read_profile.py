#!/usr/bin/env python3
"""Revision3 Demon fingerprint from ADF-only assets/native constructor; keepsV1/V2."""
import argparse,hashlib,json,struct,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--build',type=Path,default=ROOT/'build/native');a=p.parse_args()
 with tempfile.TemporaryDirectory(dir=ROOT/'build',prefix='demon-v3-')as tmp:
  tmp=Path(tmp);subprocess.run([a.build/'slamadf-data',ROOT/'amiga/historical-mods/DLM',tmp/'assets'],check=True);subprocess.run([a.build/'slamnative-data',tmp/'engine'],check=True)
  recipe=json.loads((ROOT/'analysis/import/demon-dat-startup.json').read_text());dat=(tmp/'assets/DEMON.DAT').read_bytes();main=(tmp/'assets/MAIN.DAT').read_bytes();image=bytearray((tmp/'engine').read_bytes());dest,start,size=recipe['canvas'];image[dest:dest+size]=dat[start:start+size];dest=recipe['main_offset'];image[dest:dest+len(main)]=main
  for off,value in recipe['image_words']:struct.pack_into('<I',image,off,value)
  runtime=bytearray(0x10000)
  for i in range(600):struct.pack_into('<I',runtime,0xc000+i*4,320)
  for off,value in recipe['runtime_words']:struct.pack_into('<I',runtime,off,value)
  files={'DEMON.DAT':dat,'MAIN.DAT':main,'demon-prepared/human-image.bin':image,'demon-prepared/human-runtime.bin':runtime};recipe['input_sha256']={'DEMON.DAT':sha(dat),'MAIN.DAT':sha(main)};summary=recipe['summary'];summary['dat_sha256']=sha(dat);summary['context_hashes'].update({'human-image.bin':sha(image),'human-runtime.bin':sha(runtime),'human-dat.bin':sha(dat)});files['demon-prepared/summary.json']=(json.dumps(summary,sort_keys=True,separators=(',',':'))+'\n').encode();recipe.update(asset_source='amiga',asset_revision=3,gameplay_profile='shared_native',files_sha256={n:sha(b)for n,b in files.items()})
  (ROOT/'analysis/import/demon-amiga-v3-startup.json').write_text(json.dumps(recipe,indent=2)+'\n');(ROOT/'src/assets/amiga_demon_read_profile.h').write_text('#pragma once\nnamespace slam {\ninline constexpr const char* amiga_demon_v3_sha256="'+sha(dat)+'";\n}\n')
 print('Demon revision3 profile generated; older profiles unchanged')
if __name__=='__main__':main()
