#!/usr/bin/env python3
"""Freeze bounded startup scalars; graphics/code are copied from user originals."""
import json,struct
from pathlib import Path
import pefile
from pirate_adventure_oracle import ROOT,digest

def main():
    game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    raw=(game/'SLAMTILT.EXE').read_bytes();pe=pefile.PE(data=raw);image=bytearray(0x100000)
    image[:pe.OPTIONAL_HEADER.SizeOfHeaders]=raw[:pe.OPTIONAL_HEADER.SizeOfHeaders]
    for s in pe.sections:
        if s.PointerToRawData:image[s.VirtualAddress:s.VirtualAddress+s.SizeOfRawData]=raw[s.PointerToRawData:s.PointerToRawData+s.SizeOfRawData]
    dat=(game/'DAT/PIRATE.DAT').read_bytes();main=(game/'DAT/MAIN.DAT').read_bytes()
    image[0xa0000:0xa0000+192000]=dat[0x14605c+1024:0x14605c+1024+192000]
    image[0xd0000:0xd0000+len(main)]=main
    prepared=ROOT/'build/oracle/pirate-full-tick'
    expected=(prepared/'human-image.bin').read_bytes();runtime=(prepared/'human-runtime.bin').read_bytes()
    words=[[i,struct.unpack_from('<I',expected,i)[0]]for i in range(0,len(expected),4)if expected[i:i+4]!=image[i:i+4]]
    assert all(0x52000<=a<0x70000 for a,v in words),'No code or asset patches permitted'
    r=bytearray(0x10000);r[0xc000:0xc000+2400]=struct.pack('<HH',320,0)*600
    rw=[[i,struct.unpack_from('<I',runtime,i)[0]]for i in range(0,len(runtime),4)if runtime[i:i+4]!=r[i:i+4]]
    for a,v in words:struct.pack_into('<I',image,a,v)
    for a,v in rw:struct.pack_into('<I',r,a,v)
    assert bytes(image)==expected and bytes(r)==runtime
    recipe=dict(format=1,table='The Pirate',build_sha256=digest(raw),input_sha256={'PIRATE.DAT':digest(dat),'MAIN.DAT':digest(main)},
        files_sha256={'PIRATE.DAT':digest(dat),'MAIN.DAT':digest(main),'pirate-prepared/human-image.bin':digest(expected),'pirate-prepared/human-runtime.bin':digest(runtime)},
        image_size=0x100000,canvas=[0xa0000,0x14605c+1024,192000],main_offset=0xd0000,image_words=words,runtime_words=rw,
        provenance='Bounded post-F1 canonical startup from pirate_full_tick_oracle.py, not recovered full loader. PE sections/code, MAIN data and table pixels copied from user originals. Scalar initialization only; no original code or assets embedded. Zero raw-pointer BSS; original damage buffer600rows at runtime+c000.')
    (ROOT/'analysis/import/pirate-retail-startup.json').write_text(json.dumps(recipe,indent=2)+'\n')
    print(len(words),'image scalars,',len(rw),'runtime scalars;4files byte-exact')
if __name__=='__main__':main()
