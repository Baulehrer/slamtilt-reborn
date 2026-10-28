#!/usr/bin/env python3
"""Derive a local collision-normal cache by executing the original demo routine.
Requires pefile and unicorn. No original code/assets are bundled in native source.
"""
import argparse,hashlib,json,struct,time
from pathlib import Path
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP
DEMO_SHA='31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00'
DAT_SHA='1169210c52fb4cb8785a0ef87e42bcabbc9d7b17bf9b9062f4642fb2cb69755f'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('exe',type=Path);p.add_argument('dat',type=Path);p.add_argument('output',type=Path);p.add_argument('--layers',type=int,nargs='+',default=list(range(5)));p.add_argument("--extend-bottom",action="store_true",help="Fill rows608..615 in an existing cache without recomputing the interior");a=p.parse_args()
 exe=a.exe.read_bytes();dat=a.dat.read_bytes()
 if hashlib.sha256(exe).hexdigest()!=DEMO_SHA or hashlib.sha256(dat).hexdigest()!=DAT_SHA:raise ValueError('Unsupported original build/assets')
 pe=pefile.PE(data=exe);image=pe.get_memory_mapped_image();u=Uc(UC_ARCH_X86,UC_MODE_32)
 u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image)
 u.mem_map(0x1000000,0x400000);u.mem_write(0x1100000,dat)
 u.mem_map(0x2000000,0x10000);u.mem_map(0x2100000,0x1000)
 # Same normal function, explicit zero center offset; cache coordinates ARE sample center.
 u.mem_write(0x43e71c,struct.pack('<I',0));u.mem_write(0x43e410,struct.pack('<I',0))
 obj=bytearray(0x64);struct.pack_into('<I',obj,0x44,0x1100000+0x959f6)
 u.mem_write(0x1000000,bytes(obj));stack=0x200f000
 reports=[]
 # Layer-specific cache; exact same original evaluator.
 for layer,normal_offset,hit_offset in [(0,0x959f6,0x9ba36),(1,0xb98f6,0xbf9d6),(2,0xd1956,0xd4ce6),(3,0xde796,0xe2936),(4,0xd20d6,0xd5466)]:
  if layer not in a.layers:continue
  struct.pack_into("<I",obj,0x44,0x1100000+normal_offset);u.mem_write(0x1000000,bytes(obj))
  width,height=320,616;normals=[-1]*(width*height);count=0;start=time.monotonic()
  cache_path=a.output/("normals.bin" if layer==0 else f"normals-{layer}.bin")
  if a.extend_bottom:
   raw=cache_path.read_bytes()
   if raw[:12]!=b"SLMN"+struct.pack("<II",width,height) or len(raw)!=12+width*height*2:raise ValueError("Invalid existing normal cache")
   normals=list(struct.unpack("<"+"h"*(width*height),raw[12:]))
  for y in (range(height-8,height) if a.extend_bottom else range(8,height if layer==1 else height-8)):
   for x in range(8,width-8):
    if not dat[hit_offset+y*40+x//8] & (128>>(x&7)):continue
    u.mem_write(0x1000000,struct.pack('<ii',x<<16,y<<16));u.mem_write(stack,struct.pack('<I',0x2100000))
    u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_EAX,0x1000000)
    u.emu_start(0x40e1d0,0x2100000,count=10000)
    if u.reg_read(UC_X86_REG_ESP)!=stack+4:raise ValueError('Normal oracle did not return')
    v=u.reg_read(UC_X86_REG_EAX);v=v if v<0x80000000 else v-0x100000000
    if not -1<=v<=4095:raise ValueError(f'Invalid original angle {v}')
    normals[y*width+x]=v;count+=1
  a.output.mkdir(parents=True,exist_ok=True)
  (a.output/("normals.bin" if layer==0 else f"normals-{layer}.bin")).write_bytes(b"SLMN"+struct.pack("<II",width,height)+struct.pack("<"+"h"*len(normals),*normals))
  reports.append(dict(layer=layer,extend_bottom=a.extend_bottom or layer==1,evaluated_rows=[608,616] if a.extend_bottom else [8,616 if layer==1 else 608],normal_offset=hex(normal_offset),hit_offset=hex(hit_offset),calls=count,valid_normals=sum(v>=0 for v in normals),seconds=time.monotonic()-start,sha256=hashlib.sha256((a.output/("normals.bin" if layer==0 else f"normals-{layer}.bin")).read_bytes()).hexdigest()))
 # Original contiguous LUT backing sin and cos pointers, not recomputed trigonometry.
 lut=image[0x2a1f8:0x2a1f8+0x2800]
 a.output.mkdir(parents=True,exist_ok=True)
 (a.output/'lookup.bin').write_bytes(lut)
 previous_path=a.output/'manifest.json'
 if previous_path.exists():
  previous=json.loads(previous_path.read_text()).get('layers',[])
  reports=sorted([r for r in previous if r['layer'] not in a.layers]+reports,key=lambda r:r['layer'])
 meta=dict(method='Original demo0x40e1d0 executed with Unicorn, geometry layers0..4; per-layer offsets in manifest; no guessed normals',build_sha256=DEMO_SHA,dat_sha256=DAT_SHA,normal_routine='0x40e1d0',sin_va='0x42a1f8',cos_va='0x42a9f8',cache_coordinate='bitmap sample center, offsets excluded',layers=reports,unsupported_border=8,bottom_extension_layers=[r["layer"] for r in reports if r.get("extend_bottom")],normal_sha256=hashlib.sha256((a.output/'normals.bin').read_bytes()).hexdigest())
 (a.output/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta))
if __name__=='__main__':main()
