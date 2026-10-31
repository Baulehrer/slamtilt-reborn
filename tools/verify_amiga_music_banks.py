#!/usr/bin/env python3
"""Compare Retail Windows music banks to the user's decoded Amiga source assets.

Verifies the native Amiga adapter output against source receipts and exact copy
ranges, then reconstructs all ten STIM modules independently and compares them.
It does not establish original Amiga playback rules, timing, or mixed audio.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from extract_mean_stim import extract

ROOT=Path(__file__).resolve().parents[1]
WINDOWS=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT'
TABLES={
 'mean':{'offsets':(0x5c2d2,0x61590),'sha':'1169210c52fb4cb8785a0ef87e42bcabbc9d7b17bf9b9062f4642fb2cb69755f'},
 'pirate':{'offsets':(0x51876,0x568e8),'sha':'6050b576678ec9b1878c203c057089b1c2499cdfd4a1ebdd7220f9d665fac7d6'},
 'space':{'offsets':(0x53642,0x5b8e0,0x5fef8),'sha':'18a308bdfa9fe141f57d4462a44dc4dd69cb32c35f9e6f83462fce770600115b'},
 'demon':{'offsets':(0x6ffb4,0x6b2bc,0x6e2ce),'sha':'0d78f5dbc069c5082cecce06f9620385288f615c03c83696483a43f272069c4d'},
}
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--amiga-root',type=Path,default=ROOT/'build/amiga-read-verified-data')
 p.add_argument('--decoded',type=Path,default=ROOT/'build/decoded/full')
 p.add_argument('--windows-dat',type=Path,default=WINDOWS)
 p.add_argument('--output',type=Path,default=ROOT/'build/music-audit/amiga-windows-banks.json')
 a=p.parse_args();receipt=json.loads((a.amiga_root/'amiga-import.json').read_text())
 assert receipt['asset_source']=='amiga' and receipt['gameplay_profile']=='shared_native'
 assert receipt['windows_files_required'] is False
 copy_map=(ROOT/'src/assets/amiga_copy_map.inc').read_text();tables=[]
 for table,config in TABLES.items():
  name=f'{table.upper()}.DAT';pc=(a.windows_dat/name).read_bytes();adapted=(a.amiga_root/table/name).read_bytes()
  local=json.loads((a.amiga_root/table/'data.json').read_text())
  assert sha(pc)==config['sha'] and local['asset_source']=='amiga'
  assert local['input_executable_provided'] is False and local['files'][name]==sha(adapted)
  sources={}
  for ext in ('Raw','Bin'):
   source=(a.decoded/f'{table.capitalize()}.{ext}').read_bytes()
   assert sha(source)==receipt['decoded_input_sha256'][f'{table}.{ext.lower()}']
   sources[ext]=source
  marker=bytearray(len(adapted));tag=f'static constexpr Copy {table}_copies[] = {{'
  assert copy_map.count(tag)==1
  block=copy_map.split(tag,1)[1].split('};',1)[0]
  copies=re.findall(r'\{(\d+)u,(\d+)u,(\d+)u,(true|false)\}',block)
  assert copies
  for dst,src,count,is_raw in copies:
   dst,src,count=map(int,(dst,src,count));source=sources['Raw' if is_raw=='true' else 'Bin']
   assert dst+count<=len(adapted) and src+count<=len(source)
   if adapted[dst:dst+count]==source[src:src+count]:marker[dst:dst+count]=b'\x01'*count
  rows=[]
  for bank,base in enumerate(config['offsets']):
   win,wm=extract(pc,bank,config['offsets']);amiga,am=extract(adapted,bank,config['offsets'])
   assert win==amiga and wm['orders']==am['orders'] and wm['patterns']==am['patterns']
   # Every stripped bank byte, sample directory byte and complete 31 sample
   # headers/PCM bytes must belong to an intact Amiga Raw/Bin copy range.
   ranges=[(base,am['module_end']),(0,31*4)]
   ranges.extend((x['dat_offset'],x['dat_offset']+8+x['pcm_bytes']) for x in am['samples'])
   for start,end in ranges:
    assert 0<=start<=end<=len(adapted) and 0 not in marker[start:end],(table,bank,hex(start),hex(end))
   used=bytearray(len(adapted))
   for start,end in ranges:used[start:end]=b'\x01'*(end-start)
   rows.append({'bank':bank,'offset':hex(base),'orders':am['orders'],'patterns':am['patterns'],
                'stim_sha256':sha(amiga),'stim_size':len(amiga),
                'amiga_source_backed_distinct_bytes':sum(used)})
  tables.append({'table':table,'windows_dat_sha256':sha(pc),'amiga_adapter_dat_sha256':sha(adapted),
                 'decoded_raw_sha256':sha(sources['Raw']),'decoded_bin_sha256':sha(sources['Bin']),
                 'banks':rows})
 report={'status':'VERIFIED_BOUNDED','asset_source':'amiga','asset_revision':receipt['asset_revision'],
         'windows_files_required_for_import':False,'copy_map_sha256':sha(copy_map.encode()),'tables':tables,
         'scope':'The ten reconstructed STIM modules, including original pattern bytes, order bytes and all 31 sample headers/PCM payloads, are byte-identical across this Windows Retail DAT set and this decoded Amiga asset set. Source copy-range equality verified; not a claim of original Amiga event sequencing, player timing or final audio mix.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
 print(sum(len(t['banks']) for t in tables),'Windows/Amiga source-backed music banks byte-identical')
if __name__=='__main__':main()
