#!/usr/bin/env python3
"""Generate revision2 Amiga/native ABI fingerprints from ADFs, never Windows assets."""
import argparse,hashlib,json,struct,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def words(b,entries):
 for o,v in entries:struct.pack_into('<I',b,o,v)
def main():
 p=argparse.ArgumentParser();p.add_argument('--adfs',type=Path,default=ROOT/'amiga/historical-mods/DLM');p.add_argument('--build',type=Path,default=ROOT/'build/native');a=p.parse_args()
 with tempfile.TemporaryDirectory(dir=ROOT/'build',prefix='amiga-profile-')as tmp:
  tmp=Path(tmp);subprocess.run([a.build/'slamadf-data',a.adfs,tmp/'assets'],check=True);subprocess.run([a.build/'slamnative-data',tmp/'native.bin'],check=True)
  engine=(tmp/'native.bin').read_bytes();files={p.name:p.read_bytes()for p in (tmp/'assets').iterdir()};hashes={n:sha(b)for n,b in files.items()}
  for table in ['pirate','space','demon']:
   recipe=json.loads((ROOT/f'analysis/import/{table}-dat-startup.json').read_text());image=bytearray(engine);n=table.upper()+'.DAT';dest,start,size=recipe['canvas'];image[dest:dest+size]=files[n][start:start+size];dest=recipe['main_offset'];image[dest:dest+len(files['MAIN.DAT'])]=files['MAIN.DAT'];words(image,recipe['image_words']);runtime=bytearray(0x10000)
   for i in range(600):struct.pack_into('<I',runtime,0xc000+i*4,320)
   words(runtime,recipe['runtime_words']);prefix=table+'-prepared/';out={n:files[n],'MAIN.DAT':files['MAIN.DAT'],prefix+'human-image.bin':image,prefix+'human-runtime.bin':runtime};recipe['input_sha256']={n:hashes[n],'MAIN.DAT':hashes['MAIN.DAT']}
   if 'summary'in recipe:
    summary=recipe['summary'];summary['dat_sha256']=hashes[n];summary['context_hashes'].update({'human-image.bin':sha(image),'human-runtime.bin':sha(runtime),'human-dat.bin':hashes[n]});out[prefix+'summary.json']=(json.dumps(summary,sort_keys=True,separators=(',',':'))+'\n').encode()
   recipe['files_sha256']={n:sha(b)for n,b in out.items()};recipe['asset_source']='amiga';recipe['asset_revision']=2;recipe['gameplay_profile']='shared_native';(ROOT/f'analysis/import/{table}-amiga-v2-startup.json').write_text(json.dumps(recipe,indent=2)+'\n')
   if table=='pirate':pirate_image=sha(image)
  r=json.loads((ROOT/'analysis/import/mean-retail-startup.json').read_text());image=bytearray(r['image_size'])
  for src,dst,n in r['data_copies']:image[dst:dst+n]=engine[src:src+n]
  for o,old,new in r['pointer_fixups']:assert struct.unpack_from('<I',image,o)[0]==old;struct.pack_into('<I',image,o,new)
  start,n=r['lookup'];lookup=image[start:start+n];mini=image+bytearray(0x100000-len(image));words(mini,r['minigame_image']);runtime=bytearray(0x10000);words(runtime,r['minigame_runtime']);runtime[0x6000:0x6000+len(lookup)]=lookup;globals_=bytearray(160);words(globals_,r['engine_globals']);flippers=bytearray(108);words(flippers,r['flipper_state'])
  out={'MEAN.DAT':files['MEAN.DAT'],'MAIN.DAT':files['MAIN.DAT'],'mean-prepared/pe-data.bin':image,'mean-prepared/engine-globals.bin':globals_,'mean-prepared/flipper-state.bin':flippers,'mean-prepared/lookup.bin':lookup,'mean-minigame-prepared/image.bin':mini,'mean-minigame-prepared/runtime.bin':runtime}
  (ROOT/'packaging/mean-amiga-v2-data.sha256').write_text(''.join(sha(b)+'  '+n+'\n'for n,b in out.items()))
  text='#pragma once\n#include <string_view>\nnamespace slam {\ninline constexpr const char* native_amiga_v2_pirate_image_sha256="'+pirate_image+'";\ninline std::string_view amiga_v2_table_sha256(std::string_view id){\n'
  for t in ['mean','pirate','space','demon']:text+=' if(id=="'+t+'")return "'+hashes[t.upper()+'.DAT']+'";\n'
  text+=' return {};\n}\n}\n';(ROOT/'src/assets/amiga_data_profiles_v2.h').write_text(text)
 print('Trusted Amiga profiles generated from ADFs only')
if __name__=='__main__':main()
