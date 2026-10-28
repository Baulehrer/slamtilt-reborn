#!/usr/bin/env python3
"""Classify observed reads only after verifying complete original source objects."""
import argparse,hashlib,json,re,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--data',type=Path,default=ROOT/'build/amiga-read-verified-data');p.add_argument('--reads',type=Path,default=ROOT/'build/asset-read-audit');p.add_argument('--report',type=Path,default=ROOT/'analysis/traces/asset-read-coverage.json');a=p.parse_args();engine=(ROOT/'build/asset-read-audit/native.bin').read_bytes();lamp_map=(ROOT/'src/assets/amiga_lamp_offsets.inc').read_text();rows=[]
 def le(address,n=4):return int.from_bytes(engine[address-0x400000:address-0x400000+n],'little')
 def be(b,at,n=4):return int.from_bytes(b[at:at+n],'big')
 profile={
 'pirate':(0x465958,53,[(0x64484,'flpl1.raw'),(0x6b504,'flpr1.raw'),(0x72584,'flpxr1.raw')]),
 'space':(0x46664c,48,[(0x6fd15,'flpl2.raw'),(0x76d95,'flpr2.raw'),(0x7de15,'flpxl1.raw')]),
 'demon':(0x463b54,52,[(0x84bf6,'flpl1.raw'),(0x8bc76,'flpr1.raw')])}
 for table,(descriptor,count,flippers)in profile.items():
  dat=(a.data/table/(table.upper()+'.DAT')).read_bytes();raw=(ROOT/f'build/decoded/full/{table.capitalize()}.Raw').read_bytes();audit=json.loads((a.reads/(table+'.json')).read_text());objects=[]
  assert audit['source_sha256']==sha(dat),(table,'audit source identity')
  meta=le(descriptor+8);directory=le(meta+16);section=be(raw,0);source_dir=section+be(raw,section+16)
  offsets=[int(v.strip().replace('u',''),0)for v in re.search(table+r'_lamp_offsets\[\].*?\{(.*?)\}',lamp_map,re.S)[1].split(',')if v.strip()]
  for i in range(count):
   d=le(directory+i*4);target=offsets[i];width=le(d+4,2)*16;height=le(d+6,2);record=source_dir+be(raw,source_dir+(i+1)*4);sh=be(raw,record+6,2);size=width//8*height
   assert be(raw,record+4,2)*16==width and sh<=height
   original=raw[record+12:record+12+width//8*sh]+bytes(width//8*(height-sh));assert dat[target:target+size]==original,(table,'lamp',i)
   objects.append({'kind':'original_lamp_mask','index':i,'target':target,'size':size,'source':record+12,'sha256':sha(original)})
  sources={f.name.lower():f for f in (ROOT/'build/decoded/full/Flippers').iterdir()}
  for target,name in flippers:
   b=sources[name].read_bytes();width=be(b,6,2)*8;height=be(b,8,2);frames=be(b,14,2);pixels=bytearray()
   for frame in range(frames):
    for y in range(height):
     for x in range(width):pixels.append(sum(((b[16+frame*width*height+(y*8+plane)*(width//8)+x//8]>>(7-x%8))&1)<<plane for plane in range(8)))
   assert dat[target:target+len(pixels)]==pixels,(table,name)
   objects.append({'kind':'original_flipper_art','source':name,'target':target,'size':len(pixels),'sha256':sha(pixels)})
  if table=='pirate':
   original=json.loads((ROOT/'analysis/traces/amiga-fragments-v2.json').read_text())
   for frame in original['compressed_frames']:
    target=int(frame['target'],0);assert sha(dat[target:target+480])==frame['sha256'];objects.append({'kind':'original_pirate_scene','target':target,'size':480,'sha256':frame['sha256']})
  known={};unknown=[]
  for r in audit['ranges']:
   for offset in range(r['offset'],r['offset']+r['size']):
    obj=next((o for o in objects if o['target']<=offset<o['target']+o['size']),None)
    if obj:known[obj['kind']]=known.get(obj['kind'],0)+1
    else:unknown.append({'offset':offset,'reader_pc':r['first_pc'],'first_tick':r['first_tick']})
  rows.append({'table':table,'ticks':audit['ticks'],'trajectory_exact':audit['trajectory_exact'],'unique_source_bytes_read':audit['unique_read_bytes'],'source_sha256':sha(dat),'classified_difference_bytes':known,'unresolved_read_bytes':unknown,'verified_source_objects':objects})
 report={'status':'PASS'if all(not r['unresolved_read_bytes']for r in rows)else'UNRESOLVED_READS','scope':'Observed native RD before writes; complete original masks/flippers/scene objects independently checked. Not all game paths or SDL asset readers.','tables':rows};a.report.write_text(json.dumps(report,indent=2)+'\n')
 for r in rows:print(r['table'],r['classified_difference_bytes'],'unresolved',len(r['unresolved_read_bytes']))
 if report['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
