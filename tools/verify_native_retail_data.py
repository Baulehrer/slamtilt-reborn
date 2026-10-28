#!/usr/bin/env python3
"""Verify constructed native data against source layout; never needed to play."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--native',type=Path);p.add_argument('--image',type=Path,default=ROOT/'build/native-retail-data-image.bin');p.add_argument('--report',type=Path,default=ROOT/'analysis/traces/dat-only-retail-data.json');a=p.parse_args()
 if a.native:subprocess.run([str(a.native.resolve()),str(a.image.resolve())],check=True)
 spec=importlib.util.spec_from_file_location('reference',ROOT/'tools/slamimport_reference.py');reference=importlib.util.module_from_spec(spec);spec.loader.exec_module(reference)
 source=(ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE').read_bytes();assert sha(source)=='185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
 original=reference.mapped_image(source,0x100000);native=a.image.read_bytes();assert len(native)==0x100000
 ranges=[(0x454a00,0x466fec,'Complete shared engine/math and all four initialized table data islands')]
 mean=json.loads((ROOT/'analysis/mean-retail-readset.json').read_text())
 ranges += [(0x400000+begin,0x400000+begin+size,'Mean source range')for begin,_,size in mean['copies']]
 evidence=[]
 for lo,hi,description in ranges:
  expected=original[lo-0x400000:hi-0x400000];actual=native[lo-0x400000:hi-0x400000];assert expected==actual,(hex(lo),next(i for i,(x,y)in enumerate(zip(expected,actual))if x!=y))
  evidence.append(dict(begin=hex(lo),end=hex(hi),size=hi-lo,sha256=sha(actual),description=description))
 # Only explicit native logical dispatch IDs/data masks may occupy former code space.
 allowed=bytearray(0x54000)
 source_code=(ROOT/'src/assets/native_retail_data.cpp').read_text()
 for address,values in re.findall(r'parameters\(image,(0x[0-9a-f]+)u?,\{([^}]+)\}\)',source_code):
  lo=int(address,16)-0x400000
  if 0<=lo<len(allowed):allowed[lo:lo+len(values.split(','))*4]=bytes([1])*len(values.split(','))*4
 allowed[0x3fa4:0x3fd8]=bytes([1])*(0x3fd8-0x3fa4)
 assert all(not value or allowed[i]for i,value in enumerate(native[:0x54000]))
 observed=json.loads((ROOT/'analysis/dat-only-retail-readset.json').read_text());checks=[]
 for table in observed['tables']:
  for row in table['ranges']:
   lo=int(row['begin'],16)-0x400000;hi=int(row['end'],16)-0x400000;assert native[lo:hi]==original[lo:hi],(table['table'],row)
  checks.append(dict(table=table['table'],steps=table['steps'],initial_nonzero_read_bytes=table['nonzero_bytes'],all_exact=True))
 result=dict(status='VERIFIED_BOUNDED_NATIVE_DATA',source_exe_sha256=sha(source),native_image_sha256=sha(native),native_image_size=len(native),exact_ranges=evidence,observed_readsets=checks,header_instructions_IAT_omitted=True,original_assets_bundled=False,constructor='src/assets/native_retail_data.cpp',constructor_sha256=sha((ROOT/'src/assets/native_retail_data.cpp').read_bytes()),intentional_omissions=['PE headers/instructions/imports/relocations','Obsolete Windows CD/audio/installer/error/file-path metadata','Unused CRT/library initialized data except compiled seed-accessor logical ID and x87 ABI control word'],scope='Shared engine/math and all four initialized game-data islands exact; native captions/sample-control/lamps/descriptors/logical dispatch IDs, no PE or encoded image in source. Remaining fields retain neutral ABI offsets. Runtime all-path equivalence not inferred from this layout proof.')
 a.report.write_text(json.dumps(result,indent=2)+'\n');print('Native initialized game data/Mean6ranges/three observed readsets exact; original instructions omitted')
if __name__=='__main__':main()
